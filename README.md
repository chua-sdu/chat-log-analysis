# chat-log-analysis

聊天记录分析与 HTML 祝福网页生成 Skill。把 QQ/微信聊天记录转化为有数据、有判断、有结论的分析报告，并可进一步生成带数据可视化、照片滚动故事线、音乐/蛋糕/彩蛋互动的 HTML 祝福网页（生日/纪念日/告白礼物）。

## 功能

- **聊天记录解析**：支持 QQChatExporter 导出的 JSONL/JSON/CSV 格式
- **数据分析**：消息量、类型构成、月度走势、24小时活跃、会话发起、回复速度、主题偏好、亲密称呼演变
- **Markdown 报告**：有数据、有判断、有结论的结构化报告
- **HTML 祝福网页**：
  - 7 个 Chart.js 交互式图表，每个附判断结论
  - 关系阶段时间轴 + 记录之最
  - 全屏滚动照片故事线（拍立得风格 + 时间轴 + 表情贴纸）
  - 生日蛋糕互动（点击吹蜡烛 → 撒花 → 打字机祝福）
  - 鼠标跟随爱心、点击图片放大、BGM 播放器
  - 滚动淡入动画

## 安装

将本文件夹复制到 WorkBuddy 用户级 skills 目录：

```
Windows: C:\Users\<用户名>\.workbuddy\skills\chat-log-analysis\
macOS/Linux: ~/.workbuddy/skills/chat-log-analysis/
```

重启 WorkBuddy 或新建对话即可使用。

## 使用

对 agent 说：

> "帮我分析这份QQ聊天记录，做一份HTML生日礼物网页"

agent 会自动匹配本 skill 并按流程执行：

1. 数据探查与清洗
2. 运行 `scripts/analyze.py` 生成 `stats.json`
3. 生成 Markdown 分析报告
4. 引导逐张发送照片 + 讲述故事
5. 配置互动元素（BGM、蛋糕祝福、表情贴纸）
6. 生成完整 HTML 网页

## 依赖

- Python 3.8+
- jieba（分词）：`pip install jieba`
- 联网（模板使用 Chart.js CDN 和 Google Fonts）

## 目录结构

```
chat-log-analysis/
├── SKILL.md                          # Skill 主文档（流程指引）
├── README.md                         # 本文件
├── references/
│   ├── pitfalls.md                   # 数据分析技术坑
│   └── html_pitfalls.md              # HTML 生成技术坑与布局经验
├── scripts/
│   ├── analyze.py                    # 聊天记录分析脚本（输出 stats.json）
│   └── build_html.py                 # HTML 构建脚本（数据+配置→完整HTML）
└── templates/
    └── report_template.html          # HTML 模板（含所有交互效果）
```

## 数据导出工具

- **QQ**：[QQChatExporter](https://github.com/shuakami/qq-chat-exporter)（导出 JSONL）
- **微信**：各类第三方导出工具

## 隐私说明

聊天记录在本地处理，HTML 网页本地交付，不上传任何服务器。agent 对话过程中数据会经过 AI 平台，敏感内容请自行评估。

## License

MIT
