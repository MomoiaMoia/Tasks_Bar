from flask.helpers import flash
from werkzeug.utils import redirect
from user_login import User
import pymysql

class DB_Conf():
    """
    :user:数据库用户名
    :password:数据库密码
    :dbname:数据库名
    :host:数据库地址 默认localhost
    :port:端口 默认3306
    """

    def __init__(self,user:str,password:str,dbname:str,host="localhost",port=3306) -> None:
        self.user = user
        self.password = password
        self.dbname = dbname
        self.host = host
        self.port = port


    def connect(self) -> object:
        """
        Connect to database
        无需传入直接调用方法即可
        """
        try:
            db = pymysql.connect(host=self.host,user=self.user,password=self.password,port=self.port,db=self.dbname)
        except:
            raise UserWarning
        return db

    def login_userid(self,cursor) -> tuple:
        self.cursor = cursor
        SQL = 'SELECT `user_id` FROM user_info'
        try:
            self.cursor.execute(SQL)
            data = self.cursor.fetchall()
            pure_data = []
            for t in data:
                for i in t:
                    pure_data.append(i)
            return pure_data
        except:
            raise UserWarning

    def user_info(self,cursor,user_id):
        self.cursor = cursor
        self.user_id = user_id
        SQL = 'SELECT * FROM user_info WHERE `user_id`=%s'
        try:
            self.cursor.execute(SQL,user_id)
            info = self.cursor.fetchone()
            self.user_pwd = info[2]
            self.user_name = info[3]
            self.user_type = info[4]
            self.org_id = info[5]
            self.org_name = info[6]
            self.org_notice = info[7]
            self.user = User(self.user_id,self.user_pwd,self.user_name,self.user_type,self.org_id,self.org_name,self.org_notice)
            return self.user
        except:
            return None

    def insert_task_info(self,cursor,dbobj,org_id,title,date,notes,path,task_name):
        self.cursor = cursor
        SQL = 'INSERT INTO `org_tasks`(`org_id`,`task_title`,`task_date`,`task_notes`,`task_file_path`,`full_task_name`) VALUES(%s,%s,%s,%s,%s,%s)'
        try:
            self.cursor.execute(SQL,(org_id,title,date,notes,path,task_name))
            dbobj.commit()
            return 'Task release success.'
        except:
            dbobj.rollback()
            raise UserWarning

    def query_org_task(self,cursor,org_id):
        self.cursor = cursor
        SQL = "SELECT full_task_name,task_index,task_file_path FROM org_tasks WHERE `org_id`=%s"
        try:
            self.cursor.execute(SQL,org_id)
            info = self.cursor.fetchall()
            return info
        except:
            raise UserWarning