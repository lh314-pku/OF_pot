import json
from pathlib import Path

from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

TARGET_GROUP = "暂时还没想好名字的水群"

clients = set()

DATA_FILE = Path("pots.json")


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


async def send_group_msg(
    group_id,
    message
):
    payload = {
        "action": "send_group_msg",
        "params": {
            "group_id": group_id,
            "message": message
        }
    }

    msg = json.dumps(payload)

    dead = []

    for ws in clients:
        try:
            await ws.send_text(msg)
        except:
            dead.append(ws)

    for ws in dead:
        clients.discard(ws)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    clients.add(ws)

    print("NapCat Connected")

    try:

        while True:
            # print("OK!!!!!!")

            event = json.loads(
                await ws.receive_text()
            )

            if event.get("post_type") != "message":
                continue

            if event.get("message_type") != "group":
                continue

            if event.get("group_name") != TARGET_GROUP:
                continue

            msg = event.get(
                "raw_message",
                ""
            ).strip()

            group_id = event["group_id"]

            nickname = (
                event["sender"].get("card")
                or event["sender"].get("nickname")
                or "未知用户"
            )

            # =====================
            # /help
            # =====================

            if msg == "/help":

                await send_group_msg(
                    group_id,
                    """
约锅Bot

/help : 显示帮助

/newpot [内容] : 创建锅

/join [id] : 加入锅

/pots : 查看锅

/delete [id] : 删除锅
""".strip()
                )

            # =====================
            # /newpot
            # =====================

            elif msg.startswith("/newpot"):

                detail = msg[
                    len("/newpot"):
                ].strip()

                if not detail:

                    await send_group_msg(
                        group_id,
                        "格式：/newpot 今晚学一吃饭"
                    )

                    continue

                data = load_data()

                pot_id = data["next_id"]

                data["next_id"] += 1

                data["pots"].append(
                    {
                        "id": pot_id,
                        "creator": nickname,
                        "detail": detail,
                        "members": [nickname]
                    }
                )

                save_data(data)

                await send_group_msg(
                    group_id,
                    (
                        f"🍲 创建成功\n"
                        f"ID: {pot_id}\n"
                        f"内容: {detail}\n"
                        f"发起人: {nickname}"
                    )
                )

            # =====================
            # /join
            # =====================

            elif msg.startswith("/join"):

                args = msg.split()

                if len(args) != 2:

                    await send_group_msg(
                        group_id,
                        "格式：/join 1"
                    )

                    continue

                try:
                    pot_id = int(args[1])
                except:

                    await send_group_msg(
                        group_id,
                        "ID必须是数字"
                    )

                    continue

                data = load_data()

                target = None

                for pot in data["pots"]:

                    if pot["id"] == pot_id:
                        target = pot
                        break

                if target is None:

                    await send_group_msg(
                        group_id,
                        "锅不存在"
                    )

                    continue

                if nickname not in target["members"]:

                    target["members"].append(
                        nickname
                    )

                    save_data(data)

                await send_group_msg(
                    group_id,
                    (
                        f"已加入锅 {pot_id}\n"
                        f"当前人数："
                        f"{len(target['members'])}"
                    )
                )

            # =====================
            # /pots
            # =====================

            elif msg == "/pots":

                data = load_data()

                if not data["pots"]:

                    await send_group_msg(
                        group_id,
                        "暂无锅"
                    )

                    continue

                lines = ["🍲 当前锅列表\n"]

                for pot in data["pots"]:

                    lines.append(
                        (
                            f"[{pot['id']}] "
                            f"{pot['detail']}\n"
                            f"发起人:{pot['creator']}\n"
                            f"人数:{len(pot['members'])}\n"
                            f"=============="
                        )
                    )

                await send_group_msg(
                    group_id,
                    "\n".join(lines)
                )
            
            elif msg.startswith("/delate"):
                args = msg.split()
                if len(args) != 2:
                    await send_group_msg(
                        group_id,
                        "格式：/delete 1"
                    )
                    continue
                try:
                    pot_id = int(args[1])
                except:
                    await send_group_msg(
                        group_id,
                        "ID必须是数字"
                    )
                    continue
                data = load_data()
                before_count = len(data["pots"])
                data["pots"] = [
                    pot for pot in data["pots"]
                    if pot["id"] != pot_id
                ]
                if len(data["pots"]) == before_count:
                    await send_group_msg(
                        group_id,
                        "锅不存在"
                    )
                    continue
                save_data(data)
                await send_group_msg(
                    group_id,
                    f"已删除锅 {pot_id}"
                )


    except Exception as e:

        print(e)

    finally:

        clients.discard(ws)


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3001
    )

#  Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 & 
# expert DISPLAY=:1
# sudo su
# LD_PRELOAD=./libnapcat_launcher.so qq --no-sandbox 

# http://10.129.244.97:6099/webui/web_login

# source venv/bin/activate
# cd pot
# python3 main.py