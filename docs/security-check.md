# 发布前安全自检(v0.1.0,2026-10-26)

## 结论

三个 `scripts/fetch.py` 均满足:只用 Python 标准库;只发 HTTPS GET;只访问 `www.tandiu.cn` 与 `tandiuai.cn`;不执行 shell;不写文件;不含任何密钥。未发现需要修复的问题。

## 1. 规则核对(AST + 正则,逐文件)

| 文件 | import | 危险调用(subprocess/os.system/exec/eval/写文件/删文件) | open() | 显式 HTTP 方法 | 访问域名 | 疑似密钥 |
|---|---|---|---|---|---|---|
| tandiu-llm-cost/scripts/fetch.py | argparse, datetime, json, os, sys, urllib | 无 | 无 | 无(默认 GET) | tandiuai.cn, www.tandiu.cn | 无 |
| tandiu-cn-ai-procurement/scripts/fetch.py | argparse, json, sys, urllib | 无 | 无 | 无(默认 GET) | tandiuai.cn, www.tandiu.cn | 无 |
| tandiu-ai-funding/scripts/fetch.py | argparse, collections, json, sys, urllib | 无 | 无 | 无(默认 GET) | tandiuai.cn, www.tandiu.cn | 无 |

- `os` 只用于读环境变量 `TANDIU_API_KEY`(tandiu-llm-cost 的 Pro 命令)。key 只在请求头里发往 `https://www.tandiu.cn/api/v1/*`,Pro 请求**禁止跟随重定向**,不会把 key 转发到别的地址;不发往镜像。
- 所有 URL 为代码内常量拼接固定路径,用户参数只参与本地过滤;Pro 查询参数经 `urllib.parse.urlencode` 编码。
- 每个请求 10 秒超时;输出只到 stdout。
- 归因头 `User-Agent: TANDIU-Skill/<skill>/<version>`、`X-TANDIU-Client: skill`,不含任何用户或机器信息。

## 2. Bandit 1.9.4

```
python -m bandit -r skills
Total lines of code: 335
Issues: High 0, Medium 4, Low 0
```

4 个 Medium 均为 `B310 urllib.urlopen`(提醒可能打开 file:// 等自定义 scheme)。本仓库所有 URL 均为写死的 `https://` 常量,不接受外部传入 URL,判定为误报,不处理。

## 3. Snyk Agent Scan 0.6.9(snyk-agent-scan)

已安装,但运行需要 `SNYK_TOKEN`(Snyk 账号 API Token)。按规矩不代为注册账号:

```
To use Agent Scan, set the SNYK_TOKEN environment variable.
```

**待补**:用 Snyk 账号 token 在仓库根目录运行 `SNYK_TOKEN=... snyk-agent-scan scan skills/ --json`,结果追加到本文件。
注意不要无参数运行(默认会扫描本机全部 MCP 配置并上传描述)。

## 4. SKILL.md 文本

人工通读三个 SKILL.md / fields.md:无指示 Agent 执行与数据获取无关的操作、无隐藏指令、无外链脚本下载;只引用 TANDIU 自有页面与 GitHub 仓库。
