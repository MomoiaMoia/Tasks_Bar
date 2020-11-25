import configparser
from db_models import DB_Conf


#————————————————————————————————————————————————————————
#                     读取配置文件                       |
#————————————————————————————————————————————————————————
#数据库配置信息
cf = configparser.ConfigParser()
cf.read(r"G:\Code_project\Html_Web_Design\config.conf", encoding='utf-8')
port = int(cf.get('db','db_port'))
host = cf.get('db','db_host')
user = cf.get('db','db_user')
pwd = cf.get('db','db_pwd')
db = cf.get('db','db_database')
#配置文件路径
path = cf.get('file','config_file_path')
#————————————————————————————————————————————————————————
#————————————————————————————————————————————————————————
#                      数据库管理                        |
#————————————————————————————————————————————————————————
DB = DB_Conf(user,pwd,db,host=host,port=port)
#实例化类对象 传入用户名，密码，数据库名
database = DB.connect()
db_cursor = database.cursor()  #选取游标
#————————————————————————————————————————————————————————

# SQL = 'SELECT user_id FROM user_info'
# db_cursor.execute(SQL)
# data = db_cursor.fetchall()
# pure_data = []
# for t in data:
#     for i in t:
#         pure_data.append(i)

user_id = 1729130135
# SQL = 'SELECT `user_pwd` FROM user_info WHERE `user_id`=%s'
# db_cursor.execute(SQL,(user_id))
# data = db_cursor.fetchone()
# pure_data = []
# for t in data:
#     print(t)
#     for i in t:
#         pure_data.append(i)
# print(data)

pwd = DB.login_passwd(db_cursor,user_id)
print(pwd)