import os

from py_versioning.fs import FSVersionerEngine, FSVersionCommander
from py_versioning.storage.sql_db import SQLDatabase

from py_versioning.db import DBVersionCommander
from py_versioning.combined import CombinedCommander

PROJECT = os.path.abspath(os.path.dirname(__file__))

fs_engine = FSVersionerEngine(PROJECT, True, [r'^.*py$'], [r'^.*\\storage\\.*$',])
fs_database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'py_versioning_fs_version')
fs_versioner = FSVersionCommander(fs_database, fs_engine, '.version')

#print fs_versioner.get_version()


db_versioner = DBVersionCommander('postgresql://postgres:postgres@localhost/postgres2',
                                  'postgresql://postgres:postgres@localhost/versioning', 
                                  'py_versioning_db_version')


if __name__ == '__main__':
    c = CombinedCommander(fs = fs_versioner, db = db_versioner)
    c.execute_from_command_line()
    
