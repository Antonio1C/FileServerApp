#! /usr/bin/env/ python

import pytest
from src import file_service, crypto
from mock import mock_open
import mock

@pytest.fixture()
def os_path_isfile_mocker_true(mocker):
    os_path_file_mock = mocker.patch("os.path.isfile")
    os_path_file_mock.return_value = True
    return os_path_file_mock


@pytest.fixture()
def os_path_isfile_mocker_false(mocker):
    os_path_file_mock = mocker.patch("os.path.isfile")
    os_path_file_mock.return_value = False
    return os_path_file_mock


def test_list_dir(mocker):
    list_dir_mock = mocker.patch("os.listdir")
    list_dir_mock.return_value = ["a", "b", "c"]
    res = file_service.list_dir()
    assert res == ["a", "b", "c"]


def test_create_file(mocker):
    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True)
    
    random_file_name = 'test_random_string'
    mocker.patch("src.utils.random_string").return_value = random_file_name

    my_content = "my content"
    file_service.create_file(my_content)

    mocked_open.assert_called_with(random_file_name, 'w')
    mocked_open().write.assert_called_with(my_content)


def test_create_signature_file(mocker):
    test_file_name = 'test_file_name'
    test_label = 'test_label'

    mock_create_file = mocker.patch('src.file_service.file_service.create_file')
    mock_create_file.return_value = test_file_name

    mock_get_signer = mocker.patch('src.crypto.SignatureFactory.get_signer')
    mock_get_signer.return_value = crypto.Md5Signer

    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True)

    file_content = 'test file content'
    file_service.create_signature_file(file_content, test_label)

    expected_sign = crypto.Md5Signer()(file_content)

    sign_file_name = f'{test_file_name}.{test_label}'

    mocked_open.assert_called_with(sign_file_name, 'w')
    mocked_open().write.assert_called_with(expected_sign)


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
        assert filename == second_file_name
        return False

    mock_exists = mocker.patch("os.path.exists")
    mock_exists.side_effect = os_path_exists_side_effect

    mock_rand_string = mocker.patch("src.utils.random_string")
    
    def random_string_side_effect(length):
        
        if len(mock_rand_string.mock_calls) == 1:
            return first_file_name
        return second_file_name
    
    mock_rand_string.side_effect = random_string_side_effect
    
    my_content = "my content"
    file_service.create_file(my_content)

    mocked_open.assert_called_with(second_file_name, 'w')
    assert mock_exists.mock_calls == [mock.call(first_file_name), mock.call(second_file_name)]
    mocked_open().write.assert_called_with(my_content)


def test_read_file_success_flow(mocker, os_path_isfile_mocker_true):

    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True) 

    file_content = "file content"
    mocked_open().read.return_value = file_content

    test_filename = "test_file_name"
    
    mock_isfile = os_path_isfile_mocker_true

    result = file_service.read_file(test_filename)
    
    mocked_open.assert_called_with(test_filename, "r")
    mocked_open().read.assert_called()


def test_read_file_not_existed(mocker, os_path_isfile_mocker_false):

    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True) 

    test_filename = "test_file_name"
    
    mock_isfile = os_path_isfile_mocker_false

    with pytest.raises(FileNotFoundError):
        result = file_service.read_file(test_filename)
    
    mock_isfile.assert_called_with(test_filename)


def test_delete_file_success_flow(mocker, os_path_isfile_mocker_true):

    test_filename = "test_file_name"

    mock_isfile = os_path_isfile_mocker_true
    mock_remove = mocker.patch("os.remove")
    
    file_service.delete_file(test_filename)

    mock_isfile.assert_called_with(test_filename)
    mock_remove.assert_called_with(test_filename)


def test_delete_file_not_existed(mocker, os_path_isfile_mocker_false):

    test_filename = "test_file_name"

    mock_isfile = os_path_isfile_mocker_false
    mock_remove = mocker.patch("os.remove")
    
    with pytest.raises(FileNotFoundError):
        file_service.delete_file(test_filename)

    mock_isfile.assert_called_with(test_filename)


def test_change_dir_success_flow(mocker):

    test_dir = "test_dir"

    mock_isdir = mocker.patch("os.path.isdir")
    mock_isdir.return_value = True
    mock_chdir = mocker.patch("os.chdir")
    
    file_service.change_dir(test_dir)

    mock_isdir.assert_called_with(test_dir)
    mock_chdir.assert_called_with(test_dir)


def test_change_dir_not_existed(mocker):

    test_dir = "test_dir"

    mock_isdir = mocker.patch("os.path.isdir")
    mock_isdir.return_value = False
    mock_chdir = mocker.patch("os.chdir")
    
    with pytest.raises(NotADirectoryError):
        file_service.change_dir(test_dir)

    mock_isdir.assert_called_with(test_dir)


def test_get_file_meta_data_success_flow(mocker, os_path_isfile_mocker_true):

    test_filename = "test_file_name"

    mock_os_stat = mocker.patch("os.stat")
    mock_os_stat.return_value.st_ctime = 2347
    mock_os_stat.return_value.st_mtime = 93465
    mock_os_stat.return_value.st_size = 73457

    mock_isfile = os_path_isfile_mocker_true

    assert file_service.get_file_meta_data(test_filename) == (2347, 93465, 73457)
    mock_isfile.assert_called_with(test_filename)
    mock_os_stat.assert_called_with(test_filename)


def test_get_file_meta_data_not_existed(os_path_isfile_mocker_false):

    test_filename = "test_file_name"

    mock_isfile = os_path_isfile_mocker_false

    assert file_service.get_file_meta_data(test_filename) == None
    mock_isfile.assert_called_with(test_filename)

