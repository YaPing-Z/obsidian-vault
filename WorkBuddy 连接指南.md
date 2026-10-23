---
tags:
  - 说明
  - WorkBuddy
---

# WorkBuddy × Obsidian 连接指南

本库路径：`D:\PING OB\ObsidianVault`

## 三种连接方式，从轻到重

| 方式 | 要装什么 | Obsidian 必须开着吗 | 能做什么 |
| --- | --- | --- | --- |
| **一、直接读写文件** | 什么都不用 | 不用 | 建笔记、追加、搜索、批量整理 |
| **二、官方 CLI** | 设置里开一下开关 | 必须开着 | 上面全部 + 在 OB 里打开笔记、套模板、查任务、查标签 |
| **三、MCP 服务器** | 装一个 MCP 服务 | 看类型 | 让 WorkBuddy 拥有专门的 Obsidian 工具集 |

**建议：先只用方式一**，够用了再加方式二。不要一上来全配。

---

## 方式一：直接读写文件（已可用，零配置）

原理：Obsidian 的库就是一个普通文件夹，WorkBuddy 能直接读写本地文件，所以**天然连通**。Obsidian 会监听文件变化，写入后立刻出现在库里，不用刷新。

怎么用 —— 直接在对话里说：

- 「记一下：下周要约产品过一版方案」→ 在 `00 Inbox` 生成速记
- 「把这条加到今天的日记」→ 追加到 `40 Journal/2026-10-23.md`
- 「搜一下我记过的关于双链的内容」→ 全局搜索后汇总给你
- 「把 Inbox 里的速记整理成常青笔记」→ 归类、合并、移动到 `20 Notes`
- 「按项目模板建一个叫『重构登录模块』的笔记」→ 套 `30 Templates/项目模板.md` 新建

**注意**：你目前有两个库，`D:\PING OB\PING OB`（旧的）和 `D:\PING OB\ObsidianVault`（本库）。下指令时说清是哪个，否则 WorkBuddy 默认用本库。建议长期只留一个，把旧库内容迁进来。

---

## 方式二：官方 Obsidian CLI（推荐第二步）

需要 Obsidian 1.12 以上版本。启用步骤：

1. Obsidian 中打开 **设置 → 通用（General）**
2. 找到 **Command line interface（命令行界面）**，打开开关
3. 按弹窗提示完成注册（可能要管理员权限）
4. 重开一个终端，执行 `obsidian version`，能输出版本号就成了

Obsidian 安装在 `D:\Program Files\Obsidian\Obsidian.exe`。

### 速记相关的命令

```bash
# 追加一条到今天的日记
obsidian vault="ObsidianVault" daily:append content="- [ ] 买牛奶"

# 在收件箱新建一条速记
obsidian vault="ObsidianVault" create path="00 Inbox/新速记.md" content="# 新速记"

# 用模板建笔记
obsidian vault="ObsidianVault" create name="重构登录模块" template="项目模板"

# 搜索
obsidian vault="ObsidianVault" search query="双链"

# 打开某篇笔记（速记完立刻跳过去看）
obsidian vault="ObsidianVault" open file="新速记"

# 查看全库标签分布
obsidian vault="ObsidianVault" tags counts

# 列出所有未完成任务
obsidian vault="ObsidianVault" tasks all todo
```

`vault=` 必须是第一个参数。终端的当前目录如果在库里，可以省略。

### 一个已知的坑

Windows 下给 CLI 传**中文内容**时可能出现乱码（取决于终端编码）。如果遇到，中文速记就退回方式一（让 WorkBuddy 直接写文件），CLI 只用来做打开、搜索、建空笔记这类不含中文正文的操作。

---

## 方式三：MCP 服务器（进阶，可选）

配置在 `C:\Users\Yaping\.workbuddy\mcp.json`。两种类型：

**A. 文件系统型**（不需要 Obsidian 运行，推荐）

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp@2", "serve", "--vault", "notes=D:\\PING OB\\ObsidianVault"]
    }
  }
}
```

**B. REST API 型**（能操作打开的笔记、执行命令，但要装插件）

先在 Obsidian 装社区插件 **Local REST API**，启用后复制 API Key，然后：

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp-server@latest"],
      "env": {
        "OBSIDIAN_API_URL": "http://127.0.0.1:27123",
        "OBSIDIAN_API_KEY": "把插件里的 API Key 粘到这里"
      }
    }
  }
}
```

配置完要在本会话的自定义连接器入口点「信任」才会生效。

### 安全提醒

MCP 一旦启用，AI 就具备了**写入和删除**笔记的能力。三件事务必做：

1. 库要备份（git 或云盘同步），别指望回收站
2. 删除类操作别勾「始终允许」
3. 涉及敏感内容的库，单独建一个给 AI 用，不要指向主库

---

## 速记该落在哪

| 你想到的是 | 落点 |
| --- | --- |
| 一句话灵感、待办、链接 | `00 Inbox` 新建速记 |
| 今天发生的事、当天待办 | 追加到 `40 Journal` 当天笔记 |
| 对已有主题的补充 | 追加到那篇笔记，别新建 |
| 有明确产出的项目 / 会议 / 读书 | 用 `30 Templates` 里的模板新建 |

Inbox 的价值在于**定期清空**，不是永久仓库。每周整理一次，能提炼的进 `20 Notes`，没用的直接删。

首页 `Home.md` 已经嵌入了收件箱视图，打开就能看到所有待整理的速记。
