import datetime
from typing import Any
from sqlalchemy import Integer, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

UTC_Plus_8 = datetime.timezone(datetime.timedelta(hours=8))

from dataclasses import dataclass
from fastapi import WebSocket

def now_plus_8():
    return datetime.datetime.now(tz=UTC_Plus_8)

def auto_get_expire_time(now=None):
    if now is None:
        now = now_plus_8()

    if now.hour < 20:
        expire_time = now.replace(hour=23, minute=59, second=59, microsecond=0)
    else:
        expire_time = (now + datetime.timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=0
        )

    return expire_time


def format_time_smart(dt: datetime.datetime, now: datetime.datetime | None = None) -> str:
    """智能格式化时间：同天省略日期，同年省略年。"""
    if now is None:
        now = now_plus_8()

    if dt.year == now.year:
        if dt.month == now.month and dt.day == now.day:
            return dt.strftime("%H:%M")
        return dt.strftime("%m-%d %H:%M")
    return dt.strftime("%Y-%m-%d %H:%M")


class PotDB(Base):
    __tablename__ = "pots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creator: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    detail: Mapped[str] = mapped_column(String, nullable=False)
    members: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_plus_8,
    )

    expire_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=auto_get_expire_time,
    )

@dataclass
class Member:
    # importance: user_id > nickname
    user_id: int
    nickname: str
    
    def to_dict(self):
        return {"user_id": self.user_id, "nickname": self.nickname}

def sync_member_nickname(user_id: int, new_nickname: str) -> None:
    """Lazy 更新：用户发消息时，同步其在所有未过期锅中的昵称。"""
    from db import engine
    from sqlalchemy.orm import Session

    with Session(engine) as session:
        pots = (
            session.query(PotDB)
            .filter(PotDB.expire_time > now_plus_8())
            .all()
        )

        for pot in pots:
            dirty = False

            # 更新 creator
            if pot.creator.get("user_id") == user_id and pot.creator.get("nickname") != new_nickname:
                pot.creator = {**pot.creator, "nickname": new_nickname}
                dirty = True

            # 更新 members
            new_members = []
            for m in pot.members:
                if m.get("user_id") == user_id and m.get("nickname") != new_nickname:
                    new_members.append({**m, "nickname": new_nickname})
                    dirty = True
                else:
                    new_members.append(m)

            if dirty:
                pot.members = new_members
                session.add(pot)

        session.commit()


@dataclass
class CTX:
    msg: str
    group_id: int
    member: Member
    ws: WebSocket