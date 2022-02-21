import argparse
from src.config import Config
from src.file_service import RawFileService, SignedFileService, EncryptedFileService
from src.user_service import UserService
import logging
import logging.config
import yaml
from aiohttp import web
from src.http_server import create_web_app
import psycopg2
import os

def app():
    logging_config_file = os.path.join(os.path.dirname(__file__), 'logging_config.yaml')
    with open(file=logging_config_file, mode='r') as f:
        logging_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
    
    logging.config.dictConfig(config=logging_yaml)

    logging.info('start server')

    parser = argparse.ArgumentParser("File server application")
    parser.add_argument("-d", "--directory", help='Set current directory')
    parser.add_argument('-c', '--config', help='file with server configuration', default='config.ini')
    
    logging.info('parse arguments')
    args = parser.parse_args()
    logging.info(f"getting args: {args}")

    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config_file = args.config if args.config != None else config_file

    config = Config()
    config.load(config_file)
    
    work_dir = args.directory if args.directory != None else config.working_directory()
    
    file_service = RawFileService(work_dir)
    if config.use_signature(): file_service = SignedFileService(file_service)
    if config.use_encryption(): file_service = EncryptedFileService(file_service)

    conn = psycopg2.connect(dbname='file_server', user='postgres', password='postgres', host='192.168.10.1')
    user_service = UserService(conn)
    app = create_web_app(file_service, user_service)
    web.run_app(app)
