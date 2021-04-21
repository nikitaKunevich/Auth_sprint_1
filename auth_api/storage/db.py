import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from config import config

logger = logging.getLogger(__name__)
engine = create_engine(config.POSTGRES_URI)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


def init_db():
    logger.info("init_db")
    import storage.db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
