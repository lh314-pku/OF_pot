from fastapi import FastAPI, WebSocket
import uvicorn
import json

from routes.registry import dispatch_command
import routes  # 触发注册

from models import CTX, Member, sync_member_nickname
from api import try_resolve_response

from sql import init_db

app = FastAPI()

TARGET_GROUP = "bot测试"
clients = set()

init_db()

async def send_group_msg(ws, group_id, message):
    payload = {
        "action": "send_group_msg",
        "params": {
            "group_id": group_id,
            "message": message
        }
    }
    await ws.send_text(json.dumps(payload))


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    try:
        while True:
            event = json.loads(await ws.receive_text())

            # API 响应 → 交给等待中的 call_api 处理
            if try_resolve_response(event):
                continue

            if event.get("post_type") != "message":
                continue

            if event.get("group_name") != TARGET_GROUP:
                continue

            msg = event["raw_message"].strip()

            nickname = (
                event["sender"].get("card")
                or event["sender"].get("nickname")
                or "未知"
            )
            user_id = event["sender"].get("user_id")
            
            member = Member(user_id=user_id, nickname=nickname)
            sync_member_nickname(user_id, nickname)  # lazy 同步昵称
            
            ctx = {
                "msg": msg,
                "group_id": event["group_id"],
                "member": member,
                "ws": ws
            }
            
            ctx = CTX(**ctx)

            # 提取 command
            cmd = msg.split()[0]

            result = await dispatch_command(cmd, ctx)

            if result:
                await send_group_msg(ws, ctx.group_id, result)

    finally:
        clients.discard(ws)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)