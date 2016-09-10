# -*- coding: utf-8 -*-

import string
import random


def random_name(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
