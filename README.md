# 元火约锅用Bot（功能函数部分）

基于 FastAPI + WebSocket + SQLAlchemy + SQLite 的群聊机器人服务，用于在群聊中创建、加入和管理"约锅"事件。

---

## 📦 功能概述

提供群聊命令式 Bot：

- `/help` 查看帮助
- `/detail [命令]` 查看命令详细说明
- `/newpot [内容] (@...)` 创建约锅，可 @ 多人自动加入
- `/join [id]` 加入约锅
- `/pots` 查看当前约锅列表
- `/delete [id]` 删除约锅
- `/remove [id] (@某人)` 离开约锅 / 移除成员
- `/edit [id] [新内容]` 修改锅的描述
- `/transfer [id] @某人` 转让发起人
- `/settime [id] start|expire [时间]` 修改开始/过期时间

通过 WebSocket 与 NapCat QQ 进行消息交互。

---

## ⚙️ 技术栈

- FastAPI（WebSocket 服务）
- Uvicorn（ASGI）
- SQLAlchemy 2.0（ORM，Mapped 类型）
- SQLite（数据库）
- uv（环境管理）

---

## 📁 项目结构

```
project/
├── main.py              WebSocket 入口
├── routes/              命令系统（Command）
│   ├── __init__.py      命令注册入口
│   ├── base.py          CommandRegistry / BaseCommand
│   ├── registry.py      命令调度
│   ├── help.py          /help
│   ├── detail.py        /detail
│   ├── newpot.py        /newpot
│   ├── join.py          /join
│   ├── pots.py          /pots
│   ├── delete.py        /delete
│   ├── remove.py        /remove
│   ├── edit.py          /edit
│   ├── transfer.py      /transfer
│   └── settime.py       /settime
├── models.py            ORM 模型 + 工具函数
├── db.py                数据库连接
├── sql.py               初始化建表
├── pots.db              SQLite 数据库
└── .venv/               虚拟环境
```

---

## 🚀 环境要求

- Python 3.12+
- uv

安装 uv：

```bash
pip install uv
```

---

## 🧪 初始化

创建虚拟环境：

```bash
uv venv
```

激活环境：

**Windows：**
```bash
.venv\Scripts\activate
```

**Linux/macOS：**
```bash
source .venv/bin/activate
```

安装依赖：

```bash
uv sync
# 或
uv pip install fastapi uvicorn sqlalchemy
```

---

## ▶️ 启动

```bash
uv run main.py
# 或
python main.py
```

服务地址：

```
http://0.0.0.0:3001/ws
```

---

## 🔌 NapCat 配置

WebSocket 上报地址：

```
ws://127.0.0.1:3001/ws
```

远程部署：

```
ws://<server-ip>:3001/ws
```

---

## 💬 命令

| 命令 | 格式 | 说明 | 权限 |
|------|------|------|------|
| `/help` | `/help` | 查看所有命令 | 所有人 |
| `/detail` | `/detail [命令]` | 查看命令详细说明 | 所有人 |
| `/newpot` | `/newpot [内容] (@...)` | 创建约锅，可 @ 多人自动加入 | 所有人 |
| `/join` | `/join [id]` | 加入约锅 | 所有人 |
| `/pots` | `/pots` | 查看未过期的锅列表 | 所有人 |
| `/delete` | `/delete [id]` | 删除约锅 | 所有人 |
| `/remove` | `/remove [id]` | 退出约锅 | 所有人 |
| `/remove` | `/remove [id] @某人` | 移除指定成员 | 发起人 |
| `/edit` | `/edit [id] [新内容]` | 修改锅的描述 | 发起人 |
| `/transfer` | `/transfer [id] @某人` | 转让发起人（被转让人须在锅中） | 发起人 |
| `/settime` | `/settime [id] start [时间]` | 修改开始时间 | 发起人 |
| `/settime` | `/settime [id] expire [时间]` | 修改过期时间 | 发起人 |

### `/settime` 时间格式（逐级解析）

| 示例 | 含义 |
|------|------|
| `18` | 今天 18:00 |
| `18:30` | 今天 18:30 |
| `12-31` | 12月31日，保留锅原有的时分 |
| `2025-12-31` | 指定日期，保留锅原有的时分 |
| `12-31 18:30` | 12月31日 18:30（年份取锅原有） |
| `12-31 18` | 12月31日 18:00（年份取锅原有） |
| `2025-12-31 18:30` | 完整日期时间 |

### 时间显示规则

`/pots` 中显示的时间会根据与当前时间的关系智能省略：

- 同一天 → `18:30`
- 同一年 → `06-15 14:00`
- 跨年 → `2025-01-01 00:00`

---

## 🧠 数据结构

Pot：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 自增主键 |
| `creator` | JSON | 发起人 `{"user_id": int, "nickname": str}` |
| `detail` | String | 锅的描述内容 |
| `members` | JSON | 成员列表 `[{"user_id": int, "nickname": str}, ...]` |
| `start_time` | DateTime | 开始时间（UTC+8），默认为创建时间 |
| `expire_time` | DateTime | 过期时间（UTC+8），默认当天或次日 23:59:59 |

---

## 🗄 数据库

SQLite：

```
pots.db
```

注意：不要提交数据库文件。

---

## 🧩 架构

```
NapCat QQ
    ↓ WebSocket 上报（JSON 事件）
FastAPI /ws
    ↓ 过滤群名 + 解析命令
Command Dispatcher
    ↓ 匹配 CommandRegistry
Command Handler
    ↓ SQLAlchemy ORM
SQLite (pots.db)
    ↓ 返回文本
NapCat QQ → 群聊消息
```

---

## ⚠️ 注意

- 必须开启 NapCat WebSocket 上报
- 端口 3001 需可访问
- SQLite 适合轻量使用
- 过期锅在所有操作中均视为"不存在"
- `/newpot` 中 @ 的用户以 QQ 号作为初始昵称，后续通过 `/join` 自动更新
- `/remove` 发起人离开时自动转让给下一位成员；锅空时自动删除
- `/transfer` 只能转让给已在锅中的成员
