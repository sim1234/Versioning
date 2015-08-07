PyVersioning
Required
python 2.7
SQLAlchemy 

How it works?
This program can create and manage version of databases and  file system.

In file example.py you must set:
Database and table, where program keeps data about file system, f.e:
fs_database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'fs_version')

Database, which we want to versioning and db, where program keeps data about versionised fb, f.e: 
db_versioner = DBVersionCommander('postgresql://postgres:postgres@localhost/vers_test3', 'postgresql://postgres:postgres@localhost/vers_control')

command: python example.py db, python example.py db check
action: Check version db. 

command: python example.py db create
action: Create new version db, if changes will be detected.


PyVersioning
Wymagania: 
python 2.7
SQLAlchemy 

Dzia³anie:
Program pozwala na wersjonowanie schematów baz danych oraz
systemu plików. 

W pliku example.py nale¿y odpowiednie œcie¿ki:

Œcie¿ka do bazy danych oraz nazwa kolumny w której bêdziemy trzymaæ dane odnoœnie plików, np:
fs_database = SQLDatabase('postgresql://postgres:postgres@localhost/versioning', 'fs_version')

Pierwsza œcie¿ka jest bazy któr¹ chcemy wersjonowaæ, druga do bazy w której bêdziemy trzyamæ dane.

db_versioner = DBVersionCommander('postgresql://postgres:postgres@localhost/vers_test3', 'postgresql://postgres:postgres@localhost/vers_control')

komenda: python example.py db, python example.py db check
dzia³anie: sprawdza wersje bazy 

komenda: python example.py db create
dzia³anie: tworzy now¹ wersje bazy je¿eli wykryje zmiany
