# 元火约锅用Bot（功能函数部分）

基于 FastAPI + WebSocket + SQLAlchemy + SQLite 的群聊机器人服务，用于在群聊中创建、加入和管理“约锅”事件。

---

## 📦 功能概述

提供群聊命令式 Bot：

- /help 查看帮助
- /newpot [内容] 创建约锅
- /join [id] 加入约锅
- /pots 查看当前约锅列表
- /delete [id] 删除约锅

通过 WebSocket 与 NapCat QQ 进行消息交互。

---

## ⚙️ 技术栈

- FastAPI（WebSocket 服务）
- Uvicorn（ASGI）
- SQLAlchemy（ORM）
- SQLite（数据库）
- uv（环境管理）

---

## 📁 项目结构

project/  
├── main.py          WebSocket 入口  
├── routes/          命令系统（Command）  
├── models.py        ORM 模型  
├── db.py            数据库连接  
├── sql.py           初始化建表  
├── pots.db          SQLite 数据库  
└── .venv/           虚拟环境

---

## 🚀 环境要求

- Python 3.12+
- uv

安装 uv：

pip install uv

---

## 🧪 初始化

创建虚拟环境：

uv venv

激活环境：

Windows：
.venv\Scripts\activate

Linux/macOS：
source .venv/bin/activate

安装依赖：

uv sync
或
uv pip install fastapi uvicorn sqlalchemy

---

## ▶️ 启动

uv run main.py
或
python main.py

服务地址：

http://0.0.0.0:3001/ws

---

## 🔌 NapCat 配置

WebSocket 上报地址：

ws://127.0.0.1:3001/ws

远程部署：

ws://<server-ip>:3001/ws

---

## 💬 命令

/help        查看帮助
/newpot      创建锅
/join        加入锅
/pots        查看锅列表
/delete      删除锅

---

## 🧠 数据结构

Pot：

- id
- creator
- detail
- members
- start_time
- expire_time

---

## 🗄 数据库

SQLite：

pots.db

注意：不要提交数据库文件

---

## 🧩 架构

NapCat QQ
    ↓ WebSocket
FastAPI /ws
    ↓
Middleware
    ↓
Command Dispatcher
    ↓
Command Handler
    ↓
SQLite

---

## ⚠️ 注意

- 必须开启 NapCat WebSocket 上报
- 端口 3001 需可访问
- SQLite 适合轻量使用