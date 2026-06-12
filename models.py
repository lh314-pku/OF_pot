import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime
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


class PotDB(Base):
    __tablename__ = "pots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator = Column(JSON, nullable=False)
    detail = Column(String, nullable=False)
    members = Column(JSON, nullable=False, default=list)
    
    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        default=now_plus_8
    )
    
    expire_time = Column(
        DateTime(timezone=True),
        nullable=False,
        default=auto_get_expire_time
    )

@dataclass
class Member:
    # importance: user_id > nickname
    user_id: int
    nickname: str
    
    def to_dict(self):
        return {"user_id": self.user_id, "nickname": self.nickname}

@dataclass
class CTX:
    msg: str
    group_id: int
    member: Member
    ws: WebSocket