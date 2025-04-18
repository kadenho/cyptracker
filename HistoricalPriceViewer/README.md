# Crypto App

## Author
Kaden Ho

## Installation and Running

### Installation

#### in MYSQL
Run the command: create database [NAME];

#### in PyCharm
#### In main.py:
Install kivy, matplotlib, and kivy_garden, and sqlalchemy packages (compatible with python version 3.7-3.10)

##### On line 80 of main.py:
Replace 'crypto' with the name of the database you created in quotation marks. \
Replace 'root' with your username in quotation marks (you will likely leave this as 'root'). \
Replace 'sqlpassword' with your password in quotation marks.

##### On line 83 of crypto_install.py:
Repeat the steps used on line 80 of main.py. \
Run crypto_installer.py. \
Never run the installer more than once.

##### Troubleshooting

If the installer is ran more than once run the command 'drop database [NAME]; create database [NAME]; use [NAME];' in the SQL terminal and run the installer again.
## Files

### App: 
The app utilizes the main.py and crypto.kv files. \
The app can be executed by running the main.py file.

### Installer:
The installer utilizes the crypto_installer.py and crypto.py files. \
The installer can be executed by running the crypto_installer.py file.

## Status

### Completeness
The historical price viewer app is a fully functioning prototype, but relies on preinstalled data and is not connected to the CoinGecko api.
### Correctness
There are no known errors at this time.

## References

### Kivy
Referenced [kivy documentation](https://kivy.org/doc/stable/api-kivy.html) for kivy support.

### SQL Alchemy
Referenced orm lab for installer set up.\
Referenced [SQLalchemy documentation](https://docs.sqlalchemy.org/en/14/orm/quickstart.html) for sql support.

### Matplotlib
Referenced [Matplotlib documentation](https://matplotlib.org/stable/users/explain/quick_start.html) for matplotlib support \
Referenced [Codemy.com's video](https://www.youtube.com/watch?v=83C4tl8scoY) for support importing plot onto Kivy.

### Markdown
referenced [Markdown guide](https://www.markdownguide.org/cheat-sheet/) for README.md.