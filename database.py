import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv


load_dotenv()
db_url = (
    os.environ['TESTDB_URL']
    if os.getenv('APP_DEBUG')
    else os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://', 1)
          )

engine = create_engine(db_url, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import pgmodels
    Base.metadata.create_all(bind=engine)
