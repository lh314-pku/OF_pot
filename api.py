"""
OneBot11 WebSocket API 调用工具

通过 echo 字段匹配请求与响应，支持在命令处理中同步等待 API 结果。
"""

import asyncio
import json
import uuid

# 所有待处理的 API 响应，key 为 echo 值
_pending: dict[str, asyncio.Future] = {}


async def call_api(ws, action: str, params: dict, timeout: float = 10) -> dict | None:
    """通过 WebSocket 调用 OneBot API 并等待响应"""
    echo = str(uuid.uuid4())
    payload = {
        "action": action,
        "params": params,
        "echo": echo,
    }
    await ws.send_text(json.dumps(payload))

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    _pending[echo] = future

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        return None
    finally:
        _pending.pop(echo, None)


def try_resolve_response(data: dict) -> bool:
    """如果是待处理的 API 响应，解析并返回 True；否则返回 False"""
    echo = data.get("echo")
    if echo and echo in _pending:
        _pending[echo].set_result(data)
        return True
    return False


async def get_member_name(ws, group_id: int, user_id: int) -> str:
    """获取群成员显示名称（群名片 > QQ昵称 > QQ号）"""
    result = await call_api(ws, "get_group_member_info", {
        "group_id": group_id,
        "user_id": user_id,
    })
    if result and result.get("retcode") == 0:
        data = result.get("data", {})
        return data.get("card") or data.get("nickname") or str(user_id)
    return str(user_id)
