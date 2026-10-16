# 安装、阅读与故障恢复

## 1. 准备环境

- Windows 10/11，Zotero 9；原型实测版本为 9.0.6。
- 从 [Python 官网](https://www.python.org/downloads/windows/) 安装 Python 3.11 或以上，勾选加入 PATH。
- 从 [Node.js 官网](https://nodejs.org/) 安装 Node.js 22 或以上的 LTS 版本，保留 npm。
- 可使用 Codex 的个人账户和网络连接。模型在云端运行，不在本机安装模型权重。
- 字体：宋体 `simsun.ttc`、Arial、Segoe UI Symbol。若检测不到宋体，在 Windows 可选功能中安装简体中文补充字体。

## 2. 安装后端

在 GitHub Releases 下载 `zotero-bilingual-reader-…-source.zip`，先解压到固定目录。不要在压缩包预览中运行脚本，也不要之后随意移动目录。

在该目录打开 PowerShell：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

脚本在当前目录创建 `.venv` 和 `node_modules`，按锁定版本安装依赖，运行环境检测，并在 `dist` 构建 XPI。这里的执行策略参数仅作用于本次 PowerShell 进程。

执行以下命令登录；浏览器页面属于官方 Codex 登录流程：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\login.ps1
```

这是本应用独立的登录目录，可能需要再次登录，即使电脑上的 Codex 已经登录。不要将其他工具的登录文件复制进来，也不要向维护者提供验证码或认证资料。

## 3. 安装 Zotero 插件

1. Zotero → **工具 → 插件**。
2. 点击齿轮 → **从文件安装插件**。
3. 选择本目录 `dist` 中的 `.xpi`，按 Zotero 提示完成安装。
4. 右键文献时应出现 **Codex 中英对照**。如果安装了个人原型版，先禁用原型，避免两个相同菜单。

## 4. 翻译与阅读

1. 先确保原英文 PDF 可在 Zotero 正常打开，云端占位附件需先下载。
2. 选中一篇文献，或者明确选中要翻译的 PDF 附件。
3. 右键 → **Codex 中英对照 → 生成原版式中英对照（含图中文字）**。
4. 首次建议输入 `1-2`；`1,3-5` 表示指定页，留空表示全文。这里使用 PDF 物理页码。
5. 确认所选页面将发送云端后开始。通过右键菜单查看进度。
6. 结束后，新增附件位于同一篇文献下，名称含“中英对照 · 原版式”。左栏英文，右栏中文，可缩放阅读。
7. 在新增附件上右键 → **显示文件**，可定位 Zotero 实际保存位置。

上级条目有多个 PDF 时可能选择到不同附件，建议直接选中目标英文 PDF。生成的附件带有专用标签，避免重复翻译译文。

## 5. 中途失败或停止

- 使用“当前页完成后停止”，可保留已完成缓存。
- 普通单页格式错误先继续后续页，默认再补试一次；登录、额度或模型权限错误会停止整篇，避免无效请求。
- 未完成结果会标注“中文待补”，并作为未完成附件回存。
- 再次选择**同一个原 PDF 和相同页码**，即可读取缓存并补试。
- 每次导出会新增附件；确认新版可用后，可由你自行删除旧的未完成附件。
- 翻译期间保持 Zotero 打开。重启前先等待停止完成。
- 排版失败、长期 0 页或登录错误时，先处理字体、账户额度或网络问题，再重试。

## 6. 检测与数据位置

```powershell
.venv\Scripts\python.exe scripts\doctor.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\login.ps1 -Status
```

`doctor.py` 只输出依赖版本和检测布尔值，适合提交问题。登录状态输出只供你在本机查看。

默认本机数据目录为 `%LOCALAPPDATA%\ZoteroBilingualReader`：

| 目录/文件 | 用途 |
| --- | --- |
| `settings.json` | 本机程序路径，无凭据 |
| `codex-profile/` | 官方 CLI 管理的登录与会话数据，切勿分享 |
| `outputs/` | 页面图像、译文、排版缓存、PDF，含论文内容 |
| `jobs/` | 任务及回存状态，含本机路径和 Zotero 条目编号 |

这些目录在源码目录之外，不应提交 GitHub。项目不提供自动上传日志功能。

## 模型与速度设置

默认 `gpt-6-luna` 用于普通页，`gpt-6.1-sol` 用于复杂图像、矢量图或扫描页，两者均为 `low`。分流参考图像面积和矢量路径数量，并非精准识别每一种图。所有页仍提供图像，简单图内文字也会尝试翻译。

公开版固定官方 CLI 0.163.0；旧 0.148.0 在本次实测中不支持新模型名。升级必须重新运行 setup，不能只换 XPI。账户没有对应模型权限时会停止并保留缓存，不会悄悄更换更昂贵模型。

默认值位于 `backend/translation-settings.json`。如希望升级保留个人设置，在 `%LOCALAPPDATA%\ZoteroBilingualReader\settings.json` 保留原有路径字段，增加以下 `translation` 对象：

```json
"translation": {
  "model": "gpt-6-luna",
  "vision_model": "gpt-6.1-sol",
  "reasoning_effort": "low",
  "timeout_seconds": 240,
  "max_attempts": 2
}
```

`max_attempts: 2` 指首次请求加一次补试；超时支持 30–600 秒，最多尝试 3 次。网络和权限故障应先解决，不建议不断重试。模型须为自己账户可用且支持图像输入的 Codex 模型。

若提示依赖或独立环境缺失，从固定安装目录重新运行 `setup.ps1`，修复 `.venv`、CLI 和路径。登录过期运行 `login.ps1`。已有缓存不会因安装目录更新而删除；无需复制登录凭据。

## 7. 更新与卸载

更新：停止翻译，将新源码解压到固定的新目录，运行其 `setup.ps1`，再安装新版 XPI。配置会指向新目录。登录和缓存保留在本机数据目录；不兼容的缓存版本会重新翻译。首个测试版采用手动更新。

卸载：停止任务，在 Zotero 插件页面卸载，再执行 `login.ps1 -Logout` 退出本应用的独立登录。后端目录可自行删除。若不再需要缓存，可在资源管理器删除上述本机数据目录；已导入 Zotero 的 PDF 附件不会因此删除。
