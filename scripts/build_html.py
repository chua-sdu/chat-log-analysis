"""
HTML 祝福网页构建脚本。

根据 stats.json（分析脚本输出）+ config.json（用户配置）+ 模板，生成完整 HTML。

config.json 示例：
{
    "title": "chuaaaaa × fengshanzzz 聊天记录可视化报告",
    "cover_subtitle": "两年 · 二十八万条消息 · 我们的故事",
    "self_name": "chuaaaaa",
    "peer_name": "fengshanzzz",
    "bgm": "bgm.mp3",
    "cake_title": "fengshanzzz，生日快乐",
    "birthday_message": "祝福语\\n用换行",
    "stories": [
        {"num": "01", "title": "初识", "images": ["story_01.png"], "text": "故事文字"},
        {"num": "05", "title": "手办与陪伴", "images": [], "text": "无图幕文字"}
    ],
    "stickers": ["sticker_01.png", "sticker_02.png"]
}

用法：
    python build_html.py --stats stats.json --config config.json --template ../templates/report_template.html --output report.html
"""
import json
import os
import argparse
import sys


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_story_sections(stories):
    """生成故事线 HTML section。"""
    sections = []
    for s in stories:
        num = s.get("num", "")
        title = s.get("title", "")
        text = s.get("text", "")
        images = s.get("images", [])

        # 图片区域
        if not images:
            # 无图幕
            img_html = '<div class="story-image-wrap" style="visibility:hidden;"></div>'
        elif len(images) == 1:
            img_html = f'<div class="story-image-wrap"><img src="{images[0]}" class="story-image" alt="{title}"></div>'
        else:
            imgs = "".join(
                f'<div class="story-image-wrap"><img src="{img}" class="story-image" alt="{title}"></div>'
                for img in images
            )
            img_html = f'<div class="story-grid">{imgs}</div>'

        section = f'''    <section class="story-section">
        <div class="story-container">
            {img_html}
            <div class="story-content">
                <div class="story-number">{num}</div>
                <h3 class="story-title">{title}</h3>
                <div class="story-divider"></div>
                <p class="story-text">{text}</p>
            </div>
        </div>
    </section>'''
        sections.append(section)
    return "\n\n".join(sections)


def build_chart_cards():
    """生成 7 个图表卡片的 HTML 占位（数据由 JS 注入）。"""
    charts = [
        ("messagePieChart", "双方消息量对比", "📌 判断：从消息总量可以看出双方的投入度差异。"),
        ("typeDoughnut", "内容构成分析", "📌 判断：消息类型分布反映了沟通方式的偏好。"),
        ("monthlyLine", "每月消息量走势", "📌 判断：月度走势的波峰波谷对应着关系的关键节点。"),
        ("hourlyLine", "24小时活跃分布", "📌 判断：活跃时段揭示了两人的作息默契度。"),
        ("sessionPie", "会话发起对比", "📌 判断：会话发起方反映了谁更主动开启对话。"),
        ("themeBar", "话题偏好分布", "📌 判断：话题构成展现了两人共同生活的重心。"),
        ("nicknameLine", "亲密称呼演变", "📌 判断：称呼的变化是关系升温的直接信号。"),
    ]
    cards = []
    for cid, title, judgment in charts:
        card = f'''    <div class="chart-card">
        <h3>{title}</h3>
        <div class="chart-wrap"><canvas id="{cid}"></canvas></div>
        <div class="judgment"><strong>{judgment}</strong></div>
    </div>'''
        cards.append(card)
    return "\n\n".join(cards)


def build_sticker_js(stickers):
    """生成表情贴纸撒花 JS。"""
    if not stickers:
        return ""
    sticker_list = json.dumps(stickers, ensure_ascii=False)
    return f'''
        // 随机撒表情贴纸
        const stickerList = {sticker_list};
        const posPool = [
            {{top: '6%', left: '125px'}}, {{top: '9%', right: '5%'}},
            {{top: '16%', left: '110px'}}, {{top: '22%', right: '9%'}},
            {{top: '38%', left: '100px'}}, {{top: '42%', right: '4%'}},
            {{bottom: '24%', left: '105px'}}, {{bottom: '18%', right: '5%'}},
            {{bottom: '8%', left: '120px'}}, {{bottom: '5%', right: '10%'}},
        ];
        document.querySelectorAll('.story-section').forEach((section, idx) => {{
            const count = (idx % 3 === 0) ? 3 : 2;
            const used = [];
            for (let j = 0; j < count; j++) {{
                let pi;
                do {{ pi = (idx * 3 + j * 5) % posPool.length; }}
                while (used.includes(pi) && used.length < posPool.length);
                used.push(pi);
                const s = document.createElement('img');
                s.src = stickerList[(idx * 3 + j) % stickerList.length];
                s.className = 'story-sticker';
                s.style.width = (84 + (idx * 7 + j * 13) % 40) + 'px';
                Object.assign(s.style, posPool[pi]);
                s.style.animationDelay = (idx * 0.25 + j * 0.6) + 's';
                section.appendChild(s);
            }}
        }});
'''


def main():
    parser = argparse.ArgumentParser(description="构建聊天记录 HTML 祝福网页")
    parser.add_argument("--stats", required=True, help="stats.json 路径")
    parser.add_argument("--config", required=True, help="config.json 路径")
    parser.add_argument("--template", default=os.path.join(os.path.dirname(__file__), "..", "templates", "report_template.html"),
                        help="HTML 模板路径")
    parser.add_argument("--output", default="report.html", help="输出 HTML 路径")
    args = parser.parse_args()

    stats = load_json(args.stats)
    config = load_json(args.config)

    with open(args.template, encoding="utf-8") as f:
        html = f.read()

    # 1. 替换标题
    html = html.replace("<!-- 标题占位：如 \"chuaaaaa × fengshanzzz 聊天记录可视化报告\" -->",
                        config.get("title", "聊天记录可视化报告"))
    html = html.replace("<!-- 封面标题 -->", config.get("title", ""))
    html = html.replace("<!-- 封面副标题，如 \"两年 · 二十八万条消息 · 我们的故事\" -->",
                        config.get("cover_subtitle", ""))
    html = html.replace('<!-- 蛋糕标题，如 "fengshanzzz，生日快乐" -->',
                        config.get("cake_title", ""))

    # 2. 替换 BGM 路径
    bgm = config.get("bgm", "bgm.mp3")
    html = html.replace('src="bgm.mp3"', f'src="{bgm}"')

    # 3. 注入数据
    stats["selfName"] = config.get("self_name", stats.get("meta", {}).get("self", "自己"))
    stats["peerName"] = config.get("peer_name", stats.get("meta", {}).get("peer", "对方"))
    stats["birthdayMessage"] = config.get("birthday_message", "")
    data_json = json.dumps(stats, ensure_ascii=False, indent=4)
    # 替换 REPORT_DATA 常量
    import re
    html = re.sub(
        r"const REPORT_DATA = \{.*?\n        \};",
        "const REPORT_DATA = " + data_json + ";",
        html, flags=re.DOTALL
    )
    html = html.replace(
        'const BIRTHDAY_MESSAGE = "祝福语内容，用\\\\n换行";',
        'const BIRTHDAY_MESSAGE = ' + json.dumps(config.get("birthday_message", ""), ensure_ascii=False) + ';'
    )

    # 4. 插入图表卡片
    chart_cards = build_chart_cards()
    html = html.replace(
        "<!-- 每个图表卡片结构：\n    <div class=\"chart-card\">",
        chart_cards + "\n\n    <!-- 每个图表卡片结构：\n    <div class=\"chart-card\">"
    )

    # 5. 插入故事线
    stories_html = build_story_sections(config.get("stories", []))
    html = html.replace(
        "<!-- 故事线占位：在此插入 <section class=\"story-section\"> 每一幕 -->",
        stories_html
    )

    # 6. 插入表情贴纸 JS
    stickers = config.get("stickers", [])
    if stickers:
        sticker_js = build_sticker_js(stickers)
        html = html.replace(
            "        // 故事线滚动淡入",
            sticker_js + "\n        // 故事线滚动淡入"
        )

    # 输出
    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML 已生成: {args.output}")
    print(f"  - 数据: {args.stats}")
    print(f"  - 故事幕数: {len(config.get('stories', []))}")
    print(f"  - 表情贴纸: {len(stickers)} 张")


if __name__ == "__main__":
    main()
