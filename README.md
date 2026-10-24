# Jun Xie - Personal Website

三语静态学术主页，HTML 直接服务于 GitHub Pages。构建、归档与部署是三个独立步骤。

## 维护入口

- [全站维护规则](docs/MAINTENANCE.md)：内容来源、目录、命名、更新、校验与清理流程。
- [Blog 管理](blog/README.md)：日期、置顶、标签和文章历史。
- [论文缩略图](images/papers/README.md)：DOI 映射与人工选图规则。
- [自动协作约定](AGENTS.md)：之后修改网站时默认遵循的检查要求。

## 修改哪个文件

| 内容 | 维护源文件 |
| --- | --- |
| 期刊论文 | `data/journal-publications.json` |
| 论文缩略图 | `data/paper-thumbnails.json` |
| 项目 | `data/funding.json` |
| News | `data/news.json` |
| 课程与指导 | `data/teaching-course-{en,ja,zh}.html`、`data/teaching-supervision-{en,ja,zh}.html` |
| 其他成果 | `data/misc-{en,ja,zh}.html` |
| Blog 标题、日期、排序、标签 | `assets/blog-data.js` |
| Blog 正文、素材映射 | `blog/<slug>/index.html`、`data/blog-assets.json` |
| 会议记录 | `conference/index.html` 及三语对应页，当前仍直接维护 HTML |
| 全站样式与交互 | `assets/style.css`、`assets/site.js` |

## 常用检查

从仓库根目录执行：

```sh
python3 tools/build_site.py
python3 tools/check_site.py --report tmp/site-audit.json
python3 -m unittest discover -s tools -p 'test_*.py'
node --check assets/site.js
node --check assets/blog-data.js
git diff --check
```

`check_site.py` 只读检查，不自动下载或删除任何文件。JSON 报告写入被忽略的 `tmp/`。
构建与检查需要 Python 3 和 Node.js；Blog 归档另外需要 BeautifulSoup，PDF 提图需要 PyMuPDF。

## 公开与本地

公开目录只放实际使用的网页和资源。保留旧版网址，不为目录整齐随意移动已发布文章。

- `assets/`：全站 CSS、JS 与 Blog 元数据。
- `images/`：共用图片；论文、News、课程图分别归入 `papers/`、`news/`、`teaching/`。
- `blog/<slug>/assets/`：仅该文章使用的图片。
- `・My publications/`：本地 PDF 资料库，不上传。
- `・Blog draft/`：本地草稿、历史正文、编辑记录与图片快照，不上传。
- `・Site archive/`：其他页面的退役资源及校验清单，不上传。

本地历史也需要独立备份。`.gitignore` 不是备份机制，也不会自动取消已跟踪文件。
