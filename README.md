# Zotero Bilingual Reader

在 Zotero 中把英文论文生成 **左英文、右中文的原版式对照 PDF**。正文、图注、图内坐标轴和图例都可以翻译，结果自动添加回原文献附件。

**Windows 10/11 · Zotero 9 · 自己的 Codex 账户 · AGPL-3.0-only**

[下载 0.2.0 预览版](https://github.com/guanjunz432-ctrl/zotero-bilingual-reader/releases/tag/v0.2.0-beta.1) · [安装步骤](docs/installation.md) · [English](README.en.md) · [实际验证](docs/validation.md) · [更新记录](CHANGELOG.md)

## 看真实生成效果

下图是 Green 等（2017）论文**第 4 页的实际生成结果**，直接渲染自插件后端生成的 PDF，没有手工替换中文，也不是概念示意图。

![真实论文第4页：左侧英文原页，右侧中文原版式](docs/assets/paper-page-04.png)

**图也能做中英对照。**下面是同一输出中的图 2 放大：坐标轴、图例、图注变为中文，数值刻度和柱形保留。

![实际输出图2：中英文坐标轴、图例、图注](docs/assets/paper-figure-02.png)

[下载真实两页对照 PDF（原文第 1、4 页）](docs/assets/paper-bilingual-sample.pdf) · [原论文](https://doi.org/10.5194/nhess-17-1-2017) · [示例来源、许可与生成方式](docs/sample-provenance.md)

原文 © Green 等，2017，CC BY 3.0；修改为 AI 中文翻译及左右对照排版。原作者未为插件背书。示例不代表所有论文都能达到相同质量。

## 0.2.0 修复了什么

- 临时请求替代逐页持久聊天；原有历史聊天不会自动删除。
- 普通页使用轻量模型，复杂图页使用更强的视觉模型，两者均为低推理强度。
- 独立 Python 环境；缺少依赖时提示修复方法，避免只报“后台退出 1”。
- 完成页不重复翻译；内容未变时直接复用已排版 PDF。
- 普通单页错误先继续后续页，再补试一次；登录、额度或模型权限错误停止整篇。
- 斜排、极小图内标签尽量保留原图，在页底补充对照，减少覆盖图形。

## 使用什么模型，多久完成

| 内容 | 默认模型 | 推理强度 | 本次实测云端请求 |
| --- | --- | --- | --- |
| 普通正文、简单图表页 | `gpt-6-luna` | `low` | 19.72、20.11 秒/页 |
| 大幅图像、复杂矢量图或扫描页 | `gpt-6.1-sol` | `low` | 32.65 秒/页 |
| 本机解析与排版 | PyMuPDF 等确定性程序 | 不调用模型 | 本次 3 页排版 19.83 秒 |

**公开版实测 3 页总耗时 93.16 秒，约 1 分 33 秒**，包含页面准备、云端翻译和本机排版，不含首次安装、登录和 Zotero 导入。另一次本机 16 页测试的成功云端请求合计约 8 分 36 秒，**不是整篇端到端时间**。网络、账户、图文复杂程度及重试都会影响耗时。

分流依据页面图像面积和矢量路径数量，是启发式规则。本例图 2 由 Luna 完成，不是所有图都用强模型。模型权限因账户而异，可[修改模型设置](docs/installation.md#模型与速度设置)，不会自动回退到更昂贵模型。

降低推理、分流和缓存能减少不必要请求；不能把 token 数换算为固定的订阅额度百分比，也不保证节省比例。[完整测试口径](docs/validation.md)。

## 安装和使用

1. 准备 Windows 10/11、Zotero 9、Python 3.11+、Node.js 22+（含 npm）。
2. 从 Release 下载 **source.zip 和 XPI**，将源码解压到固定目录。
3. 在该目录运行 `setup.ps1`，再运行 `login.ps1`，使用自己的账户完成官方登录。
4. Zotero → 工具 → 插件 → 从文件安装 XPI。
5. 选中英文 PDF 或父文献 → 右键 → **Codex 中英对照** → 生成；页码留空为全文，也可先试 `1-2`。

升级请停止旧任务，解压新版源码、重新运行 setup 并安装新版 XPI。登录和已有页面缓存保留。[详细步骤与故障恢复](docs/installation.md)。

## 边界与隐私

图内文字依赖视觉识别，密集地图、小字、倾斜标签和公式需人工核对；不能承诺所有文字都能识别、翻译或原位放下。[已知限制](docs/limitations.md)。

本机不运行模型，不提供共享账号、转发服务器或遥测。所选页文字和图像发送至 OpenAI；本项目不读取、复制或发布登录凭据。译文及 PDF 缓存在本机，生成附件可能按你的 Zotero 设置同步。[数据流与隐私](PRIVACY.md)。

## 开发与许可

```powershell
.\.venv\Scripts\python.exe scripts/test.py
node tests/test_native_bridge.cjs
.\.venv\Scripts\python.exe scripts/privacy_check.py
.\.venv\Scripts\python.exe scripts/package_release.py
```

源代码 AGPL-3.0-only；论文示例另按 CC BY 3.0 标注。[第三方说明](THIRD_PARTY_NOTICES.md) · [贡献指南](CONTRIBUTING.md) · [安全反馈](SECURITY.md)。非 Zotero 或 OpenAI 官方插件。
