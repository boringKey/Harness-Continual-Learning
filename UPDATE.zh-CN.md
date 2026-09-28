# Pages 发布修复

保持 v10 的设计、文案、论文、原图、实验结果和视频位置不变。本次仅处理部署。

1. 全部站点绝对地址从旧的 `/HCL/` 修正为 `/Harness-Continual-Learning/`，包括 canonical、Open Graph、论文元数据、sitemap、robots 和网页源码地址。
2. `index.html` 直接位于发布包根目录，`.nojekyll` 和完整 `static/` 资源一起提供。
3. 新增 `scripts/publish_pages.py`，可在用户本机认证后上传完整文件、开启 Pages 并检查线上内容，未实际执行云端发布。
4. 改写 README 和部署说明，不再假定目标仓库已经开启 Pages。
5. 新增发布路径检查和本地 HTTP 资源检查。先前浏览器截图记录是 v10 设计测试，不是线上部署证明。

远程检查发现：目标仓库只有 README 与 .nojekyll，has_pages=false，Actions 总记录数为 0。本次准备完整修复包，不等于线上已修好。
