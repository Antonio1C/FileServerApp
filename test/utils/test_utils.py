#! /usr/bin/env/ python

from src import utils

def test_random_string():
    
    generated_strings = []
    string_length = 10
    for i in range(100):
        new_string = utils.random_string(string_length)
        assert new_string not in generated_strings
        assert len(new_string) == string_length
        generated_strings.append(new_string)
