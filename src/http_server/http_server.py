from genericpath import exists
import os
from aiohttp import web
import json
import aiohttp_jinja2, jinja2
import pathlib2 as plib
from src.config import Config

from src.user_service import UserService
from src.file_service import RawFileService, SignedFileService, EncryptedFileService
from src.user_service import User

MODULE_PATH = plib.PurePath(__file__).parent

def check_authorization(func):
    async def wrapper(self, request, *args, **kwargs):
        try:
            user_name = request.match_info['user_name']
            if not user_name in self.users.keys():
                raise web.HTTPFound('/login')

            # TODO have to using header 'Authorization'
            # h_auth = 'Authorization'
            # if not h_auth in request.headers:
            #     raise web.HTTPFound('/login')
            
            # uuid = request.headers['Authorization']
            # if not await user_service.is_autorized(uuid):
            #     return bad_auth
            
            user_service = self.users[user_name].user_service
            if not await user_service.is_authorized(user_name):
                raise web.HTTPFound('/login')
            
            return await func(self, request, *args, **kwargs)
        except Exception as ex:
            raise ex
    
    return wrapper


def create_file_service(work_dir:str):
    try:
        config = Config()
        user_dir = os.path.join(config.filestorage_directory(), work_dir)
        file_service = RawFileService(user_dir)
        if config.use_signature(): file_service = SignedFileService(file_service)
        if config.use_encryption(): file_service = EncryptedFileService(file_service)
        
        return file_service
        
    except Exception as ex:
        print(ex)


class Handler:

    def __init__(self, db_conn):
        self.__users = {}
        self.__db_conn = db_conn


    @property
    def users(self):
        return self.__users
        
        
    @property
    def db_conn(self):
        return self.__db_conn 
    
    
    @check_authorization
    async def ls(self, request, *args, **kwargs):
        try:
            username = request.match_info['user_name']
            file_service = self.users[username].file_service
            files_list = file_service.ls()
            files_list.sort()
            files_list = '\n'.join(files_list)
            return web.Response(text=files_list)
        except Exception as ex:
            print(ex)
            return web.Response(text='Error')


    @check_authorization
    async def pwd(self, request, *args, **kwargs):
        work_dir = self.file_service.pwd()
        return web.Response(text=work_dir)


    @check_authorization
    async def create(self, request: web.Request, *args, **kwargs):
        try:
            data = b''
            while not request.content.at_eof():
                data += await request.content.read()

            filename = await self.file_service.create(data)
            meta_data = self.file_service.get_meta_data(filename)
            
            response = {
                'filename': filename,
                'creation_time': meta_data[0],
                'modification_time': meta_data[1],
                'file_size': meta_data[2]
            }

            return web.Response(text=json.dumps(response))
        except Exception as ex:
            print(ex)


    @check_authorization
    async def read(self, request, *args, **kwargs):
        try:
            params = request.query
            if not 'filename' in params.keys():
                return web.Response(status=403, text='need to get filename')
            filename = params['filename']
            content = await self.file_service.read(filename)
            content = content.decode()
            
            response = {
                'content': content
            }
            return web.Response(text=json.dumps(response))
        
        except Exception as ex:
            print(ex)


    @check_authorization
    async def delete(self, request, *args, **kwargs):
        try:
            params = request.query
            if not 'filename' in params.keys():
                return web.Response(status=403, text='need to get filename')
                
            filename = params['filename']
            
            self.file_service.delete(filename)

            response = {
                'action': f'file {filename} was deleted'
            }
            return web.Response(text=json.dumps(response))

        except Exception as ex:
            print(ex)


    @check_authorization
    async def chdir(self, request, *args, **kwargs):
        try:
            params = request.query
            if not 'dirname' in params.keys():
                return web.Response(status=403, text='need to get dirname')
                
            dirname = params['dirname']
            
            self.file_service.chdir(dirname)

            response = f'new directory now {dirname}'
            return web.Response(text=response)

        except Exception as ex:
            print(ex)


    async def main_page(self, request, *args, **kwargs):
        raise web.HTTPFound('/login')


    async def signin(self, request, *args, **kwargs):
        try:
            data = b''
            while not request.content.at_eof():
                data += await request.content.read()
            
            data = json.loads(data)
            await self.user_service.add_user(data['username'], data['pwd'])
            
            return web.Response(text='user was successfully "created"')
        except Exception as ex:
            print(ex)


    @aiohttp_jinja2.template('login.html')
    async def login_page(self, request, *args, **kwargs):
        return dict()


    async def login(self, request, *args, **kwargs):
        data = await request.post()
        if data['login'] == '':
            raise web.HTTPFound('/login')
        
        user_name = data["login"]
        user_service = UserService(self.db_conn)
        file_service = create_file_service(user_name)
        user = User(user_name, file_service, user_service)
        self.users[user_name] = user

        await user_service.add_session(user_name, data['pwd'])

        new_url = f'/{user_name}/ls'
        raise web.HTTPFound(new_url)


    async def logout(self, request, *args, **kwargs):
        try:
            uuid = request.headers['Authorization']
            await self.user_service.logout(uuid)
            return web.Response(text='Successful logout')
            
        except Exception as ex:
            print(ex)


def create_web_app(db_conn):

    app = web.Application()
    
    handler = Handler(db_conn)

    template_dir = plib.Path(MODULE_PATH, 'templates')
    aiohttp_jinja2.setup(app,
                    loader=jinja2.FileSystemLoader(template_dir.absolute()))
    
    static_dir = plib.Path(MODULE_PATH, 'static')
    app.router.add_static('/static/',
            path=static_dir.absolute(),
            name='static')
    app['static_root_url'] = '/static'

    app.add_routes([
        web.get('/', handler.main_page),
        web.get('/{user_name}/ls', handler.ls),
        web.get('/pwd', handler.pwd),
        web.get('/read', handler.read),
        web.put('/chdir', handler.chdir),
        web.get('/delete', handler.delete),
        web.post('/create', handler.create),
        web.post('/signin', handler.signin),
        web.post('/logout', handler.logout),
        web.get('/login', handler.login_page),
        web.post('/login', handler.login),
    ])

    return app