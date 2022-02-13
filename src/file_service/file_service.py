#! /usr/bin/env/ python

from typing import Optional
from abc import ABCMeta, abstractmethod


class FileService(metaclass=ABCMeta):

    @abstractmethod
    def pwd(self) -> str: raise Exception('not implemented')
    
    
    @abstractmethod
    def abspath(self, fd_name:str) -> str: raise Exception('not implemented')


    @abstractmethod
    def create(self, data: str) -> str: raise Exception('not implemented')


    @abstractmethod
    def read(self, filename: str) -> Optional[str]: raise Exception('not implemented')


    @abstractmethod
    def ls(self) -> list: raise Exception('not implemented')


    @abstractmethod
    def chdir(self, new_directory): raise Exception('not implemented')


    @abstractmethod
    def delete(self, filename: str): raise Exception('not implemented')


    @abstractmethod
    def get_meta_data(self, filename: str) -> tuple: raise Exception('not implemented')

