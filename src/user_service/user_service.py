from datetime import datetime, timedelta
from psycopg2 import sql
import uuid

from src.file_service import FileService


class UserService:

    
    def __init__(self, db):
        self._db = db


    @property
    def db(self):
        return self._db
        
        
    async def __get_user_new_id(self, cursor) -> int:
        request = sql.SQL(f'SELECT user_id FROM public."users" ORDER BY user_id DESC LIMIT 1')
        cursor.execute(request)
        result = cursor.fetchone()
        if result == None: return 1

        return result[0] + 1
    
    
    def calc_expir_date(self):
        return datetime.now() + timedelta(minutes=30)
    
    
    async def add_user(self, username: str, passwd: str) -> int:
        cursor = self.db.cursor()
        user_id = self.get_user_new_id(cursor)
        request = sql.SQL(f'''INSERT INTO  public."users" (user_id, name, passwd)
                             VALUES ('{user_id}', '{username}', '{passwd}')''')
        cursor.execute(request)
        self.db.commit()


    async def add_session(self, username, passwd) -> str:
        cursor = self.db.cursor()
        request = sql.SQL(f'''SELECT user_id FROM public."users"
                            WHERE name = '{username}' AND passwd = '{passwd}' ''')
        cursor.execute(request)
        result = cursor.fetchone()
        if result == None: return None

        user_id = result[0]
        new_uuid = f'{uuid.uuid1()}'
        expiration_date = self.calc_expir_date()
        request = sql.SQL(f'''INSERT INTO public."sessions" (user_id, uuid, expiration_date)
                            VALUES ('{user_id}', '{new_uuid}', '{expiration_date}')''')
        
        cursor.execute(request)
        self.db.commit()
        
        return new_uuid


    async def is_authorized(self, name: str) -> bool:
        cursor = self.db.cursor()
        request = sql.SQL(f'''SELECT user_id FROM public."users"
                        WHERE name='{name}' ''')
        cursor.execute(request)
        result = cursor.fetchone()
        user_id = result[0]
        
        request = sql.SQL(f'''SELECT uuid, expiration_date FROM public."sessions"
                        WHERE user_id = '{user_id}' ''')
        cursor.execute(request)
        result = cursor.fetchone()
        
        if result == None: return False
        
        session_uuid = result[0]
        if datetime.now() > result[1]:
            await self.logout(session_uuid)
            return False
        
        # need to update session time
        exp_date = self.calc_expir_date()
        request = sql.SQL(f'''UPDATE sessions SET expiration_date = '{exp_date}'
                                WHERE uuid = '{session_uuid}' ''')
        
        cursor.execute(request)
        self.db.commit()
        
        return True


    async def logout(self, uuid: str) -> None:
        cursor = self.db.cursor()
        request = sql.SQL(f'DELETE FROM public."sessions" WHERE uuid = \'{uuid}\'')
        cursor.execute(request)
        self.db.commit()


class User:
    
    
    def __init__(self, name: str, file_service: FileService, user_service: UserService):
        self._name = name
        self._user_service = user_service
        self._file_service = file_service
    
    
    @property
    def name(self):
        return self._name
    
    
    @property
    def user_service(self):
        return self._user_service
        
         
    @property
    def file_service(self):
        return self._file_service