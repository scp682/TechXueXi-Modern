# 来源与修改声明

本项目 **TechXueXi-Modern** 基于 [TechXueXi/TechXueXi](https://github.com/TechXueXi/TechXueXi) 的本地 `TechXueXi-developing` 源码副本进行修改，基础代码标识版本为 `v20230521`。该副本来自源码压缩包，不含原始 Git 历史，因此不能可靠声明对应的上游 commit。

原始代码及资源的权利仍归 TechXueXi 项目原作者及各贡献者所有。感谢上游项目提供的源码、结构和学习流程。本仓库是独立的非官方衍生兼容更新，不是原作者、TechXueXi 组织或学习强国平台的官方发布，也不暗示任何授权背书或合作关系。

原始 LGPL-3.0 许可证原文保留在 [LICENSE](LICENSE)。GNU GPL v3 的配套条款原文见 [COPYING](COPYING)。新增和修改代码沿用本仓库原许可证，不改为 MIT 或其他不兼容许可证。原始 README 另存为 [doc/README.upstream.md](doc/README.upstream.md)，其中旧版本的分数、环境和维护说明不代表本仓库当前承诺。

## 2026-10-11 的修改

由本仓库维护者使用 AI 辅助完成兼容更新，主要修改包括：

- `SourcePackages/pdlearn/mydriver.py`：本机 Chrome、现代无头模式、二维码加载、CDP Cookie 恢复及 JSON 请求。
- `SourcePackages/pdlearn/get_links.py`：当前公开 JSON 内容源、排序、去重、响应检查和 Windows 系统网络兼容。
- `SourcePackages/pdlearn/score.py`：按网站实时任务定义解析积分，不拆分合并分数；兼容旧 Python TLS 失败。
- `SourcePackages/pdlearn/article_video.py`：真实视频播放检查、串行浏览、有界重试和资源清理。
- `SourcePackages/pdlearn/daily_practice.py`：新增当前每日练习页面的明确官方提示匹配。
- `SourcePackages/pdlearn/answer_question.py`、`pandalearning.py`：调用当前每日练习，并跳过官网已不提供的任务。
- `SourcePackages/pdlearn/threads.py`、`version.py`：锁释放、版本请求超时及取消无限等待。
- 启动 BAT、Windows 依赖约束、诊断工具和 20 项回归测试。

发布整理同样于 2026-10-11 完成：补充来源说明、安装与更新指南、隐私排除规则和安全检查。不上传维护者的账号数据、Cookie、浏览器、Python 安装包、虚拟环境、数据库及运行截图，不启用原项目的发布工作流。

完整的本地适配与验证记录见 [更新说明-2026-10-11.md](更新说明-2026-10-11.md)。涉及本兼容版的问题请在本仓库反馈，不要因为本仓库的变更打扰上游作者。
