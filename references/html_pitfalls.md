# HTML 祝福网页生成 — 技术坑与经验

## 资源与路径

- **HTML 和所有资源必须同目录**：图片、音频用相对路径引用（`story_01.png`、`bgm.mp3`），交付时整个文件夹一起给用户。
- **中文文件名/路径**：PowerShell 下复制含中文和空格的路径必须加双引号；`copy /Y` 在 PowerShell 中不支持，要用 `Copy-Item -Force`。
- **图片命名规范**：`story_01.png`（单图）、`story_04a.png`/`story_04b.png`（多图）、`cover.jpg`、`ending.jpg`、`sticker_XX.png`、`bgm.mp3`。

## 图片处理

- **禁止裁切人脸**：故事线图片必须用 `object-fit: contain` 完整显示。全屏背景 `cover` 方案会裁切人脸，用户明确反对过。
- **拍立得效果用 img 的 padding 实现**：给 `<img>` 加 `background:#fff; padding: 10px 10px 40px 10px` 即可模拟白边+底部留白，不需要额外包 div。
- **多图幕用 flex 换行**：`display:flex; flex-wrap:wrap; gap:14px`，不要用 grid 强制铺满（会拉伸/裁切）。
- **QQ 聊天记录图片路径**：原始图片在 `nt_qq/nt_data/Pic/YYYY-MM/Thumb/`（缩略图）和 `Ori/`（原图），缩略图足够网页用，体积小加载快。

## 布局迭代经验

用户对故事线布局的偏好演进（按尝试顺序）：
1. ❌ 左右 50/50 分栏 → 文字少时留白太多
2. ❌ 上下居中 → 右半屏空
3. ❌ 全屏图片背景+文字叠加 → 图片被裁切、太乱
4. ❌ 中间时间轴+交替左右 → 内容被时间线分割，空间利用差
5. ✅ **左侧时间线 + 右侧左图右文水平排列 + 拍立得 + 表情贴纸** → 最终方案

关键原则：**时间线在最左（60px），内容全部在右侧，图片和文字水平排列，表情贴纸随机撒在空白处填充**。

## 互动效果

- **浏览器禁止自动播放音频**：BGM 必须用户手动点击一次才能播放，做成播放/暂停按钮即可，不要尝试自动播放。
- **点击图片放大用 FLIP 动画**：记录原位置 `getBoundingClientRect()` → 克隆图 fixed 定位在原位 → 改到目标位置加 `transition` → 返回时改回原位。动画曲线用 `cubic-bezier(0.34, 1.4, 0.64, 1)` 有弹性。
- **蛋糕元素用纯 CSS 画**：三层 div + 渐变 + `repeating-linear-gradient` 做奶油花边，火焰用 `radial-gradient` + `animation` 抖动，吹灭用 scale 变形动画。
- **撒花用 JS 动态创建 div**：100 个小色块，随机颜色/位置/延迟/时长，`position:fixed; top:-20px`，动画 `translateY(110vh) rotate(720deg)`。
- **打字机效果**：`insertBefore(document.createTextNode(char), cursor)` 逐字插入，换行符 `\n` 时延迟加长（350ms），普通字 65ms。
- **滚动淡入用 IntersectionObserver**：`threshold: 0.15`，进入视口加 `.visible` class，CSS `transition: opacity 0.8s, transform 0.8s`。
- **鼠标爱心**：`mousemove` 事件节流（90ms），创建 fixed 定位的 emoji div，CSS 动画上浮淡出，1.3s 后移除。

## JS 执行顺序坑

- **蛋糕 HTML 在 `<script>` 之后时**，`document.getElementById('birthdayCake')` 会返回 null。必须把蛋糕相关代码包在 `document.addEventListener('DOMContentLoaded', ...)` 里，或把 script 移到 body 末尾。
- **Chart.js 必须在 canvas 元素之后初始化**，script 放在 body 末尾最安全。
- **Edit HTML 时不要误删 `<script>` 标签**：替换 footer 等相邻内容时，old_string 如果包含 `<script>` 会把标签删掉，导致所有 JS 失效。替换后必须检查 `<script>` 是否还在。

## 字体

- **可爱中文字体用 Google Fonts 的 ZCOOL KuaiLe（站酷快乐体）**：`<link href="https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap">`，标题和幕号用，正文保持系统字体保证可读性。
- 需要联网加载字体；离线环境下字体回退到系统默认。

## 人称约束

- 用户可能要求全程不用人称代词（我/你/他/我们/对方），统一用双方名字/昵称。
- 数据报告的图表标签、判断结论、故事线文字都要检查，不能漏。
- 标题也要中性化，如"双方消息量对比"而非"你和ta的消息量"。

## 交付验证

- 生成后用浏览器打开 HTML，逐项检查：7个图表是否渲染、故事线图片是否加载、点击放大是否正常、蛋糕点击是否触发、音乐是否播放、表情贴纸是否显示。
- 特别检查：所有图片路径是否正确（相对路径）、是否有图片404。
- 告知用户：HTML 和资源文件夹必须一起移动，不能只发 HTML 文件。
