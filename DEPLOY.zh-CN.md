# Harness Continual Learning：修复 404 并发布

## 已核实的原因

本次检查时，`boringKey/Harness-Continual-Learning` 的 `main` 根目录只有 `README.md` 和 `.nojekyll`，没有网站入口或资源；GitHub API 返回 `has_pages: false`，Actions 记录数为 0。因此，项目网页尚未部署。截图是已有个人主页的未找到页面，不是本项目网页样式加载失败。

本包保留最终 v10 设计及原图、论文、数据与视频预留位，仅修正部署路径及发布方法。准备文件不等于已经上线。

- 项目仓库：https://github.com/boringKey/Harness-Continual-Learning
- 发布后的目标网址：https://boringkey.github.io/Harness-Continual-Learning/
- Pages 设置：https://github.com/boringKey/Harness-Continual-Learning/settings/pages
- Actions：https://github.com/boringKey/Harness-Continual-Learning/actions

**不要修改 `boringKey.github.io` 个人主页仓库，也不要设置自定义域名。**

## 方法 A：浏览器上传（不需要安装软件）

### 1. 上传源码

解压发布包，打开其中的 `Harness-Continual-Learning` 文件夹。访问：

https://github.com/boringKey/Harness-Continual-Learning/upload/main

把文件夹内部的文件和子文件夹拖入上传区；不要上传 ZIP，也不要把外层文件夹一起嵌套进去。待上传完成，选择提交到 `main` 并点击 **Commit changes**。

根目录应直接看见：

```text
index.html
static/
scripts/
README.md
.nojekyll
```

图片、PDF、CSS 和 JavaScript 在 `static/` 内，必须一起上传。`.nojekyll` 已存在于远程仓库，即使文件管理器隐藏了它也不要删除。当前包共约 5 MB，单个文件都小于 25 MiB。

### 2. 开启 Pages

进入该项目仓库的 **Settings → Pages → Build and deployment**，设置：

```text
Source: Deploy from a branch
Branch: main
Folder: /(root)
```

点击 **Save**。此项目不需要 npm、Jekyll 配置或自定义 GitHub Actions 工作流。不要选择 `/docs`，不要把个人主页仓库作为发布源。

### 3. 验证

进入 **Actions**，等 Pages 部署成功；再回到 **Settings → Pages → Visit site**。

先确认响应的确是 HCL 项目页，而不是只看到网站 URL。应看见论文标题、Minecraft 视频位置、原始 Figure 1 / Figure 2 和实验结果。

若仍看到 404，先检查上传的根目录和 Pages 设置，再检查 Actions。只有部署成功后仍显示旧内容时，才考虑强制刷新或缓存问题。

## 方法 B：在本地运行自动发布脚本

该脚本会上传完整网站，启用 `main / (root)`，并验证线上 HTML、CSS、JavaScript 和两张原图的响应状态及内容哈希。它不是只修改 README。

前提：Python 3.9+、GitHub CLI `gh`，以及对目标仓库有管理权限的 `boringKey` 账号。没有 `gh` 时使用方法 A，或从 https://cli.github.com/ 安装。

在解压后包含 `index.html` 的目录中执行：

```bash
gh auth login --hostname github.com --web
python3 scripts/publish_pages.py
```

脚本会显示目标仓库、准备创建或覆盖的文件，并要求输入 `PUBLISH`。默认等待上线验证最多 600 秒。

安全行为：仅写入 `boringKey/Harness-Continual-Learning`；不读取或修改个人主页仓库；不强制推送；不删除远程独有文件；重复运行保留已有 `config.js` 和录像；遇到既有自定义域名、不同发布源或远程并发修改时停止。它通过本机 `gh` 使用认证，不要求在聊天里提供 Token。

输出 `VERIFIED` 才代表已通过线上内容检查；输出“uploaded/configured but not yet verified”只代表上传和配置完成，不代表网站已可用。

## 后续修改视频

把视频放在 `static/videos/`，修改 `static/js/config.js` 中的 `src`、`title` 和 `caption`，例如：

```javascript
src: "static/videos/comparison-1.mp4"
```

路径相对于 `index.html`，不要以 `/` 开头。留空时显示预留位。重复运行发布脚本会保留远程已有配置；修改配置可在仓库直接编辑，或用 Git 单独提交。较大录像使用媒体托管地址。

## 本地检查和预览

```bash
python3 scripts/check_site.py
python3 -m http.server 8000
```

访问 `http://localhost:8000`；正式项目使用 `/Harness-Continual-Learning/` 路径，已进行子路径资源检查。

## 参考

GitHub 官方 404 排查：https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-404-errors-for-github-pages-sites

发布源设置：https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

Pages API：https://docs.github.com/en/rest/pages/pages
