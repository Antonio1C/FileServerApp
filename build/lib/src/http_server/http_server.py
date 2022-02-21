from aiohttp import web
import json

from src.user_service import UserService
from src.file_service import FileService

def check_authorization(func):
    async def wrapper(self, request, *args, **kwargs):
        try:
            user_service = self.user_service
            h_auth = 'Authorization'
            bad_auth = web.Response(text='need to authorize!')
            if not h_auth in request.headers:
                return bad_auth
            
            uuid = request.headers['Authorization']
            if not await user_service.is_autorized(uuid):
                return bad_auth
            
            return await func(self, request, *args, **kwargs)
        except Exception as ex:
            print(ex)
            raise ex
    
    return wrapper


class Handler:

    def __init__(self, file_service: FileService, user_service: UserService):
        self.user_service = user_service
        self.file_service = file_service


    @check_authorization
    async def ls(self, request, *args, **kwargs):
        files_list = self.file_service.ls()
        files_list.sort()
        files_list = '\n'.join(files_list)
        return web.Response(text=files_list)


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


    async def login(self, request, *args, **kwargs):
        try:
            data = b''
            while not request.content.at_eof():
                data += await request.content.read()
            
            data = json.loads(data)
            uuid = await self.user_service.add_session(data['username'], data['pwd'])

            return web.Response(text=uuid)
        except Exception as ex:
            print(ex)


    async def logout(self, request, *args, **kwargs):
        try:
            uuid = request.headers['Authorization']
            await self.user_service.logout(uuid)
            return web.Response(text='Successful logout')
            
        except Exception as ex:
            print(ex)


def create_web_app(file_service: FileService, user_service: UserService):

    app = web.Application()
    handler = Handler(file_service, user_service)

    app.add_routes([
        web.get('/ls', handler.ls),
        web.get('/pwd', handler.pwd),
        web.get('/read', handler.read),
        web.put('/chdir', handler.chdir),
        web.get('/delete', handler.delete),
        web.post('/create', handler.create),
        web.post('/signin', handler.signin),
        web.post('/logout', handler.logout),
        web.post('/login', handler.login),
    ])

    return app