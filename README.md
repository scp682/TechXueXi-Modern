# TechXueXi-Modern

基于 [TechXueXi/TechXueXi](https://github.com/TechXueXi/TechXueXi) 的**非官方兼容更新版**，重点适配当前网站和 Windows 上的现代 Google Chrome。保留原项目思路，修复旧版登录、内容源、积分解析及运行流程。

本仓库不是原项目官方版本，也不代表学习强国平台。原始代码与资源归原作者及贡献者所有；沿用上游 LGPL-3.0 许可证。具体来源、修改范围和日期见 [NOTICE.md](NOTICE.md)，原始说明保存在 [doc/README.upstream.md](doc/README.upstream.md)。

## 这次更新解决了什么

- 最新 Chrome 二维码加载与登录 Cookie 的域名不匹配。
- 旧文章、视频接口失效或仍返回过时内容。
- 把网站的合并积分错误拆半、固定显示已经不存在的任务。
- 视频没有真正播放却一直倒计时，以及不递增的重试计数导致无限循环。
- 每日练习入口与选择器过时、主流程未调用每日练习。
- Python 3.8 在部分 Windows 网络环境中的 TLS/代理兼容问题。

现在文章、视频串行浏览；播放异常、验证要求或连续 3 次没有积分变化会停止对应环节。只有网站实际积分达到上限才报告完成。每日练习仅使用明确的官方提示，无法可靠确定答案时停止，不猜题、不绕过验证码。

## 已验证的范围

2026-10-11 本机 Windows、Chrome **154.0.8037.99** 与同主版本 ChromeDriver 的有限样本实测：

| 环节 | 官网返回结果 |
| --- | --- |
| 文章浏览 | 0/12 → 2/12 |
| 实际视频播放 | 0/12 → 3/12 |
| 每日练习 | 5/5 |
| 今日积分 | 1 → 11 |

另有 **20 项模拟回归测试**、依赖检查与 BAT 启动自检通过。真实计分与模拟测试是不同证据；以上结果不代表所有任务已经跑满，也不保证所有账号、网络环境或未来网站规则都适用。

此次重点验证 Windows。仓库保留部分上游 Linux、Docker、推送和历史功能代码，但不宣称已重新验证它们；官网未提供的每周、专项任务自动跳过。不会沿用旧 README 中固定“45 分/天”的承诺。

## Windows 首次使用

GitHub 发布的是源码，**不包含维护者本地的 Python、ChromeDriver、离线依赖包或账号资料**。新用户需要自己准备环境：

1. 安装 Google Chrome。
2. 安装 [Python 3.8.10 x64](https://www.python.org/downloads/release/python-3810/)。这是为了兼容遗留依赖；建议仅在隔离的本地环境使用，不替换其他项目的 Python。勾选 Add Python to PATH，或安装到常用 Python38 目录。
3. 从 [Chrome for Testing 官方下载页](https://googlechromelabs.github.io/chrome-for-testing/) 获取与自己 Chrome **主版本一致**的 Windows ChromeDriver。将解压后的 `chromedriver.exe` 放到 `SourcePackages/chrome/` 下；没有目录就自行创建。
4. 下载本仓库 ZIP 并完整解压，双击根目录的 **一键启动.bat**。首次运行会创建 `.venv` 并安装 `requirements-windows.txt`。
5. 使用自己的学习强国 APP 扫码登录。账号状态只保存到本地 `SourcePackages/user/`，该目录不会被 Git 跟踪。

启动自检不会登录：

```powershell
.\一键启动.bat --check
```

如自动安装失败，可在根目录使用 Python 3.8 创建环境并安装：

```powershell
py -3.8 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip "setuptools<81" wheel
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
```

Python 3.8 已是旧运行时。本适配版尚未完成迁移到受支持 Python/Selenium 版本；不要把兼容修复理解为依赖栈已全面现代化。Chrome 更新到新主版本后，通常也需要更新 ChromeDriver。

## 配置与更新

个人配置放在 `SourcePackages/user/settings.conf`，默认字段参考 `SourcePackages/config/default_template.conf`。不要把账号数据或机器人密钥填进受 Git 跟踪的默认模板。

如果通过 Git 克隆，先检查 `git status`。没有待处理修改时可运行：

```powershell
git pull --ff-only
```

有本地修改时先提交或备份，避免覆盖。ZIP 下载用户可下载新版本到另一个目录，确认后再迁移自己的本地用户数据。

原项目旧版“一键更新”脚本会把远程地址切回上游，因此未收入本兼容版。不要用它更新本仓库。

## 测试与诊断

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

诊断工具位于 `tools/`。`verify_update.py --live` 会实际浏览内容，`--quiz-run` 会提交每日练习；不要把它们当作完全只读的检查。详细记录见 [更新说明-2026-10-11.md](更新说明-2026-10-11.md)。

## 隐私与使用边界

账号 Cookie、个人配置、日志、数据库、二维码、截图、浏览器和本地环境均已从版本控制中排除。上传或反馈前仍需自行检查敏感信息，详见 [SECURITY.md](SECURITY.md)。

请遵守平台规则及适用要求，仅在自己有权限的账号与本地环境中使用。网站可能调整接口、验证或计分规则；遇到限制应停止并在官方页面处理。本项目不提供账号、不承诺积分、不绕过安全验证，也不替代真实学习。

## 致谢与许可证

感谢 [TechXueXi/TechXueXi](https://github.com/TechXueXi/TechXueXi) 及其贡献者提供的基础实现。

保留 [LICENSE](LICENSE) 中的 **GNU LGPL v3** 原文，配套 GNU GPL v3 原文见 [COPYING](COPYING)。本仓库新增与修改代码沿用原许可证，完整来源及修改声明见 [NOTICE.md](NOTICE.md)。本兼容版的问题请在本仓库提交，不要因这些修改打扰上游作者。
