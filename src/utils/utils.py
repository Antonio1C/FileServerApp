#! /usr/bin/env/ python

import random
import string

def random_string(length):
    '''
    Generate random string using ASCII letters and digits with needed length

    Parameters
    ------------
        length: int
            length of generated string

    Returns
    ------------
        generated string
    '''
    r_string = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
    return r_string