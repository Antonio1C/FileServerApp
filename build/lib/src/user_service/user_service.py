from datetime import datetime, timedelta
from aiohttp import request
from psycopg2 import sql
import uuid

class UserService:

    
    def __init__(self, db):
        self.db = db


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


    async def is_autorized(self, uuid: str) -> bool:
        cursor = self.db.cursor()
        request = sql.SQL(f'''SELECT uuid, expiration_date FROM public."sessions"
                        WHERE uuid = '{uuid}' ''')
        cursor.execute(request)
        result = cursor.fetchone()
        if result == None: return False
        if datetime.now() > result[1]:
            await self.logout(uuid)
            return False
        
        # need to update session time
        exp_date = self.calc_expir_date()
        request = sql.SQL(f'''UPDATE sessions SET expiration_date = '{exp_date}'
                                WHERE uuid = '{uuid}' ''')
        
        cursor.execute(request)
        self.db.commit()
        
        return True


    async def logout(self, uuid: str) -> None:
        cursor = self.db.cursor()
        request = sql.SQL(f'DELETE FROM public."sessions" WHERE uuid = \'{uuid}\'')
        cursor.execute(request)
        self.db.commit()