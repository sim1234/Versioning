from _db import Database

from sqlalchemy import create_engine, text
import subprocess

class SQLDatabase(Database):
    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name
        self.engine = create_engine(self.db_path)
    
    def _do_sql(self, sql):
        connection = self.engine.connect()
        result = connection.execute(text(sql))
        return result
    
    def get_all_versions(self):
        sql = "select name, hash, json from %s ORDER BY id" % self.table_name
        r = self._do_sql(sql)
        return map(lambda x: map(lambda y: y.strip(), x), r)
    
    def get_latest_version(self):
        try:
            sql = "select name, hash, json from %s ORDER BY id DESC LIMIT 1" % self.table_name
            r = list(self._do_sql(sql))[0]
            return map(lambda y: y.strip(), r)
        except Exception:
            return ['None', None, '[{}, {}]']

    def get_version(self, name):
        try:
            sql = "select name, hash, json from %s WHERE name='%s' LIMIT 1" % (self.table_name, name)
            r = list(self._do_sql(sql))[0]
            return map(lambda y: y.strip(), r)
        except Exception:
            raise KeyError()
        
    def new_version(self, name, hash_, json_):
        try:
            git_hash = GitHash().get_git_hash()
        except Exception, e:
            print e
            git_hash = ''
        sql = "INSERT INTO %s (name, hash, json, date, git_hash) VALUES ('%s', '%s', '%s', NOW(), '%s')" % (self.table_name, name, hash_, json_, git_hash)
        return self._do_sql(sql)
    
    def delete_version(self, name):
        try:
            sql = "DELETE FROM %s WHERE id IN (SELECT id FROM %s WHERE name='%s' LIMIT 1)" % (self.table_name, self.table_name, name)
            return self._do_sql(sql)
        except Exception:
            raise KeyError()


class GitHash():
    def call(self, cmd):
        r = cmd + '\n'
        try:
            r += subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            r += e.output
        return r

    def get_git_hash(self):
        return self.call('git rev-parse --verify HEAD')[28:]