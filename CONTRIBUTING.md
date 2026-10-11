# 参与 TechXueXi-Modern

这是基于 TechXueXi/TechXueXi 的非官方兼容版。请向本仓库反馈本适配版问题，不要把这些变更归因于上游维护者。原项目贡献说明另存于 [doc/CONTRIBUTING.upstream.md](doc/CONTRIBUTING.upstream.md)，仅作历史参考。

1. Fork 本仓库，从 `main` 建立自己的修改分支。
2. 做范围明确的修改，并为网站页面、响应解析和失败停止条件添加可重复的回归测试。
3. 运行 `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 与依赖检查。
4. 提交前运行 `.\.venv\Scripts\python.exe tools/audit_publish.py`，确认没有账号文件、Cookie、密钥、运行截图或本地环境进入版本控制。
5. 创建面向本仓库 `main` 分支的 Pull Request，说明改动、测试结果及未验证部分。

单元测试通过不等于网站运行成功。真实网站验证必须使用自己有权限的账号，并明确说明验证范围；不要提交账号数据或完整原始日志。

请保留许可证、原作者归属和修改声明；不要新增猜题、伪造积分、绕过验证码或削弱证书验证的逻辑。
