import pytest

from app.db import database


#************************
#* Double de session    *
#************************

class DummySession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


#***************************
#* Tests du cycle get_db() *
#***************************

def test_get_db_yields_a_session(monkeypatch):
    session = DummySession()
    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    generator = database.get_db()
    yielded_session = next(generator)

    assert yielded_session is session

    generator.close()


def test_get_db_closes_session_when_generator_is_exhausted(monkeypatch):
    session = DummySession()
    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    generator = database.get_db()
    next(generator)

    with pytest.raises(StopIteration):
        next(generator)

    assert session.closed is True
