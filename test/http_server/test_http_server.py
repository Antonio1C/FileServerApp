from calendar import c
import os
import shutil
import pytest
from src.file_service import RawFileService, SignedFileService, EncryptedFileService
from src.http_server import create_web_app
import json

filename = 'test_file_name'
filedata = 'Data for test file'
test_path = os.path.abspath('./test/test_path')

@pytest.fixture()
async def client_server(mocker, aiohttp_client):

    Config = mocker.patch('src.config.Config')
    
    if not os.path.exists(test_path):
        os.mkdir(test_path)
    Config().working_directory = test_path
    
    keys_dir = os.path.join(test_path, 'keys')
    if not os.path.exists(keys_dir):
        os.mkdir(keys_dir)
    sign_dir = os.path.join(test_path, 'signature_files')
    if not os.path.exists(sign_dir):
        os.mkdir(sign_dir)
    
    Config().encryption_keys_path = keys_dir
    Config().signature_dir = sign_dir

    file_service = SignedFileService(RawFileService(test_path))
    file_service = EncryptedFileService(file_service)
    server = create_web_app(file_service)
    
    client = await aiohttp_client(server)
    return client, server


async def test_check_create(mocker, client_server):
    
    global filename

    client, _ = client_server
    response = await client.post('/create', data = filedata)
    
    assert response.status == 200
    
    data = b''
    while not response.content.at_eof():
        data += await response.content.read()
    data_dict = json.loads(data.decode())
    
    assert list(data_dict.keys()) == ['filename', 'creation_time', 'modification_time', 'file_size']
    filename = data_dict['filename']


async def test_check_ls(mocker, client_server):
    
    client, _ = client_server
    response = await client.get('/ls')
    
    data = b''
    while not response.content.at_eof():
        data += await response.content.read()
    
    files_list = [filename, 'keys', 'signature_files']
    files_list.sort()
    assert data.decode() == '\n'.join(files_list)


async def test_check_read(client_server):
    client, _ = client_server
    response = await client.get(f'/read?filename={filename}')

    assert response.status == 200
    
    data = b''
    while not response.content.at_eof():
        data += await response.content.read()
    
    assert data.decode() == json.dumps({'content': filedata})


async def test_check_delete(client_server):
    client, _ = client_server
    response = await client.get(f'/delete?filename={filename}')

    assert response.status == 200
    
    data = b''
    while not response.content.at_eof():
        data += await response.content.read()
    
    assert data.decode() == json.dumps({'action': f'file {filename} was deleted'})


def test_delete_test_path():
    shutil.rmtree(test_path)
    assert not os.path.exists(test_path)