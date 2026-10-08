# daily-news-mail

每天从 GDELT 获取近 24 小时的新闻标题和来源，用 DeepSeek API 生成中文趋势简报，再通过 AgentMail 发到 163 邮箱。

## 配置

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中配置：

- `DEEPSEEK_API_KEY`：DeepSeek API 密钥（必需）
- `AGENTMAIL_API_KEY`：AgentMail API 密钥（必需）

不要把密钥写进代码、提交记录或日志。工作流只通过 GitHub Actions Secrets 将密钥注入运行环境。默认使用 `deepseek-flash`；如需更换模型，可在工作流中设置 `DEEPSEEK_MODEL` 环境变量。

## 运行

- `workflow_dispatch`：在 Actions 页面手动运行。
- 定时运行：每天 `03:10 UTC`，即北京时间 `11:10`。

简报每条包括事实、背景、重要性、对普通人的影响和后续观察点，并附 GDELT 返回的新闻来源链接。当前最小版本把 GDELT 标题和元数据交给模型，因此简报会明确标注标题信息有限的部分，不代表已阅读全文或独立核实。
