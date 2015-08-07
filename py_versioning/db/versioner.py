import sys


from .engine import CheckVersion, CreateVersion

class DBVersioner(object):
    def __init__(self, versioned_db_path, storage_db_path, table_name):
        self.versioned_db_path = versioned_db_path
        self.storage_db_path = storage_db_path
        self.table_name = table_name
    
    
    def check_version(self):
        return CheckVersion(self.versioned_db_path, self.storage_db_path, self.table_name).version
    
    def create_version(self):
        return CreateVersion(self.versioned_db_path, self.storage_db_path, self.table_name).version
        
        

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
        except ImportError:
            pass



