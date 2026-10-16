# 真实论文示例的来源与生成记录

## 来源与许可

Green, D., et al. (2017). *City-scale accessibility of emergency responders operating during flood events*. Natural Hazards and Earth System Sciences, 17, 1–16. [DOI / 出版页面](https://doi.org/10.5194/nhess-17-1-2017)。

出版页面明确标注 © Author(s) 2017，Creative Commons Attribution 3.0。[许可全文](https://creativecommons.org/licenses/by/3.0/)。本示例修改为 AI 中文翻译、左右对照排版及对应区域裁切；原作者和出版方未为插件背书。原文引文、作者、来源和图注保留。图 2 描绘 Leicester City Council 开展的设计降雨情景，原图注中的来源说明保留。

只公开原文第 1、4 页的对照结果，没有公开整篇论文或地图底图页。源论文 SHA256：`a3d298713e944f645a2d357e16e70cb617f132e97a791a6b4cc96813976fd375`。

这些论文衍生示例适用 CC BY 3.0，区别于仓库源代码的 AGPL-3.0-only。

## 产物与复现

- `assets/paper-bilingual-sample.pdf`：公开版后端实际生成的原文第 1、4 页。
- `assets/paper-page-04.png`：上述 PDF 第 2 页的直接渲染。
- `assets/paper-figure-02.png`：同一 PDF 中图 2 及图注的对应区域放大裁切；未重绘图形或手工替换译文。
- `assets/benchmark.json`：去除本机路径、会话编号及账户信息的测量数据。

本次云端测试处理原文 1、4、7 页，公开结果选取 1、4 页。图内中文由模型生成，排版由本机程序执行。样例未经过学术审校，数字、单位和术语仍应核对。

完成安装与个人登录后，从出版方获得上述原版 PDF，运行：

```powershell
.\.venv\Scripts\python.exe backend/layout_reader.py paper.pdf --pages 1,4,7
.\.venv\Scripts\python.exe scripts/make_paper_demo.py --layout <本次输出的layout目录>
```

导出脚本验证源文件哈希、完成页和排版错误，然后从已生成 PDF 导出，不预置中文译文。云端重新生成可能有措辞、定位和耗时差异，不保证二进制相同。不要将包含个人路径和论文内容的缓存上传 GitHub。

旧 synthetic/cloud 示例保留作历史与回归检查，它们是自制材料，未用作本版宣传主图。
