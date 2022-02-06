#! /usr/bin/env/ python

from src import file_service, utils
from mock import mock_open
import mock


def test_list_dir(mocker):
    list_dir_mock = mocker.patch("os.listdir")
    list_dir_mock.return_value = ["a", "b", "c"]
    res = file_service.list_dir()
    assert res == ["a", "b", "c"]


def test_create_file(mocker):
    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True)
    
    random_file_name = 'test_random_string'
    mocker.patch("src.file_service.file_service.unique_filename").return_value = random_file_name

    my_content = "my content"
    file_service.create_file(my_content)

    mocked_open.assert_called_with(random_file_name, 'w')
    mocked_open().write.assert_called_with(my_content)


def test_unique_filename(mocker):
    some_random_string = "some_rand_string"
    mock_rand_string = mocker.patch("src.utils.random_string")
    mock_rand_string.return_value = some_random_string

    res = file_service.file_service.unique_filename()
    assert res == some_random_string


def test_create_file_duplicate(mocker):
    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True)

    path_exists_calls_count = 0 

    first_file_name = 'first_file_name'
    second_file_name = 'second_file_name'

    def os_path_exists_side_effect(filename):
        nonlocal path_exists_calls_count
        path_exists_calls_count += 1
        
        if path_exists_calls_count == 1:
            assert filename == first_file_name
            return True
        elif path_exists_calls_count == 2:
            assert filename == second_file_name
        return False

    mock_exists = mocker.patch("os.path.exists")
    mock_exists.side_effect = os_path_exists_side_effect

    mock_uniq_file_name = mocker.patch("src.file_service.file_service.unique_filename")
    
    def unique_filename_side_effect():
        
        if len(mock_uniq_file_name.mock_calls) == 1:
            return first_file_name
        else:
            return second_file_name
    
    mock_uniq_file_name.side_effect = unique_filename_side_effect
    
    my_content = "my content"
    file_service.create_file(my_content)

    mocked_open.assert_called_with(second_file_name, 'w')
    assert mock_exists.mock_calls == [mock.call(first_file_name), mock.call(second_file_name)]
    mocked_open().write.assert_called_with(my_content)


def test_read_file(mocker):

    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True) 

    file_content = "file content"
    mocked_open().read.return_value = file_content

    test_filename = "test_file_name"
    another_filename = "another_file_name"

    def os_path_isfile_side_effect(filename):
        if filename == test_filename:
            return True
        return False
    
    mock_isfile = mocker.patch("os.path.isfile")
    mock_isfile.side_effect = os_path_isfile_side_effect

    result = file_service.read_file(test_filename)
    
    assert result == file_content
    mocked_open.assert_called_with(test_filename, "r")
    mocked_open().read.assert_called()

    result = file_service.read_file(another_filename)

    assert result == None
    assert mocked_open().read.call_count == 1


def test_delete_file(mocker):

    test_filename = "test_file_name"
    another_filename = "another_file_name"

    def os_path_isfile_side_effect(filename):
        if filename == test_filename:
            return True
        return False
    
    mock_isfile = mocker.patch("os.path.isfile")
    mock_isfile.side_effect = os_path_isfile_side_effect

    mock_remove = mocker.patch("os.remove")
    
    file_service.delete_file(test_filename)

    mock_remove.assert_called_with(test_filename)
    
    file_service.delete_file(another_filename)

    assert mock_remove.call_count == 1


def test_change_dir(mocker):

    test_dir = "test_dir"
    another_dir = "another_dir"

    def os_path_isdir_side_effect(dirname):
        if dirname == test_dir:
            return True
        return False
    
    mock_isfile = mocker.patch("os.path.isdir")
    mock_isfile.side_effect = os_path_isdir_side_effect

    mock_chdir = mocker.patch("os.chdir")
    
    file_service.change_dir(test_dir)

    mock_chdir.assert_called_with(test_dir)
    
    file_service.change_dir(another_dir)

    assert mock_chdir.call_count == 1
