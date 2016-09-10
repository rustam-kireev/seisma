# -*- coding: utf-8 -*-

import os

from importlib import import_module

from flask import Blueprint


def is_package(path):
    return os.path.isfile(
        os.path.join(path, '__init__.py'),
    )


def is_py_module(file_name):
    return not file_name.startswith('_') \
        and file_name.endswith('.py')


def load_module(module_name, package=None):
    module_name = '{}{}'.format(
        package + '.' if package else '', module_name,
    )

    module = import_module(module_name)

    return module


def load_blueprints_from_module(module):
    for attribute in dir(module):
        value = getattr(module, attribute, None)
        if isinstance(value, Blueprint):
            yield value


def load_blueprints(path_to_dir, package=None, recursive=True):
    lst_dir = os.listdir(path_to_dir)
    full_path = lambda *n: os.path.join(path_to_dir, *n)

    modules = (n.replace('.py', '') for n in lst_dir if is_py_module(n))

    for module_name in modules:
        module = load_module(module_name, package=package)

        for suite in load_blueprints_from_module(module):
            yield suite

    if recursive:
        packs = (n for n in lst_dir if is_package(full_path(n)))

        for pack in packs:

            for suite in load_blueprints(
                    full_path(pack),
                    recursive=recursive,
                    package='{}.{}'.format(package, pack) if package else pack):
                yield suite
