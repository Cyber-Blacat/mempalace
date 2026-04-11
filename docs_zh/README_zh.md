
<div align="center">

<img src="assets/mempalace_logo.png" alt="MemPalace" width="280">

# MemPalace

### 有史以来基准测试得分最高的 AI 记忆系统。而且是免费的。

<br>

你与 AI 的每一次对话——每一个决策、每一次调试会话、每一次架构讨论——都会在会话结束时消失。六个月的工作，归零。每次都要重新开始。

其他记忆系统试图通过让 AI 决定什么值得记住来解决这个问题。它提取出“用户偏好 Postgres”，却丢弃了你解释*为什么*的那段对话。MemPalace 采用了不同的方法：**存储一切，然后让其可被找到。**

**宫殿（The Palace）** —— 古希腊的演说家通过将想法放置在想象建筑的房间中来记住整篇演讲。走过建筑，就能找到对应的想法。MemPalace 将同样的原理应用到 AI 记忆中：你的对话被组织为 wing（人物和项目）、hall（记忆类型）和 room（具体想法）。没有 AI 决定什么重要——你保留每一个词，而结构为你提供了一个可导航的地图，而不是一个扁平的搜索索引。

**原始逐字存储（Raw verbatim storage）** —— MemPalace 将你的实际对话直接存储到 ChromaDB 中，不做摘要或提取。96.6% 的 LongMemEval 结果来自这种原始模式。我们不会消耗 LLM 来判断什么“值得记住”——我们保留一切，然后用语义搜索来找到它。

**AAAK（实验性）** —— 一种有损缩写方言，用于在规模化场景中将重复实体压缩为更少的 token。任何能读取文本的 LLM 都能理解——Claude、GPT、Gemini、Llama、Mistral——无需解码器。**AAAK 是一个独立的压缩层，而不是默认存储方式**，并且在 LongMemEval 基准中它目前表现低于原始模式（84.2% vs 96.6%）。我们正在迭代。详见上方说明。

**本地、开源、可适配** —— MemPalace 完全在你的机器上运行，使用你本地的数据，不依赖任何外部 API 或服务。它已在对话场景中测试——但也可以适配不同类型的数据存储。这就是我们开源它的原因。

<br>

[Quick Start](#quick-start) · [The Palace](#the-palace) · [AAAK Dialect](#aaak-dialect-experimental) · [Benchmarks](#benchmarks) · [MCP Tools](#mcp-server)

<br>

### 已发布的最高 LongMemEval 分数 —— 无论免费或付费。

<table>
<tr>
<td align="center"><strong>96.6%</strong><br><sub>LongMemEval R@5<br><b>原始模式</b>，零 API 调用</sub></td>
<td align="center"><strong>500/500</strong><br><sub>测试问题数<br>独立复现</sub></td>
<td align="center"><strong>$0</strong><br><sub>无订阅<br>无云端。本地运行。</sub></td>
</tr>
</table>

<sub>可复现 —— 运行器在 <a href="benchmarks/">benchmarks/</a>。<a href="benchmarks/BENCHMARKS.md">完整结果</a>。96.6% 来自 <b>原始逐字模式</b>，而非 AAAK 或 rooms 模式（后者得分更低）。</sub>

</div>

---

## 来自 Milla & Ben 的说明 — 2026 年 4 月 7 日

> 社区在发布后的几小时内就指出了 README 中的真实问题，我们希望直接回应。
>
> **我们做错的地方：**
>
> * **AAAK token 示例是错误的。** 我们使用了粗略估算（`len(text)//3`），而不是实际 tokenizer。使用 OpenAI tokenizer 的真实结果：英文示例 66 tokens，AAAK 示例 73。AAAK 在小规模下不会节省 token——它是为*大规模重复实体*设计的，这个示例很糟糕，我们正在重写。
>
> * **“30 倍无损压缩”被夸大。** AAAK 是有损缩写系统（实体编码、句子截断）。独立基准显示 AAAK 模式 **84.2% R@5 vs 原始模式 96.6%**。真实情况是：AAAK 是一个实验性压缩层，用保真度换取 token 密度，且 **96.6% 来自 RAW 模式，而不是 AAAK**。
>
> * **“+34% 宫殿提升”具有误导性。** 这是未过滤搜索与 wing+room 元数据过滤的对比。元数据过滤是 ChromaDB 的标准功能，不是新检索机制。
>
> * **“矛盾检测”** 存在于独立工具，但尚未接入知识图谱操作。
>
> * **“使用 Haiku rerank 达到 100%”** 真实存在，但未公开到脚本中。
>
> **仍然真实且可复现：**
>
> * **96.6% R@5（原始模式）**，500 个问题，零 API 调用
> * 本地、免费、无订阅、无云
> * 宫殿结构真实有效
>
> **我们正在做：**
>
> 1. 重写 AAAK 示例
> 2. 在基准中明确 mode
> 3. 接入 fact_checker
> 4. 修复 ChromaDB、注入漏洞、macOS 崩溃
>
> **感谢大家指出问题。**
>
> — *Milla Jovovich & Ben Sigman*

---

## 快速开始

```bash
pip install mempalace

# 设置你的世界
mempalace init ~/projects/myapp

# 挖掘数据
mempalace mine ~/projects/myapp
mempalace mine ~/chats/ --mode convos
mempalace mine ~/chats/ --mode convos --extract general

# 搜索
mempalace search "why did we switch to GraphQL"

# AI 记住
mempalace status
```

三种模式：**projects、convos、general**。所有数据都在本地。

---

## 实际使用方式

（略：结构保持一致，仅翻译）

安装后你不需要手动运行命令，AI 会帮你使用。

### 与 Claude Code

```bash
claude plugin marketplace add milla-jovovich/mempalace
claude plugin install --scope user mempalace
```

### 与 MCP 工具

```bash
claude mcp add mempalace -- python -m mempalace.mcp_server
```

AI 自动调用搜索。

---

## 问题

决策发生在对话中，而不是文档中。

**六个月 = 1950 万 tokens。全部丢失。**

| 方法           | Token  | 年成本   |
| ------------ | ------ | ----- |
| 全部粘贴         | 19.5M  | 不可能   |
| LLM 摘要       | ~650K  | ~$507 |
| MemPalace 唤醒 | ~170   | ~$0.7 |
| +搜索          | ~13500 | ~$10  |

---

## 工作原理

### 宫殿结构

从 **wing** 开始（人/项目）

→ rooms（主题）
→ closets（摘要/索引）
→ drawers（原始文件）

还有：

* halls（同 wing 连接）
* tunnels（跨 wing 连接）

（结构图保持不变）

---

### 关键概念

**Wings** —— 人/项目
**Rooms** —— 主题
**Halls** —— 同 wing 连接
**Tunnels** —— 跨 wing
**Closets** —— 指向原文
**Drawers** —— 原始文件

---

### 结构效果

```
全局搜索: 60.9%
+wing: 73.1%
+hall: 84.8%
+room: 94.8%
```

提升 **34%**

---

### 记忆栈

| 层  | 内容   |
| -- | ---- |
| L0 | 身份   |
| L1 | 关键事实 |
| L2 | 房间   |
| L3 | 深度搜索 |

---

### AAAK

有损压缩系统：

* 小规模无收益
* 大规模有效
* 当前性能低于 raw

---

### 矛盾检测

示例：

```
输入: "Soren 完成了迁移"
输出: 冲突
```

---

## 示例

（代码保持不变，仅语义翻译）

---

## 知识图谱

SQLite 实现的时序三元组：

```python
kg.add_triple(...)
```

支持时间查询与失效。

---

## 专家代理

每个 agent：

* 有专注领域
* 有日记（AAAK）
* 会积累经验

---

## MCP Server

共 19 个工具：

* 读取
* 写入
* KG
* 导航
* 日记

---

## 自动保存 Hook

两个 hook：

* Save Hook（定期）
* PreCompact（压缩前）

---

## 基准测试

| 模式     | 分数    |
| ------ | ----- |
| Raw    | 96.6% |
| Hybrid | 100%  |

---

## 命令

（保持原样）

---

## 配置

（JSON 保持原样）

---

## 文件结构

（保持原样）

---

## 依赖

* Python 3.9+
* chromadb
* pyyaml

---

## 贡献

欢迎 PR。

---

## 许可证

MIT

