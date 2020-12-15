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

    def insert_task_info(self,cursor,dbobj,org_id,title,date,end_date,notes,path,task_name,category):
        self.cursor = cursor
        SQL = 'INSERT INTO `org_tasks`(`org_id`,`task_title`,`task_date`,`task_end_date`,`task_notes`,`task_file_path`,`full_task_name`,`tasks_category`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            self.cursor.execute(SQL,(org_id,title,date,end_date,notes,path,task_name,category))
            dbobj.commit()
            return 'Task release success.'
        except:
            dbobj.rollback()
            raise UserWarning

    def insert_task_check_table_userinfo(self,cursor,dbobj,table_name,col_name,default):
        SQL = f"ALTER TABLE `{table_name}` ADD `{col_name}` VARCHAR(255) DEFAULT '{default}'"
        cursor.execute(SQL)
        dbobj.commit()
        return None

    def query_org_task(self,cursor,org_id,now_time):
        self.cursor = cursor
        SQL = "SELECT full_task_name,task_index,task_file_path FROM org_tasks WHERE `org_id`=%s and `task_end_date` > %s and `task_date` < %s"
        try:
            self.cursor.execute(SQL,(org_id,now_time,now_time))
            info = self.cursor.fetchall()
            return info
        except:
            raise UserWarning

    def query_tasks_date_category(self,cursor,tasks_index):
        SQL = "SELECT org_tasks.task_date,org_tasks.tasks_category FROM org_tasks WHERE org_tasks.task_index = %s"
        try:
            cursor.execute(SQL,tasks_index)
            return cursor.fetchall()
        except:
            raise UserWarning

    def update_tasks_upload_info(self,cursor,dbobj,table_name,task_date,user_id):
        SQL = f"UPDATE `{table_name}` SET `{table_name}`.`{task_date}` = '已完成' WHERE `{table_name}`.user_id = {user_id}"
        try:
            cursor.execute(SQL)
            dbobj.commit()
            return "已完成, 请前往[检查]页面查看"
        except:
            raise UserWarning

    def reset_passwd(self,cursor,dbobj,user,new_password):
        self.cursor = cursor
        SQL = "UPDATE user_info SET user_pwd = %s  WHERE user_id = %s"
        try:
            self.cursor.execute(SQL,(new_password,user))
            dbobj.commit()
            return 'Reset password success.'
        except:
            dbobj.rollback()
            raise UserWarning


    def insert_category_tb(self,cursor,dbobj,org_id,category):
        SQL = "INSERT INTO `org_tasks_category`(`org_id`,`tasks_category`) VALUES(%s,%s)"
        try:
            cursor.execute(SQL,(org_id,category))
            dbobj.commit()
            return True
        except:
            dbobj.rollback()
            raise UserWarning

    def query_category(self,cursor,*org_id):
        SQL = "SELECT * FROM org_tasks_category WHERE org_id = %s"
        try:
            cursor.execute(SQL,(org_id))
            category_temp = self.cursor.fetchall()
            category = {}
            for item in category_temp:
                category_index = item[0]
                category_name = item[2]
                category[category_index] = category_name
            return category
        except:
            raise UserWarning

    def create_category_tb(self,cursor,dbobj,org_id,table_name):
        fk_name = 'fk_' + table_name
        create_tb_SQL = f"CREATE TABLE `{table_name}`(user_id bigint(255) PRIMARY KEY,CONSTRAINT `{fk_name}` FOREIGN KEY(`user_id`) REFERENCES user_info(`user_id`));"
        create_row_SQL = f"INSERT INTO `{table_name}`(user_id) VALUES(%s)"
        get_userid_SQL = 'SELECT `user_id` FROM user_info WHERE org_id=%s'
        try:
            cursor.execute(create_tb_SQL)
            cursor.execute(get_userid_SQL,(org_id))
            user_id_list = cursor.fetchall()
            for id in user_id_list:
                cursor.execute(create_row_SQL,(id))
            dbobj.commit()
            return None
        except:
            dbobj.rollback()
            raise UserWarning

    def query_check_table(self,cursor,table_name):
        SQL_2 = f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = '{table_name}';"
        SQL = f"SELECT `user_info`.user_name,`user_info`.org_id,`{table_name}`.* FROM `user_info` INNER JOIN `{table_name}` ON `user_info`.user_id = `{table_name}`.user_id"
        try:
            cursor.execute(SQL_2)
            table_header = cursor.fetchall()
            cursor.execute(SQL)
            table_info = cursor.fetchall()
            return table_header[1:],table_info
        except:
            pass

    def insert_check_chat_msg(self,cursor,dbobj,user_id,user_name,org_id,msg_category,check_msg,datetime):
        SQL = f"INSERT INTO user_msg(`user_id`,`user_name`,`org_id`,`msg_category`,`msg_info`,`msg_date`) VALUES({user_id},'{user_name}','{org_id}','{msg_category}','{check_msg}','{datetime}')"
        try:
            cursor.execute(SQL)
            dbobj.commit()
            return "🍻"
        except:
            dbobj.rollback()
            raise UserWarning

    def query_check_chat_msg(self,cursor,org_id,msg_category):
        SQL = "SELECT * FROM user_msg WHERE `org_id`=%s and `msg_category`=%s"
        try:
            cursor.execute(SQL,(org_id,msg_category))
            msg = [(msg[2],msg[-2],msg[-1]) for msg in cursor.fetchall()]
            return msg
        except:
            return None