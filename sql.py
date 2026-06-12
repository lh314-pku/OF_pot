from db import Base, engine
import models  # noqa: F401

def init_db():
    Base.metadata.create_all(engine)