---

# mempalace/ — 核心包

为 MemPalace 提供支撑的 Python 包。所有模块，所有逻辑。

## 模块

| 模块                       | 它的作用                                                                             |
| ------------------------ | -------------------------------------------------------------------------------- |
| `cli.py`                 | CLI 入口点 —— 路由到 mine、search、init、compress、wake-up                                 |
| `config.py`              | 配置加载 —— `~/.mempalace/config.json`、环境变量、默认值                                      |
| `normalize.py`           | 将 5 种聊天格式（Claude Code JSONL、Claude.ai JSON、ChatGPT JSON、Slack JSON、纯文本）转换为标准转录格式 |
| `miner.py`               | 项目文件摄取 —— 扫描目录，按段落切分，存储到 ChromaDB                                                |
| `convo_miner.py`         | 对话摄取 —— 按交换对（Q+A）切分，从内容中检测房间                                                     |
| `searcher.py`            | 通过 ChromaDB 向量进行语义搜索 —— 按 wing/room 过滤，返回逐字内容 + 评分                               |
| `layers.py`              | 4 层记忆栈：L0（身份），L1（关键事实），L2（房间回忆），L3（深度搜索）                                         |
| `dialect.py`             | AAAK 压缩 —— 实体编码、情绪标记、30 倍无损比率                                                    |
| `knowledge_graph.py`     | 时序实体-关系图 —— SQLite、按时间过滤查询、事实失效                                                  |
| `palace_graph.py`        | 基于房间的导航图 —— BFS 遍历、跨 wing 的隧道检测                                                  |
| `mcp_server.py`          | MCP 服务器 —— 19 个工具、AAAK 自动教学、Palace 协议、代理日记                                       |
| `onboarding.py`          | 引导式首次运行设置 —— 询问人物/项目，生成 AAAK 引导 + wing 配置                                        |
| `entity_registry.py`     | 实体编码注册表 —— 将名称映射为 AAAK 编码，处理歧义名称                                                 |
| `entity_detector.py`     | 从文件内容中自动检测人物和项目                                                                  |
| `general_extractor.py`   | 将文本分类为 5 种记忆类型（决策、偏好、里程碑、问题、情绪）                                                  |
| `room_detector_local.py` | 使用 70+ 模式将文件夹映射为房间名称 —— 无 API                                                    |
| `spellcheck.py`          | 名称感知拼写检查 —— 不会“纠正”你的实体注册表中的专有名词                                                  |
| `split_mega_files.py`    | 将拼接的转录文件拆分为按会话划分的文件                                                              |

## 架构

```
用户 → CLI → miner/convo_miner → ChromaDB（宫殿）
                                     ↕
                              knowledge_graph（SQLite）
                                     ↕
用户 → MCP Server → searcher → 结果
                  → kg_query → 实体事实
                  → diary    → 代理日志
```

宫殿（ChromaDB）存储逐字内容。知识图谱（SQLite）存储结构化关系。MCP 服务器将两者暴露给任何 AI 工具。
