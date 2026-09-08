# 技术坑与经验（实战踩坑记录）

## 数据获取

- **NTQQ 数据库解密是深坑，不要自己写解密器**。NTQQ 用 SQLCipher 4 加密，密钥在进程内存（`wrapper.node` 模块）中，且 `nt_sqlite3_key_v2` 函数会被多次调用（每次打开一个库），PowerShell hook 脚本容易抓到错误数据库的密钥。直接推荐现成工具：`QQChatExporter`（导出 JSONL，最省事）、NapNeko `qq_dump_db`（解密 db）。
- 密钥特征：16 字节 ASCII 字符串。但即便拿到密钥，KDF 参数（迭代次数、HMAC 算法、page size、reserve 区）各版本不同，暴力搜参数是时间黑洞。

## 数据探查

- **图片消息无独立 type**：QQChatExporter 把图片藏在 `type="text"` 的 `content.text` 里，以 `[图片:xxx]` 占位符表示；`elements` 里有 image 元素。分类必须按占位符前缀识别，不能只看 `type` 字段。
- 表情（贴纸）= `type_17`，通话记录 = `type_19`（`content.text` 含 `通话时长 H:MM:SS`），回复引用 = `type="reply"`（`content.text` 有 `[回复消息]` 前缀）。
- 撤回消息 `recalled=true`，系统消息 `type="system"`，两者都要排除。

## 分词与词云

- **词云/高频词必须用 `jieba.posseg` 词性过滤**，否则会被「收到/看看/不能/不想/回去/告诉」等口语功能词淹没，词云毫无语义。只保留实词词性 `n/nr/ns/nt/nz/vn/v/a/an/i/l/ng`，再加「无意义词黑名单」（否定词、趋向动词、情态词、时间指代词、语气词）。
- 「首次出现」要防误匹配：`《爱你》`是歌名、「比赛的对象」不是称呼、「别人的老婆」不是称呼，需人工剔除后再下结论。

## 依赖安装

- **jieba 安装会卡**：`pip install jieba` 打包 19MB 词典时 setuptools 极慢（可能卡十几分钟甚至永久）。解法：先找 pip 缓存里已构建好的 `jieba-*.whl`（`pip/cache/wheels/` 下），直接 `pip install <那个.whl>`；或安装时先单独装 jieba、其他包分开装。
- 大包（numpy/matplotlib/scipy）用 `--no-cache-dir` 可避免缓存清理报错；但 `--no-cache-dir` 会让 jieba 重新构建 wheel（慢），所以 jieba 单独用缓存 wheel 装。

## 可视化

- **wordcloud 的 `color_func` 必须返回 0-255 的 int RGB**（PIL 要求），不能返回 0-1 的 float，否则 `TypeError: 'float' object cannot be interpreted as an integer`。
- **matplotlib 没有 `font.fallback` 这个 rcParam**（3.11 会报 `KeyError`）。emoji 渲染：名字用纯文本替代 emoji 最省事；若必须用 emoji，注册 Segoe UI Emoji 字体到 `font.sans-serif` 列表。
- 中文字体：`plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']` + `plt.rcParams['axes.unicode_minus'] = False`。
- PPT 用 `python-pptx`，图用 `height` 约束（而非 width）并水平居中，避免不同宽高比的图排版不一致。

## 文件操作

- **`rm -f xxx/*.png && python viz.py` 这种「删旧图再跑」有风险**：若脚本中途失败，旧图已被删、新图没生成，目录就空了。正确顺序：先跑脚本确认成功，再清理旧文件；或先备份。
