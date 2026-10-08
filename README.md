# daily-news-mail

GitHub Actions 定时启动后，先把简报要求和“搜索新闻”函数交给 DeepSeek。DeepSeek 根据要求提出不同主题的搜索查询；程序执行 Google News RSS 搜索并把结果回传给 DeepSeek，再由 DeepSeek 整理简报，最后通过 AgentMail 发到 163 邮箱。

## 配置

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中配置：

- `DEEPSEEK_API_KEY`：DeepSeek API 密钥（必需）
- `AGENTMAIL_API_KEY`：AgentMail API 密钥（必需）

不要把密钥写进代码、提交记录或日志。工作流只通过 GitHub Actions Secrets 将密钥注入运行环境。默认使用 `deepseek-flash`；如需更换模型，可在工作流中设置 `DEEPSEEK_MODEL` 环境变量。

## 运行

- `workflow_dispatch`：在 Actions 页面手动运行。
- 定时运行：每天 `03:10 UTC`，即北京时间 `11:10`。

DeepSeek API 的函数调用让模型可以请求外部搜索，但实际搜索由仓库中的程序执行。搜索结果包含新闻标题、来源、链接和 RSS 可提供的摘要；简报会标注信息有限的内容，不代表已阅读全文或独立核实。
