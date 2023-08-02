from config import DATABASE_URI
from models import Base, Recording
from consumer import Consumer

import pprint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

pp = pprint.PrettyPrinter(indent=4)
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def mq_callback(ch, method, properties, body):
    print(" Received a message!")

    recording = Recording(body.decode())
    pp.pprint(recording)

    with session_scope() as sesh:
        try:
            sesh.add(recording)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print('that didnt work %r' % (e))



if __name__ == "__main__":
    consumer = Consumer(mq_callback)