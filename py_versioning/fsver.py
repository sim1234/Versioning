import sys
import os
import re
import json
import hashlib

def safe_list_get(l, idx, default = None):
    try:
        return l[idx]
    except IndexError:
        return default

def md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def md5_file(f, block_size = 2**10):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()


class FSVersioner(object):
    def __init__(self, path, ignore_empty_folders = True, allow_regs = ['.*'], ignore_regs = []):
        self.path = unicode(path)
        self.ignore_empty_folders = ignore_empty_folders
        self.allow_regs = allow_regs
        self.ignore_regs = ignore_regs

    def process_folder(self, path, name = u'.'):
        path = unicode(path)
        all_dirs, all_files = self.get_dirs_files(path)
        dirs = {}
        files = {}
        for dir_name in all_dirs:
            dir = self.process_folder(os.path.join(path, dir_name), dir_name)
            if dir:
                dirs[dir_name] = dir
        for file_name in all_files:
            files[file_name] = self.hash_file(os.path.join(path, file_name))
        if self.ignore_empty_folders and (not files) and (not dirs):
            return None
        #print path, dirs
        return [dirs, files]
    
    def file_ok(self, path):
        for reg in self.allow_regs:
            if re.match(reg, path):
                for reg2 in self.ignore_regs:
                    if re.match(reg2, path):
                        return False
                return True
        return False
    
    def get_dirs_files(self, path):
        _, all_dirs, all_files = os.walk(path).next()
        files = []
        for f in all_files:
            if self.file_ok(os.path.join(path, f)):
                files.append(f)
        return all_dirs, files
    
    def hash_file(self, path):
        f = open(path, 'rb')
        r = md5_file(f, 2**12)
        f.close()
        return r
    
    def dump_json(self, pretty = False):
        data = self.process_folder(self.path)
        js = json.dumps(data, sort_keys = True, separators=(',', ':'))
        hash = md5(js)
        if pretty:
            js_p = json.dumps(data, sort_keys = True, indent = 2, separators=(',', ': '))
            return hash, js_p
        return hash, js
    
    
    def compare_files(self, files1, files2):
        created = []
        not_changed = []
        changed = []
        deleted = []
        for filename, hash in files2.iteritems():
            if files1.has_key(filename):
                if files1[filename] == hash:
                    not_changed.append(filename)
                else:
                    changed.append(filename)
            else:
                created.append(filename)
        
        for filename, hash in files1.iteritems():
            if not files2.has_key(filename):
                deleted.append(filename)
                
        return created, not_changed, changed, deleted
    
    def compare_dirs(self, dir1, dir2, path = u'.'):
        created = []
        not_changed = []
        changed = []
        deleted = []
        
        for dir_name, rdir1 in dir1[0].iteritems():
            rdir2 = dir2[0].get(dir_name, [{}, {}])
            cr, nc, ch, dl = self.compare_dirs(rdir1, rdir2, os.path.join(path, dir_name))
            created.extend(cr)
            not_changed.extend(nc)
            changed.extend(ch)
            deleted.extend(dl)
        
        cr, nc, ch, dl = self.compare_files(dir1[1], dir2[1])
        created.extend(map(lambda x: os.path.join(path, x), cr))
        not_changed.extend(map(lambda x: os.path.join(path, x), nc))
        changed.extend(map(lambda x: os.path.join(path, x), ch))
        deleted.extend(map(lambda x: os.path.join(path, x), dl))
        
        return created, not_changed, changed, deleted 
    
    
        
        
class FileJsonDatabase(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self._data = self._load(self.file_name)
        self.config = self._data['config']
        self.datasets = self._data['datasets']
    
    def _load(self, file_name):
        try:
            f = open(file_name, 'r')
        except IOError:
            self._init_db(file_name)
            f = open(file_name, 'r')
        data = json.load(f)
        f.close()
        return data
    
    def _init_db(self, file_name):
        self._dump(file_name, {'config': {}, 'datasets':{}})
        
    def _dump(self, file_name, data):
        f = open(file_name, 'w')
        json.dump(data, f, separators = (',', ':'))
        f.close()
        
        
    def save(self):
        self._dump(self.file_name, self._data)
    
    def get_dataset(self, name, default = []):
        if not self.datasets.has_key(name):
            self.datasets[name] = default
        return self.datasets[name]
    
    def get_config(self, name, default = None):
        if not self.config.has_key(name):
            self.config[name] = default
        return self.config[name]
    
    def set_config(self, name, value):
        self.config[name] = value
        
        
class Versioner(object):
    DEFAULT_FSVC = {'path' : '.', 'ignore_empty_folders' : False, 'allow_regs': ['.*'], 'ignore_regs': []}
    DEFAULT_DBVC = {}  
    
    def __init__(self, versioning_file_name = 'version.info'):
        self.db = FileJsonDatabase(versioning_file_name)
        self.init_fsv()
        self.init_dbv()
    
    
    def init_fsv(self):
        self.fs_ve = self.db.get_config('file_system_versioning_enabled', False)
        self.fs_db = self.db.get_dataset('file_system', [])
        self.fs_versioner = None
        config = self.db.get_config('file_system_versioning_config', self.DEFAULT_FSVC)
        if self.fs_ve:
            self.fs_versioner = FSVersioner(**config)
    
    def init_dbv(self):
        self.db_ve = self.db.get_config('database_versioning_enabled', False)
        self.db_db = self.db.get_dataset('database', [])
        self.db_versioner = None
        config = self.db.get_config('database_versioning_config', self.DEFAULT_DBVC)
        if self.db_ve:
            pass
            #self.db_versioner = DBVersioner(**config)
        
    def save(self):
        return self.db.save()
    
    
    def fs_current_version(self):
        try:
            return self.fs_db[-1]
        except IndexError:
            return ["None", None, None]
    
    def fs_actual_version(self):
        hash, js = self.fs_versioner.dump_json(pretty = False)
        return ['--ACTUAL--', hash, js]
    
    def fs_version_list(self):
        current = self.fs_current_version()
        actual = self.fs_actual_version()
        if current[1]:
            if current[1] == actual[1]:
                return self.fs_db
            return self.fs_db + [actual]
        return [actual]
    
    def fs_changed(self):
        current = self.fs_current_version()
        actual = self.fs_actual_version()
        return current[1] != actual[1]
    
    def fs_get_version(self, ignore_modified = False):
        current = self.fs_current_version()
        actual = self.fs_actual_version()
        if (not ignore_modified) and current[1] != actual[1]:
            return "%s+" % current[0]
        return current[0]
        
    
    def fs_new_version(self, name, hash, js):
        self.fs_db.append([name, hash, js])
        
    def fs_del_version(self, name = None, hash = None):
        for i, data in enumerate(self.fs_db):
            if name == data[0] or hash == data[1]:
                return self.fs_db.pop(i)
        raise KeyError('Version not found')
    
    def fs_find_version(self, name = None, hash = None):
        if name is None:
            return self.fs_current_version()
        if name == '--ACTUAL--':
            return self.fs_actual_version()
        for data in self.fs_db:
            if name == data[0] or hash == data[1]:
                return data
        raise KeyError('Version not found')



class VersionCommander(Versioner):
    def fs_print_deltas(self, v1_json, v2_json, show_no_change = False):
        v1 = json.loads(v1_json)
        v2 = json.loads(v2_json)
        created, not_changed, changed, deleted = self.fs_versioner.compare_dirs(v1, v2)
        for f in created:
            print '+++', f.encode('ascii','replace')
        for f in changed:
            print '@@@', f.encode('ascii','replace')
        for f in deleted:
            print '---', f.encode('ascii','replace')
        if show_no_change:
            for f in not_changed:
                print '===', f.encode('ascii','replace')
    
    def execute_fs_command(self, parts):
        HELP = "Available commands are: enable; disable; current; actual; changed; list; new <name>; del <name>; diff [<name1> <name2>]."
        if parts == []:
            #print HELP
            #return
            print self.fs_get_version()
            parts = ['diff']
        
        verbose = '-v' in parts
        cmm = parts[0]
        if cmm == 'enable':
            self.db.set_config('file_system_versioning_enabled', True)
            self.save()
            print "Enabled file system versioning."
        elif cmm == 'disable':
            self.db.set_config('file_system_versioning_enabled', False)
            self.save()
            print "Disabled file system versioning."
            
        elif cmm == 'current':
            name, hash, js = self.fs_current_version()
            print name, hash
            if verbose:
                print js
        elif cmm == 'actual':
            name, hash, js = self.fs_actual_version()
            print name, hash
            if verbose:
                print js
        elif cmm == 'changed':
            print self.fs_changed()
                
        elif cmm == 'list':
            for name, hash, js in self.fs_version_list():
                if verbose:
                    print name.ljust(20, ' '), hash, js
                else:
                    print name.ljust(20, ' '), hash
        elif cmm == 'new':
            name = safe_list_get(parts, 1, None)
            current = self.fs_current_version()
            actual = self.fs_actual_version()
            if current[1] != actual[1]:
                try:
                    self.fs_find_version(name = name)
                    print "Error: Version named '%s' already exists!" % name
                except KeyError:
                    self.fs_new_version(name, actual[1], actual[2])
                    self.save()
                    print "Created new version: '%s' : %s." % (name, actual[1])
                    if verbose:
                        print js
            else:
                print "Error: No changes detected!"
        elif cmm == 'del':
            name = safe_list_get(parts, 1, '')
            try:
                name, hash, js = self.fs_del_version(name = name)
                self.save()
                print "Deleted version named '%s' : %s." % (name, hash)
                if verbose:
                    print js
            except KeyError:
                print "Error: Version named '%s' not found!" % name
        
        elif cmm == 'diff':
            name1 = safe_list_get(parts, 1, None)
            name2 = safe_list_get(parts, 2, '--ACTUAL--')
            try:
                v1 = self.fs_find_version(name = name1)
                v2 = self.fs_find_version(name = name2)
            except KeyError:
                print "Error: Version named '%s' or '%s' not found!" % (name1, name2)
                return
            print "Comparing '%s' to '%s':" % (v1[0], v2[0])
            self.fs_print_deltas(v1[2], v2[2], verbose)
        
        else:
            print "Error: '%s' - No such command!" % cmm
            print HELP
                    
                    
                    
    def execute_db_command(self, ):
        HELP = "Available commands are: enable; disable."
        if parts == []:
            print HELP
            return
        
        cmm = parts[0]
        if cmm == 'enable':
            self.db.set_config('file_system_versioning_enabled', True)
            self.save()
            print "Enabled database versioning."
        elif cmm == 'disable':
            self.db.set_config('file_system_versioning_enabled', False)
            self.save()
            print "Disabled database versioning."
            
            #TODO: Rozwinac o prace Jarka
            
        else:
            print "Error: '%s' - No such command!" % cmm
            print HELP
    
    def execute_command(self, parts):
        if parts == []:
            print "TODO: STATUS ALL"
        else:
            mod = parts[0]
            if mod == 'fs':
                if self.fs_ve or safe_list_get(parts, 1, None) == 'enable':
                    self.execute_fs_command(parts[1:])
                else:
                    print "Error: File system versioning is disabled!"
            elif mod == 'db' or safe_list_get(parts, 1, None) == 'enable':
                if self.db_ve:
                    self.execute_db_command(parts[1:])
                else:
                    print "Error: Database versioning is disabled!"
            else:
                print "Error: '%s' - No such option!" % mod
                print "Available options are: fs; db."
    
    

def execute_from_command_line():
    VersionCommander().execute_command(sys.argv[1:])


if __name__ == "__main__":
    execute_from_command_line()
