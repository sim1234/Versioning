import os

from py_versioning.fs import FSVersionerEngine, FSVersionCommander
from py_versioning.storage.sql_db import SQLDatabase
#from py_versioning.storage.json_db import FileJsonDatabase

from py_versioning.db import DBVersionCommander
from py_versioning.combined import CombinedCommander

PROJECT = os.path.abspath(os.path.dirname(__file__))

fs_engine = FSVersionerEngine(PROJECT, True, [r'^.*py$'], [r'^.*\\storage\\.*$',])
fs_database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'fs_version')
#database = FileJsonDatabase(os.path.join(PROJECT, 'version.json'))
fs_versioner = FSVersionCommander(fs_database, fs_engine, '.version')

fs_get_version = fs_versioner.get_version
fs_version = fs_get_version()


db_versioner = DBVersionCommander('postgresql://postgres:postgres@localhost/postgres2', 'postgresql://postgres:postgres@localhost/vers_control')


if __name__ == '__main__':
    c = CombinedCommander(fs = fs_versioner, db = db_versioner)
    c.execute_from_command_line()
    
