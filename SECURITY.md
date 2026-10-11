# 隐私与安全

- Cookie 等同登录凭证。不要把 `SourcePackages/user/`、二维码、浏览器资料、`.env`、运行截图或原始日志上传到 GitHub。
- `.gitignore` 只是防止误加入的第一道防线。发布前应检查完整暂存文件列表；不要使用 `git add -f` 绕过忽略规则。
- 本仓库只发布源码与测试，不附带任何账号，也不会替用户绕过验证码或账号验证。
- 默认模板不应填写真实机器人 token、secret、密码或 Cookie。个人配置放在被忽略的 `SourcePackages/user/settings.conf`。
- 旧 Python 3.8 与 Selenium 3 用于兼容遗留程序，不代表推荐安全基线。请仅在本地隔离环境使用，不向公网开放遗留 Web 控制台。
- 提交问题时，只提供脱敏错误描述、系统版本、Chrome/ChromeDriver 版本和复现步骤。不要粘贴原始请求头、完整 Cookie 或含账号资料的日志。

若误上传凭证，请先撤销或重新登录使其失效，再清理 Git 历史。仅删除最新版本中的文件不能消除历史泄露。
