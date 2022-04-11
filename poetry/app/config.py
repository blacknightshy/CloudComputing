import os
from urllib import parse

DEBUG = False

# password = parse.quote('Booway@2020')
db_host = 'sh-cynosdbmysql-grp-inpb6obi.sql.tencentcdb.com'
db_name = 'root'
db_password = parse.quote('Root1234')
db_port = 29170

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+db_name+':'+db_password+'@'+str(db_host)+':'+str(db_port)+'/poetry'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/package'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-$-%#'
TOKEN_TIME = 3600*2