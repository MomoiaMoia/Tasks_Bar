from user_login import User
from db_models import DB_Conf
import configparser

#————————————————————————————————————————————————————————
#                     读取配置文件                       |
#————————————————————————————————————————————————————————
#数据库配置信息
cf = configparser.ConfigParser()
cf.read(r"G:\Code_project\Html_Web_Design\config.conf", encoding='utf-8')
port = int(cf.get('db','db_port'))
host = cf.get('db','db_host')
db_user = cf.get('db','db_user')
db_pwd = cf.get('db','db_pwd')
db = cf.get('db','db_database')
#配置文件路径
path = cf.get('file','config_file_path')
#————————————————————————————————————————————————————————
#————————————————————————————————————————————————————————
#                      数据库管理                        |
#————————————————————————————————————————————————————————
DB = DB_Conf(db_user,db_pwd,db,host=host,port=port)
#实例化类对象 传入用户名，密码，数据库名
database = DB.connect()
db_cursor = database.cursor()  #选取游标
#————————————————————————————————————————————————————————

id = 1729130136
pwd = 123456789

user = User(DB.user_info(db_cursor,id))
print(type(user.get_id()))
print(user.is_authenticated(pwd))
print(type(user.load_user()))