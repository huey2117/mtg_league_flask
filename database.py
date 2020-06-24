import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


test = False
if test:
    postgres = {
        'user': 'dbtest',
        'password': 'devdbtest',
        'host': 'localhost',
        'port': '5432',
        'dbname': 'd8dndq07tlbq07'
    }

    db_url = f"postgresql://{postgres['user']}:{postgres['password']}@" \
        f"{postgres['host']}:{postgres['port']}/{postgres['dbname']}"
    # db_url = os.environ['TESTDB_URL']
else:
    db_url = os.environ['DATABASE_URL']

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