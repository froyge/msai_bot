from sqlalchemy.engine import CursorResult, Engine
from sqlalchemy import create_engine, Column, Integer, String, select, update, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from config import DATABASE


Base = declarative_base()


class UserData(Base):
    __tablename__ = "user_data"
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    user_name = Column(String)
    aki_lang = Column(String, default='en')
    child_mode = Column(Integer, default=1)


class MyDB:
    engine: Engine = create_engine(URL.create(**DATABASE))


def getlanguage(user_id: int) -> str:
    """
    Returns the Language Code of the user. (str)
    """
    stmt = select(UserData.aki_lang).where(UserData.user_id == user_id)
    with MyDB.engine.connect() as conn:
        cur = conn.execute(stmt)
        return cur.fetchone()[0]


def getchildmode(user_id: int) -> int:
    """
    Returns the Child mode status of the user. (str)
    """
    stmt = select(UserData.child_mode).where(UserData.user_id == user_id)
    with MyDB.engine.connect() as conn:
        cur = conn.execute(stmt)
        return cur.fetchone()[0]


def updatelanguage(user_id: int, lang_code: str) -> None:
    """
    Update Akinator Language for the User.
    """
    stmt = update(UserData).where(UserData.user_id == user_id).values(aki_lang=lang_code)
    with MyDB.engine.connect() as conn:
        conn.execute(stmt)
    print(f"User {user_id}: Language updated")


def updatechildmode(user_id: int, mode: int) -> None:
    """
    Update Child Mode of the User.
    """
    stmt = update(UserData).where(UserData.user_id == user_id).values(child_mode=mode)
    with MyDB.engine.connect() as conn:
        conn.execute(stmt)
    print(f"User {user_id}: Child mode updated")


def adduser(user_id: int, first_name: str, last_name: str, user_name: str) -> None:
    """
    Adding the User to the database. If user already present in the database,
    it will check for any changes in the user_name, first_name, last_name and will update if true.
    """
    with MyDB.engine.connect() as conn:
        cursor: CursorResult = conn.execute(select(UserData.user_id).where(UserData.user_id == user_id))
        if cursor.rowcount == 0:
            stmt = insert(UserData).values(user_id=user_id,
                                           first_name=first_name,
                                           last_name=last_name,
                                           user_name=user_name)
            conn.execute(stmt)
            print('User inserted', user_name)
        else:
            stmt = update(UserData).where(UserData.user_id == user_id) \
                .values(first_name=first_name, last_name=last_name, user_name=user_name)
            conn.execute(stmt)
            print('User updated')


def main():
    Base.metadata.create_all(MyDB.engine)


if __name__ == "__main__":
    main()
