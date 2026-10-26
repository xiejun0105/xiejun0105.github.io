# 全站内容与资源维护规则

本规则适用于之后的论文、News、Blog、课程、项目、会议与样式更新。
核心原则：**一处维护、按用途存放、先归档后清理、检查通过再交付**。

## 文档职责与入口

- 根目录 `README.md`：GitHub 项目首页，只保留简洁的公开欢迎信息，不放维护说明。
- 本文件：面向维护者的操作手册，集中记录内容来源、存储、归档和校验规则。
- [AGENTS.md](../AGENTS.md)：编码助手的工作约定，要求修改前阅读本手册。
- [Blog 管理](../blog/README.md)：文章日期、置顶、标签与存档细节。
- [论文缩略图](../images/papers/README.md)：DOI 映射、命名与选图细节。

这是三语静态网站，HTML 直接服务于 GitHub Pages。构建、归档与部署是独立步骤。
本手册和 AGENTS 如提交到公开仓库，也可被外部读取，并非私密文件；
真正的内部笔记、原始资料与历史记录只能留在被忽略的本地目录中。

构建与检查需要 Python 3 和 Node.js；Blog 归档另需 BeautifulSoup，PDF 提图需 PyMuPDF。
检查工具只读运行，不自动下载或删除资源；JSON 报告存于被忽略的 `tmp/`。

## 1. 内容来源

以本节的源文件表为入口。不要同时维护多份相同数据。

| 内容 | 维护源文件 |
| --- | --- |
| 名片信息与头像 | `index.html`、`ja/index.html`、`zh/index.html` |
| 期刊论文 | `data/journal-publications.json` |
| 论文研究主题 | `data/research-topics.json` 定义主题；每篇论文的 `topics` 指定归属 |
| 论文缩略图 | `data/paper-thumbnails.json` |
| 项目 | `data/funding.json` |
| News | `data/news.json` |
| 课程与指导 | `data/teaching-course-{en,ja,zh}.html`、`data/teaching-supervision-{en,ja,zh}.html` |
| 其他成果 | `data/misc-{en,ja,zh}.html` |
| Blog 标题、日期、排序、标签 | `assets/blog-data.js` |
| Blog 正文、素材映射 | `blog/<slug>/index.html`、`data/blog-assets.json` |
| 会议记录 | `conference/index.html` 及三语对应页，目前直接维护 HTML |
| 全站样式与交互 | `assets/style.css`、`assets/site.js` |
| 访问统计 | `assets/analytics.js`；`tools/site_analytics.py` 负责统一接入 |

- `tools/build_site.py` 生成三语共享导航、页脚、论文列表、首页相关区块、项目与课程页面。
- 课程/指导/其他成果的 `data/*.html` 是人工维护的片段，不是可以删除的构建残留。
- Blog 正文直接保存在 `blog/<slug>/index.html`；构建脚本不把 Markdown 转成文章。
- Blog 列表在浏览器中由 `assets/blog-data.js` 生成；修改 HTML 正文不会自动改摘要或日期。
- 会议及其他未纳入生成器的正文仍直接维护对应 HTML；不要假定所有网页都由生成器生成。
- 修改数据后运行构建，检查生成的英文、日文、中文页面；不要只修一个生成结果。

## 2. 目录与命名

| 目录 | 放什么 | 不放什么 |
| --- | --- | --- |
| `assets/` | CSS、JS、Blog 列表数据 | 新课程图、候选导出、PDF |
| `images/papers/` | 已选用的共享论文图 | 未采用的候选裁图 |
| `images/news/` | 本地新闻缩略图、公司标志 | 远程原始页面 HTML |
| `images/teaching/` | 正式采用的课程插图 | 多轮设计候选 |
| `images/` 根目录 | 现有共享图片、头像与报告封面 | 新增的杂乱临时导出 |
| `blog/<slug>/assets/` | 仅该文使用的最终图片 | SVG/PNG/WebP 多份相同用途副本 |
| `data/` | 正式维护的数据和内容片段 | 检查报告、历史快照 |
| `tools/` | 可复用的构建、检查、归档和提图工具 | 私有语料和图片输出 |
| `docs/` | 全站维护文档 | 私有写作笔记 |

命名规则：
- 文章 URL 使用稳定的描述性 slug，不加发布日期或序号；更新不得改变既有链接。
- 论文图采用 `FirstAuthor_Year_content.ext`，同年文章靠内容关键词区分，DOI 映射保证准确对应。
- News 图建议 `YYYY-MM-DD-short-topic.ext`；机构 Logo 使用 `organization-logo.ext`。
- 课程图使用稳定课程名，如 `urban-planning.webp`，不要把 white、final、v8 作为公开命名惯例。
- 候选图和版本号只在本地保留。不要为了统一目录而搬动全部已发布图片或破坏外部链接。
- 已有根目录共享论文图可以继续使用，不重复复制到每篇 Blog。

## 3. 图片和来源

- 优先存本地，并在原有清单中记录来源；News 使用 `imageSource`，论文用 DOI 缩略图映射。
- `data/blog-assets.json` 记录每篇文章的封面及实际正文图片，必须与 HTML、列表封面一致。
- 同一张图被论文与 Blog 共用时，只保留一份公开资源，通过清单关联。
- 论文框架图、坐标轴、文字和颜色不能为了压缩随意裁掉或模糊；优先无损 WebP。
- 照片可选适当质量的 JPEG/WebP；是否缩小分辨率须按实际显示尺寸和清晰度判断。
- 体积超过 1 MB 的单张图作为人工复核提醒，不是自动失败或强制有损压缩。
- 优化前后检查图片尺寸、解码和画面；无损转换应比对像素。不要只看扩展名或文件大小。
- 本地保存不代表已取得使用许可；来源、署名和复用条件仍需人工确认。

## 4. 日期、排序与标签

- `publishedAt` 是列表显示与非置顶排序使用的发布日期，格式为 `YYYY-MM-DD`。
- 普通修订保留发布日期，实质更新填写 `updatedAt`；不要靠改日期来调整排序。
- 用户明确要求重新发布时才重设发布日期，并在本地存档中记录原因及原始日期。
- About My Research 本次按用户要求重新标为 **2026-10-24**，旧日期保存在本地历史中。
- `dateSource: site-prepared` 表示网站版本准备日期，不是已验证的 GitHub 部署时间。
- 置顶使用 `pinned` 与 `pinOrder`，与主题标签无关；不要为排序添加假的 topic。
- 展示分类用 `tag`，筛选归属用 `tags`。新增筛选项须同步英文、日文、中文 Blog 页按钮。
- Blog 正文保持约定的英文。普通专题按写作规范组织；研究总览可用愿景式文风，不强制引用。

## 5. 标准更新流程

1. 确认修改范围和真实来源，阅读维护入口及相关清单。
2. 实质改 Blog 前先保存当前版本，记录更新原因。
3. 改正确的源数据、片段或文章正文；挑选最终图片，不把整套候选导出放到公开目录。
4. 同步摘要、日期、标签和资产映射，更新所有受影响语言，不改无关页面内容。
5. 构建并检查，修复全部错误；逐项判断大文件等提醒是否合理。
6. 有浏览器环境时核对桌面/手机、深浅色、图片比例、导航与相关交互；没有环境要明确说明。
7. 保存新版 Blog 快照与编辑记录。确认正文、元数据、旧新图片可恢复后清理完成的独立草稿。
8. 复核 Git 差异。源码完成不等于部署完成，只有明确授权后才执行提交与推送。

日常执行：

```sh
python3 tools/build_site.py
python3 tools/check_site.py --report tmp/site-audit.json
python3 -m unittest discover -s tools -p 'test_*.py'
node --check assets/site.js
node --check assets/blog-data.js
node --check assets/analytics.js
node --check assets/publication-filter.js
git diff --check
```

Blog 前后归档示例：

```sh
python3 tools/archive-blog.py --slug about-me --event before-update --note '修订前保存'
# 修改、构建与检查后，再运行：
python3 tools/archive-blog.py --slug about-me --note '记录本次修改内容'
```

未变化的 Blog 默认跳过；明确需要检查点才加 `--force`。撤下前先用
`--event before-withdrawal` 归档，再移除列表项，否则工具无法按该 slug 找到文章。

## 6. 资源清理与恢复

`check_site.py` 仅检查，不自动删除。报告包含资源体积、SHA-256、引用来源和相同内容分组。
它扫描公开 HTML/CSS、JSON 数据和 Blog JS 元数据；“未引用”仍需检查手写工具、外部链接和运营用途。

清理规则：
- 检查所有语言、数据片段、共享映射和代码生成路径，确认资源不是当前或计划中的正式依赖。
- 替换图片先添加新图并更新源数据，构建后再归档旧图，避免中间状态的失效链接。
- 公开旧版文件若有明确的外部访问用途，应保留或设置替代方案，不因“未引用”直接移除。
- 普通退役资源使用下列工具，先复制、校验哈希、写清单，再移除公开副本。

```sh
# 默认只复制；--move 才会在存档校验成功后移出公开目录。
python3 tools/archive-site-assets.py images/unused-example.png \
  --note '已由新资源替代且确认无引用' --move
```

工具拒绝移动仍被识别为引用中的资源；请求包含多个文件时先验证整组参数。
存档位于 `・Site archive/YYYY-MM-DD/<原路径>`，`manifest.json` 记录原路径、体积、哈希和原因。
恢复时按清单将文件复制回原路径，核对哈希并重新运行检查。旧记录不覆盖，不重写 Git 历史。

## 7. 本地资料与公开边界

- `・My publications/`、`・Blog draft/`、`・Site archive/`、`tmp/` 必须保持在根 `.gitignore` 中。
- Blog 历史正文、图像快照与原始编辑稿留在 `・Blog draft/archive/<slug>/`。
- 全站其他退役资源留在 `・Site archive/`，不要为清理网站而删除用户的唯一副本。
- 原始 PDF、Gemini/AI 写作脚本的密钥、调试导出、词云审核语料和系统文件不上传。
- 新增本地专用目录时，同时检查 `.gitignore`、构建脚本的跳过列表和检查工具的私有目录列表。
- `.gitignore` 不会取消已跟踪文件。检查 Git 索引，必要时仅取消跟踪，保留磁盘上的本地文件。
- 本地忽略目录应另有独立备份；仓库和网站不能充当它们的唯一备份。

## 8. 检查边界与完成标准

检查工具可发现本地失效路径、公开页链接私有目录、Blog 日期或映射不一致、缺失标签按钮、
字节级重复媒体、待复核的大图与未引用候选。它不验证外部网站是否在线，也不执行浏览器布局测试。
不把检查报告或候选资源清单提交为新的公开内容，不宣称未执行的远程部署成功。

交付前明确：改了什么、检查结果、保留了哪些必要提醒、历史存在哪里、是否已经推送。

## 9. 访问统计维护

- 服务：GoatCounter 官方托管版；后台为 `https://junxie.goatcounter.com/`，需账户登录。
- 统计接口：`https://junxie.goatcounter.com/count`，这是公开接入标识，不是后台密码或 API 密钥。
- `assets/analytics.js` 是唯一配置入口；不要逐篇粘贴第三方脚本。
- 构建脚本自动向完整的正式 HTML 加入一个共享加载器；跳过数据片段与重定向页，防止重复计数。
- 只在 HTTPS 正式域名 `xiejun0105.github.io` 加载第三方代码；本地预览、其他域名不加载。
- 若未来使用自定义域名，需明确修改正式域名判断并补测试，不能未经检查放开所有来源。
- 只记录页面访问，不绑定自动点击事件；移除路径查询参数，`/index.html` 归并到 `/`。
- 来源仅提交来源站点的 origin，不传来源路径或查询参数；地区由服务端按 IP 估算。
- 尊重浏览器 Do Not Track 和 Global Privacy Control 信号；这会减少计数，属于预期行为。
- 第三方脚本被拦截或服务不可用时，页面内容和导航不依赖它，也不试图绕过用户的拦截器。
- 后台私有可见性、是否收集地区、逐次访问明细是否关闭，必须由账号持有人在 GoatCounter 设置中确认；网站代码无法代替后台设置。
- 排除自己的正式站访问可用官方的 `#toggle-goatcounter` 入口，确认后按提示操作；不同浏览器或设备需分别设置。
- 建议每月查看一次，按需季度导出；不要为简单统计额外搭建服务器或公开阅读计数。
- 代码和离线测试不证明后台已收到真实访问；部署后由持有人登录后台核对，不能伪造测试访问量。
- 只有正式网站部署完成后才会开始记录新访问，不能补回未统计的历史数据。

官方参考：[接入](https://www.goatcounter.com/help/start)、[JavaScript 设置](https://www.goatcounter.com/help/js)、[排除自己的访问](https://www.goatcounter.com/help/skip-dev)。

## 10. 默认主题

- 全站在打开页面时使用访问者设备当地时间：07:00 至 17:59 默认浅色，其余时间默认深色。
- 手动切换优先，并通过 `localStorage` 的 `theme` 字段保留，下次打开和跨页访问仍使用该选择。
- 不再使用操作系统深浅色偏好作为默认；存储被禁用时仍允许当前页面手动切换。
- 若需重新按时间选择，清除该站点存储中的 `theme`；不新增页面按钮或自动覆盖用户的手动选择。
- 实现在 `assets/site.js`，边界及手动切换测试见 `tools/test_theme.py`。

## 11. 论文主题筛选

- 主题字典位于 `data/research-topics.json`：`id` 是稳定英文 slug，`labels` 包含中英日名称。
- `primary: true` 仅表示在 Publications 默认展开；其他主题放在“更多主题”中，不代表首页精选。
- 标签收起时单行横向滚动，展开后全部标签在同一个 flex 区域自然换行；不得将附加主题另排为独立列表。展开按钮位于右侧，结果说明在下方。
- 每篇论文在 `data/journal-publications.json` 添加 `topics: ["climate-change", "disclosure"]`，DOI 仍是论文的唯一标识。
- 一篇论文可归属多个主题；界面按单选筛选。同一论文不会复制到多个列表，原有排序、年份、编号与缩略图不改变。
- 主题按 PDF 的摘要、研究对象及实际分析内容人工归类，不因引言提到某个词就贴标签。
- Human Capital 指教育、健康、能力等资本存量；Well-being 指情绪、职业压力与生活体验，不将所有员工研究自动归入前者。
- Climate Change 用于明确研究气候风险、政策、减缓或气候披露的论文；一般环境绩效论文不自动归入。
- 研究计划中的交通/城市新方向不作为已有论文标签；仅在正式内容确实对应时新增主题。
- 新增主题须有三语名称并至少关联一篇论文，不能用空标签或替换现有 ID 破坏已分享链接。
- 构建会统一生成三语筛选按钮、数量及论文归属属性，不手工改生成页面。
- 深链接为 `/publications/journal/?topic=climate-change`；语言切换保留主题，All 清除主题，前进/后退恢复筛选。
- 筛选只隐藏不匹配论文、空年份及相应年度链接；无 JavaScript 时保持全部论文可读。
- 论文筛选交互仅加载在三语 Journal 页面；首页名片显示五个精选主题的普通链接。
- `landing: true` 控制名片是否展示主题，`landingRow` 指定行；不要与 `primary` 混用。第一行为 Corporate Sustainability、Climate Change、Well-being，第二行为 Supply Chains、Human Capital。
- 名片默认复用三语 `labels`，较短的展示名称可通过 `landingLabels` 按语言覆盖，不改变主题 ID 或论文页名称。
- 名片标签由构建脚本生成在介绍段落下方，统一为两行；字号略小于正文（桌面 14px，窄屏 13px），窄屏不足时可横向滑动。语言切换与名片主体的组间距为 8px，保留介绍组合底部留白。
- 名片主题使用无边框、无底纹的文字链接，淡色 # 仅为视觉提示，悬停/聚焦变色并提供“查看相关论文”的三语提示。
- 介绍段落不保留尾部空白高度；如需三语名片高度稳定，将保留空间放在介绍与标签组合的底部，避免标签远离实际段落。
- 每次修改后运行构建、全站检查与单元测试；`check_site.py` 会核对三语按钮及 DOI/topic 归属。
- 交互位于 `assets/publication-filter.js`，渲染/校验位于 `tools/publication_topics.py`，测试见 `tools/test_publication_topics.py`。
