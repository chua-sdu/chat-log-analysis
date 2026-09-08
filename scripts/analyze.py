"""
聊天记录通用分析脚本模板。

使用前按实际数据微调这几处：
1. EXPORT_DIR / CHUNKS_DIR：导出文件路径（JSONL 分块目录，或单文件）
2. SELF_UIN / PEER_UIN / SELF_NAME / PEER_NAME：双方身份
3. 消息字段名（本项目用 QQChatExporter 的字段：timestamp/sender.uin/type/content.text）

输出：
- stats.json：所有统计结果（供可视化/报告使用）
- word_freq.json：双方高频词频（供词云使用，已做词性过滤）

依赖：jieba, numpy（如需可视化再加 matplotlib/python-pptx）
"""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

# ============ 配置区 ============
EXPORT_DIR = r"你的导出目录"
CHUNKS_DIR = os.path.join(EXPORT_DIR, "chunks")  # JSONL 分块目录；单文件时直接指向文件
OUT_DIR = r"输出目录"

SELF_UIN = "自己的 QQ 号/uid"
PEER_UIN = "对方的 QQ 号/uid"
SELF_NAME = "自己"
PEER_NAME = "对方"

CN_OFFSET_MS = 8 * 3600 * 1000  # 北京时间偏移（毫秒）

# ============ 停用词 / 主题词典 ============
STOPWORDS = set("""
的 了 是 我 你 他 她 它 们 吗 呢 啊 吧 呀 哦 嗯 哈 啦 就 都 也 还 又 不 在 有 和 与 这 那 个 上 下 里 外 中 什么 怎么 为什么 这样 那样 这个 那个 一个 没有 不是 就是 但是 因为 所以 然后 如果 可以 应该 需要 觉得 知道 真的 非常 特别 比较 一点 一下 已经 现在 今天 明天 昨天 时候 东西 事情 大家 我们 你们 自己 别人 看看 告诉 一会 感觉 刚刚 干嘛 还有 可能 有点 不要 出来 没事 晚上 这么 那么
""".split())

INTERACTION_WORDS = set("""
哈哈 哈哈哈 哈哈哈哈 哈哈哈哈哈 嘿嘿 嘻嘻 呵呵 宝宝 晚安 早安 么么 亲亲 抱抱 想你 爱你 摸摸头 乖 宝贝 收到 没事 好 好的 嗯嗯 哦哦
""".split())

THEME_DICT = {
    "学习/工作": "作业 考试 上课 实验 报告 论文 项目 代码 面试 实习 工作 复习 老师 图书馆 舍友 宿舍".split(),
    "饮食": "吃 饭 外卖 奶茶 食堂 火锅 夜宵 好吃 饿 早餐 午饭 晚饭 咖啡".split(),
    "出行/地点": "出门 回家 去哪 地铁 打车 旅游 旅行 火车 飞机 学校 教室".split(),
    "健康/作息": "生病 医院 药 感冒 累 睡 熬夜 困 洗澡 休息 睡觉 失眠".split(),
    "娱乐": "游戏 电影 视频 追剧 音乐 歌 玩 综艺 动漫 直播 打球".split(),
    "情感/关系": "想你 爱你 喜欢 在一起 结婚 恋爱 甜 心动 告白".split(),
}

# ============ 消息分类 ============
def get_text(msg):
    c = msg.get("content", {})
    return c.get("text", "") if isinstance(c, dict) else ""

def classify(msg):
    """返回 (category, text)。图片/语音/视频/表情/通话等无文本内容，text 为空。"""
    t = msg.get("type", "")
    txt = get_text(msg)
    if t == "system":
        return "system", ""
    if t in ("audio", "video", "file", "type_17", "type_19", "forward"):
        return {"audio": "audio", "video": "video", "file": "file",
                "type_17": "sticker", "type_19": "call", "forward": "forward"}[t], ""
    if t == "reply":
        return "reply", txt.replace("[回复消息]", "").strip()
    if t == "text":
        for prefix, cat in [("[图片", "image"), ("[视频", "video"), ("[语音", "audio"), ("[文件", "file")]:
            if txt.startswith(prefix):
                return cat, ""
        return "text", txt
    return "other", ""

# ============ 数据加载 ============
def load_messages(chunks_dir):
    msgs = []
    if os.path.isfile(chunks_dir):
        files = [chunks_dir]
    else:
        files = [os.path.join(chunks_dir, f) for f in sorted(os.listdir(chunks_dir)) if f.endswith(".jsonl")]
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msgs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return msgs

def cn_time(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc) + timedelta(hours=8)

# ============ 文本分析（posseg 词性过滤，避免口语功能词）============
import jieba
import jieba.posseg as pseg
MEANINGFUL_POS = {"n", "nr", "ns", "nt", "nz", "vn", "v", "a", "an", "i", "l", "ng"}
MEANINGLESS_WORDS = set("""
不能 不用 不会 不想 不要 不是 没有 可以 应该 需要 知道 觉得 感觉 看到 准备 告诉 看看 收到 没事 干嘛 还有 可能 有点 是不是 当然 以后 现在 今天 明天 昨天 时候 东西 事情 什么 怎么 为什么 这样 那样 这个 那个 一个 一下 一起 还是 或者 而且 可是 不过 只是 一直 总是 已经 其实 真的 非常 特别 比较 一点 但是 因为 所以 然后 如果 就是 而已 回去 回来 出去 出来 进去 下来 上去 过来 过去 出门 不理 开心 快乐 怎么办 怎么样
""".split())

def tokenize(texts):
    wc = Counter()
    for t in texts:
        if not t:
            continue
        t = re.sub(r"https?://\S+", "", t)
        t = re.sub(r"\[[^\]]*\]", "", t)
        for w, flag in pseg.cut(t):
            w = w.strip().lower()
            if not w or len(w) < 2 or flag not in MEANINGFUL_POS:
                continue
            if w in STOPWORDS or w in MEANINGLESS_WORDS or w.isdigit():
                continue
            if re.fullmatch(r"[a-z]+", w):
                continue
            wc[w] += 1
    return wc

# ============ 主分析 ============
def main():
    msgs = load_messages(CHUNKS_DIR)
    valid = [m for m in msgs if m.get("type") != "system" and not m.get("recalled")]
    valid.sort(key=lambda m: m.get("timestamp", 0))

    total = len(valid)
    active_days = len({cn_time(m["timestamp"]).strftime("%Y-%m-%d") for m in valid})

    self_count = sum(1 for m in valid if m.get("sender", {}).get("uin") == SELF_UIN)
    peer_count = total - self_count

    type_counter = Counter(classify(m)[0] for m in valid)

    # 按月、按小时聚合
    monthly = defaultdict(lambda: {"self": 0, "peer": 0, "total": 0})
    hourly_self, hourly_peer = Counter(), Counter()
    for m in valid:
        dt = cn_time(m["timestamp"])
        ym = dt.strftime("%Y-%m")
        monthly[ym]["total"] += 1
        if m.get("sender", {}).get("uin") == SELF_UIN:
            monthly[ym]["self"] += 1
            hourly_self[dt.hour] += 1
        else:
            monthly[ym]["peer"] += 1
            hourly_peer[dt.hour] += 1

    # 会话切分（30 分钟）
    SESSION_GAP_MS = 30 * 60 * 1000
    sessions, cur = [], [valid[0]]
    for m in valid[1:]:
        if m["timestamp"] - cur[-1]["timestamp"] >= SESSION_GAP_MS:
            sessions.append(cur); cur = [m]
        else:
            cur.append(m)
    sessions.append(cur)
    initiator = Counter("self" if s[0].get("sender", {}).get("uin") == SELF_UIN else "peer" for s in sessions)

    # 回复速度（跨人首次回应，过滤连发/超长）
    speeds_self, speeds_peer = [], []
    prev_uin, prev_ts = None, None
    for m in valid:
        uin = m.get("sender", {}).get("uin")
        ts = m["timestamp"]
        if uin not in (SELF_UIN, PEER_UIN):
            continue
        if prev_uin is not None and uin != prev_uin:
            gap = ts - prev_ts
            if 60 * 1000 <= gap <= 12 * 3600 * 1000:
                (speeds_self if uin == SELF_UIN else speeds_peer).append(gap)
        prev_uin, prev_ts = uin, ts

    def median(lst):
        s = sorted(lst)
        n = len(s)
        return (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2) if n else None

    # 文本
    self_texts, peer_texts = [], []
    for m in valid:
        cat, txt = classify(m)
        if cat == "text" and txt:
            (self_texts if m.get("sender", {}).get("uin") == SELF_UIN else peer_texts).append(txt)
    self_words, peer_words = tokenize(self_texts), tokenize(peer_texts)

    result = {
        "meta": {
            "self": SELF_NAME, "peer": PEER_NAME, "total": total,
            "active_days": active_days, "self_count": self_count, "peer_count": peer_count,
        },
        "types": dict(type_counter),
        "monthly": [{"month": ym, **d} for ym, d in sorted(monthly.items())],
        "hourly": {
            "self": {str(h): hourly_self[h] for h in range(24)},
            "peer": {str(h): hourly_peer[h] for h in range(24)},
        },
        "sessions": {"count": len(sessions), "initiator_self": initiator.get("self", 0),
                      "initiator_peer": initiator.get("peer", 0)},
        "reply_speed": {"self_median_ms": median(speeds_self), "peer_median_ms": median(speeds_peer)},
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    def clean_freq(wc):
        c = {w: c for w, c in wc.items() if w not in INTERACTION_WORDS}
        return dict(sorted(c.items(), key=lambda x: -x[1])[:300])
    wf = {"self": clean_freq(self_words), "peer": clean_freq(peer_words)}
    with open(os.path.join(OUT_DIR, "word_freq.json"), "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

    print(f"有效消息 {total}，活跃 {active_days} 天")
    print(f"{SELF_NAME} {self_count} vs {PEER_NAME} {peer_count}")
    print(f"结果已保存到 {OUT_DIR}")

if __name__ == "__main__":
    main()
