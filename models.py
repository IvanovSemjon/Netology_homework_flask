import atexit
import datetime
from sqlalchemy import (
    create_engine,
    Integer,
    String,
    DateTime,
    func,
    ForeignKey
)
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    MappedColumn,
    mapped_column
)


# Используем SQLite для упрощения тестирования
engine = create_engine('sqlite:///bulletin_board.db')
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    email: MappedColumn[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    password_hash: MappedColumn[str] = mapped_column(
        String(128), nullable=False
    )

    @property
    def json(self):
        return {
            'id': self.id,
            'email': self.email
        }

    @property
    def id_json(self):
        return {'id': self.id}


class Bulletin_board(Base):
    __tablename__ = 'bulletin_board'

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    title: MappedColumn[str] = mapped_column(String(80))
    text: MappedColumn[str] = mapped_column(String(1000))
    registration_date: MappedColumn[datetime.datetime] = mapped_column(
        DateTime, default=func.now()
    )
    user_id: MappedColumn[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )

    @property
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'registration_date': self.registration_date.isoformat(),
            'user_id': self.user_id
        }

    @property
    def id_json(self):
        return {'id': self.id}


Base.metadata.create_all(engine)

atexit.register(engine.dispose)
