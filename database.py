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
    db_url = 'postgres://lpilqufqtyyyty:c58229c2efc4838576b1aa003659e3dbedaf3daef39aeae99bf4b8626935182f@ec2-75-101-133-29.compute-1.amazonaws.com:5432/d8dndq07tlbq07'

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