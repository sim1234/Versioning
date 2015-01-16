#from ConfigParser import ConfigParser
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy import inspect

import json

class CreateVersion():
    def __init__(self, versioned_db_path, storage_db_path):
        self.path1 = versioned_db_path #self.get_ini("DB", "path1")
        self.path2 = storage_db_path #self.get_ini("DB", "path4")
        self.create_engine()
        last_version = self.get_latest_version()
        if last_version:
            new_list = self.test3()
            new_json = json.dumps(new_list)
            print last_version
            old_list = eval(last_version[3])

            #print old_list, 'asd'
            if last_version[3] == new_json:
                print 'No changes detected in db!'
                print 'path: %s' % self.path1
            else:
                column, row = self.compareVersion(new_list, old_list)
                new_version = last_version[1].split('.')
                if len(column) > 0:
                    new_version[0] = str(int(new_version[0]) + 1)
                    new_version[1] = str(0)
                else:
                    new_version[1] = str(int(new_version[1]) + 1)
                new_version_str = new_version[0] + '.' + new_version[1]
                if column:
                    print 'Changes tables'
                for c in column:
                    #print c[0], c[1]
                    print c
                if row:
                    print 'Changes columns'
                for r in row:
                    #print r[0], r[1], r[2]
                    print r
                
                self.insertNewVersion(new_json, new_version_str)
                #print 'Wersja bazy danych zmienila sie i zostala dodana do DB.\n %s' % new_version_str 
                print 'Created new db version %s' % new_version_str 
        else:
            self.create_new_version()
            print 'Version 0.0 was created.'
        #m = MetaData
        #m.reflect(m, sbind = self.engine)
        #self.test()
        #self.test2()
        #self.test3()
        #self.test4()

    def compareVersion(self, olds, news):
        diff_tables = []
        diff_columns = []
        for new in news:
            for i, jj in new.items():
                #try:
                    #print new, i, jj
                    nn = self.find_in_list_with_dic(olds, i)
                    if nn:
                        for n in nn:
                            if not n in jj:
                                diff_columns.append(('+++',unicode(i),n))
                        for j in jj:
                            if not j in nn:
                                diff_columns.append(('---',unicode(i),j))
                    else:
                        diff_tables.append(('---', new))
        
        for old in olds:
            for i, jj in old.items():
                    nn = self.find_in_list_with_dic(news, i)
                    if nn:
                        pass
                        '''
                        for n in nn:
                            if not n in jj:
                                diff_columns.append(('---',unicode(i),n))
                        for j in jj:
                            if not j in nn:
                                diff_columns.append(('+++',unicode(i),j))
                        '''
                    else:
                        diff_tables.append(('+++', old))
        
        dt = []
        dc = []
        for t in diff_tables:
            if not t in dt:
                dt.append(t)
        for c in diff_columns:
            if not c in dt:
                dc.append(c)
        return dt, dc
        
        
    def find_in_list_with_dic(self, elements_dic, element):
        for e in elements_dic:
            for i, j in e.items():
                if i == element:
                    return e[i]
                    return True
        return False

    #def get_ini(self, section, name):
    #    try:
    #        parser = ConfigParser()
    #        parser.read('config.cfg')
    #        return parser.get(section, name)
    #    except Exception, e:
    #        #print e
    #        return False
        
    def create_engine(self):
        self.engine = create_engine(self.path1)
        self.engine2 = create_engine(self.path2)
        
    def do_sql(self, q):
        connection = self.engine.connect()
        result = connection.execute(text(q))
        return result
    
    def do_sql2(self, q):
        connection = self.engine2.connect()
        result = connection.execute(text(q))
        return result
    
    def get_versions(self):
        q = "select * from control ORDER BY id"
        return self.do_sql2(q)
    
    def get_latest_version(self):
        row = self.get_versions()
        latest = []
        for r in row:
            latest = r
        if latest:
            return latest
        else:
            return False
    
    def create_new_version(self, new_json = False):
        if not new_json:
            aaa = self.test3()
            json_db = json.dumps(aaa)
            #print json_db
            version = '0.1'
        self.insertNewVersion(json_db, version)
        

    def insertNewVersion(self, json_db, version):
        q = """INSERT INTO control 
                (version, date ,json_db ) VALUES 
                ('%s', NOW(), '%s')""" %(version, json_db)
        self.do_sql2(q)
            
        

    def test(self):
        q = "select * from register_app_pod"
        row = self.do_sql(q)
        for i in row:
            pass
            
    def test2(self):
        for table in self.m.tables.values():
            ##print table.name
            for column in table.c:
                #print column.name
                pass
            
    def test3(self):
        inspector = inspect(self.engine)
        
        table_list = []
        for table_name in inspector.get_table_names():
            ##print('table name %s' %table_name)
            table_dic = {}
            columns = []
            
            for column in inspector.get_columns(table_name):
                ##print("Column: %s" % column['name'])
                columns.append(column['name'])
            det_str = table_name +'_details'
            details =  self.test4(table_name)

            table_dic[det_str] = details
            table_dic[table_name] = columns
            table_list.append(table_dic)
            
            
        return table_list
    
    def test4(self, name):
        meta = MetaData()
        meta.bind = self.engine
        meta.reflect()
        datatable = meta.tables[name]
        #for c in datatable.columns:
        #    #print dir(c)
        #    ##print c.params()
        # [str(c.params) for c in datatable.columns]
        return [str(c.type) for c in datatable.columns]

class CheckVersion():
    def __init__(self, versioned_db_path, storage_db_path):
        self.path1 = versioned_db_path #self.get_ini("DB", "path1")
        self.path2 = storage_db_path #self.get_ini("DB", "path4")
        
        self.create_engines()
        versions = self.get_versions()
        aaa = self.test3()
        my_json = json.dumps(aaa)
        #print aaa
        #print my_json
        for v in versions:
            
            if v[3] == my_json:
                print v[1]
                break

    #def get_ini(self, section, name):
    #    try:
    #        parser = ConfigParser()
    #        parser.read('config.cfg')
    #        return parser.get(section, name)
    #    except Exception, e:
    #        #print e
    #        return False
        
    def create_engines(self):
        #self.engine = create_engine(self.get_ini("DB", "path1"))
        #self.engine2 = create_engine(self.get_ini("DB", "path4"))
        self.engine = create_engine(self.path1)
        self.engine2 = create_engine(self.path2)
        
    def do_sql(self, q):
        connection = self.engine.connect()
        result = connection.execute(text(q))
        return result
    
    def do_sql2(self, q):
        connection = self.engine2.connect()
        result = connection.execute(text(q))
        return result
    
    def get_versions(self):
        q = "select * from control ORDER BY -id"
        return self.do_sql2(q)
    
    def test3(self):
        inspector = inspect(self.engine)
        table_list = []
        for table_name in inspector.get_table_names():
            table_dic = {}
            columns = []

            for column in inspector.get_columns(table_name):
                columns.append(column['name'])
            det_str = table_name +'_details'
            details =  self.test4(table_name)
            table_dic[det_str] = details
            table_dic[table_name] = columns
            table_list.append(table_dic)
        return table_list
    
    def test4(self, name):
        meta = MetaData()
        meta.bind = self.engine
        meta.reflect()
        datatable = meta.tables[name]
        #for c in datatable.columns:
        #    #print dir(c)
        #    ##print c.params()
        # [str(c.params) for c in datatable.columns]
        return [str(c.type) for c in datatable.columns]

#create = CreateVersion()
#heck = CheckVersion()
#db = DataBase(2)
