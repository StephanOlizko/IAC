import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import BigInteger, create_engine, select, update
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

COUNTER_ID = 1

engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
    ),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Counter(Base):
    __tablename__ = "counter"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(BigInteger, default=0)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as session:
        if session.get(Counter, COUNTER_ID) is None:
            session.add(Counter(id=COUNTER_ID, value=0))
    yield


app = FastAPI(title="Counter", lifespan=lifespan)


def get_session():
    with SessionLocal.begin() as session:
        yield session


def read_value(session: Session) -> int:
    return session.scalar(select(Counter.value).where(Counter.id == COUNTER_ID))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/counter")
def get_counter(session: Session = Depends(get_session)):
    return {"value": read_value(session)}


@app.post("/api/counter")
def increment_counter(session: Session = Depends(get_session)):
    session.execute(
        update(Counter).where(Counter.id == COUNTER_ID).values(value=Counter.value + 1)
    )
    return {"value": read_value(session)}
