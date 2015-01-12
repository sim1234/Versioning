import os

from py_versioning.fs import FSVersionerEngine, FSVersionCommander
from py_versioning.storage.sql_db import SQLDatabase
#from py_versioning.storage.json_db import FileJsonDatabase

PROJECT = os.path.abspath(os.path.dirname(__file__))
engine = FSVersionerEngine(PROJECT, True, [r'^.*py$'], [r'^.*\\storage\\.*$',])
database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'fs_version')
#database = FileJsonDatabase(os.path.join(PROJECT, 'version.json'))
versioner = FSVersionCommander(database, engine, '.version')

get_version = versioner.get_version
version = get_version()

if __name__ == '__main__':
    versioner.execute_from_command_line()
    
