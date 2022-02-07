#! /usr/bin/env/ python

import random
import string

def random_string(length):
    r_string = ''.join(random.choice(string.ascii_letters + '0123456789') for i in range(length))
    return r_string