from fileinput import filename
from urllib import response
from aiohttp import web
import json

from src.file_service import FileService
from src.file_service.raw_file_service import RawFileService

class Handler:

    def __init__(self, file_service: FileService):
        self.file_service = file_service

    async def ls(self, request, *args, **kwargs):
        files_list = self.file_service.ls()
        file_list = '\n'.join(files_list)
        return web.Response(text=file_list)


    async def pwd(self, request, *args, **kwargs):
        work_dir = self.file_service.pwd()
        return web.Response(text=work_dir)


    async def create(self, request: web.Request, *args, **kwargs):
        try:
            params = request.query
            if not 'content' in params.keys():
                return web.Response(status=403, text='not found content!')
            
            data = ''
            while not request.content.at_eof():
                data += await request.content.read()
            content = params['content']
            filename = self.file_service.create(content.encode())
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

    async def read(self, request, *args, **kwargs):
        try:
            params = request.query
            if not 'filename' in params.keys():
                return web.Response(status=403, text='need to get filename')
            filename = params['filename']
            content = self.file_service.read(filename).decode()

            response = {
                'content': content
            }
            return web.Response(text=json.dumps(response))

        except Exception as ex:
            print(ex)


    async def delete(self, request, *args, **kwargs):
        pass


    async def chdir(self, request, *args, **kwargs):
        pass



def create_web_app(file_service: FileService):

    app = web.Application()
    handler = Handler(file_service)

    app.add_routes([
        web.get('/ls', handler.ls),
        web.get('/pwd', handler.pwd),
        web.post('/create', handler.create),
        web.get('/read', handler.read),
        web.get('/delete', handler.delete),
        web.put('/chdir', handler.chdir)
    ])

    return app