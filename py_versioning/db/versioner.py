import sys


from .engine import CheckVersion, CreateVersion

class DBVersioner(object):
    def __init__(self, versioned_db_path, storage_db_path, table_name, versioning_file_path = ".db_version"):
        self.versioned_db_path = versioned_db_path
        self.storage_db_path = storage_db_path
        self.table_name = table_name
        self.versioning_file_path = versioning_file_path
    
    def _current_version(self):
        try:
            f = open(self.versioning_file_path, 'r')
            name = f.read()
            f.close()
        except IOError:
            name = '0.0.0'
        return name
    
    def set_version(self, name):
        f = open(self.versioning_file_path, 'w')
        f.write(name)
        f.close()
    
    def check_version(self):
        v = CheckVersion(self.versioned_db_path, self.storage_db_path, self.table_name)
        self.set_version(v.version)
        return v.version
    
    def create_version(self):
        v = CreateVersion(self.versioned_db_path, self.storage_db_path, self.table_name)
        self.set_version(v.version)
        return v.version
        
        

class DBVersionCommander(DBVersioner):
    
    def execute_command(self, parts):
        HELP = "Available commands are: check; create."
        if parts == []:
            parts = ['check']
        
        cmm = parts[0]
        if cmm == 'check':
            version = self.check_version()
            print(version)
            self.setIni('VERSION', 'db', version)
        elif cmm == 'create':
            version = self.create_version()
            print(version)
            self.setIni('VERSION', 'db', version)
        
        else:
            print "Error: '%s' - No such command!" % cmm
            print HELP
                    

    def execute_from_command_line(self):
        self.execute_command(sys.argv[1:])

    def setIni(self, section, name, value):
        try:
            from ConfigParser import ConfigParser
            if value:
                parser = ConfigParser()
                parser.read('config.cfg')
                parser.set(section, name, value)
                with open('config.cfg', 'wb') as configfile:
                    parser.write(configfile)
        except (Exception):
            pass



