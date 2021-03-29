import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

from config import config

logger = logging.getLogger(__name__)
engine = create_engine(config.POSTGRES_URI)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()


def init_db():
    logger.info("init_db")
    # Здесь необходимо импортировать все модули с моделями, которые должны зарегистрироваться в ORM.
    # В противном случае, их нужно импортировать до вызова init_db()
    # Это необходимо, чтобы sqlalchemy увидел все таблицы и при необходимости создал их.
    import storage.db_models

    Base.metadata.create_all(bind=engine)
