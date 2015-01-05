#!/usr/bin/python3
from __future__ import print_function, unicode_literals
import copy
import os
import shutil
import sys

from doit.loader import generate_tasks
from doit.cmd_base import TaskLoader
from doit.reporter import ExecutedOnlyReporter
from doit.doit_cmd import DoitMain


class MyTaskLoader(TaskLoader):
    task_getter = lambda self: self.program.get_all_tasks()

    def __init__(self, program):
        self.program = program

    def load_tasks(self, cmd, opt_values, pos_args):
        DOIT_CONFIG = {
            'reporter': ExecutedOnlyReporter,
            'outfile': sys.stderr,
            'default_tasks': ['copy'],
        }
        tasks = generate_tasks('test', self.task_getter())
        return tasks, DOIT_CONFIG

    @staticmethod
    def get_partial_loader(level):
        TL = copy.copy(MyTaskLoader)
        TL.task_getter = lambda self: self.program.get_tasks(level)
        return TL


class MyDoit_Impl(DoitMain):
    def __init__(self, program, TASK_LOADER):
        self.program = program
        self.TASK_LOADER = TASK_LOADER
        self.task_loader = self.TASK_LOADER(program)

    def run(self, cmd_args):
        command = cmd_args[0]
        # ...
        return super(MyDoit_Impl, self).run(cmd_args)


class MyDoit(object):
    def __init__(self, program):
        self.program = program

    def run(self, cmd_args):
        command = cmd_args[0]
        if command == 'run':
            for level in self.program.get_task_levels():
                print("Processing level {0}".format(level))
                impl = MyDoit_Impl(self.program, MyTaskLoader.get_partial_loader(level))
                res = impl.run(cmd_args)
                if res != 0:
                    return res
            return 0
        else:
            impl = MyDoit_Impl(self.program, MyTaskLoader)
            return impl.run(cmd_args)


def get_content(filename):
    with open(filename, "rb") as f:
        return f.read().decode('utf-8')


def write_content(filename, content):
    with open(filename, "wb") as f:
        f.write(content.encode('utf-8'))


class Program():
    def _do_copy(self, source, destination):
        content = get_content(source)
        if not content.startswith('copy'):
            content = ''
        content += 'copy "{0}" to "{1}"\n'.format(source, destination)
        write_content(destination, content)

    def get_task_levels(self):
        return [1, 2, 3]

    def _create_tasks(self, *files):
        for src_file, dst_file in files:
            yield {
                'basename': 'copy',
                'name': dst_file,
                'file_dep': [src_file],
                'targets': [dst_file],
                'actions': [(self._do_copy, (src_file, dst_file))],
            }

    def _get_tasks_impl(self, level):
        if level == 1:
            yield self._create_tasks(('1', 'dest/1.a'), ('2', 'dest/2.a'), ('dest/2.a', 'dest/2.b'))
        elif level == 2:
            yield self._create_tasks(('dest/1.a', 'dest/1.b'))
        elif level == 3:
            yield self._create_tasks(('1', 'dest/1.c'), ('dest/2.b', 'dest/2.c'))

    def get_tasks(self, level):
        yield {
            'basename': 'copy',
            'name': None,
            'doc': 'Copies modified or non-existing files over',
        }
        yield self._get_tasks_impl(level)

    def get_all_tasks(self):
        yield {
            'basename': 'copy',
            'name': None,
            'doc': 'Copies modified or non-existing files over',
        }
        for level in self.get_task_levels():
            yield self._get_tasks_impl(level)


def main(args=None):
    program = Program()
    return MyDoit(program).run(args)


if __name__ == "__main__":
    try:
        shutil.rmtree('dest', True)
    except:
        pass
    os.mkdir('dest')
    write_content('1', 'bla')
    write_content('2', 'bla')
    sys.exit(main(['run', '-n4']))
