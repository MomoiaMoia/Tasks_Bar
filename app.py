from flask import Flask,render_template,redirect,flash
from form import LoginForm, NewTaskForm, ResetPasswdForm ,UploadForm
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import uuid
import os
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
data_file_path = cf.get('file','data_file_path')
# # #配置文件路径
# path = cf.get('file','config_file_path')
#————————————————————————————————————————————————————————
#————————————————————————————————————————————————————————
#                      数据库管理                        |
#————————————————————————————————————————————————————————
DB = DB_Conf(user,pwd,db,host=host,port=port)
#实例化类对象 传入用户名，密码，数据库名
database = DB.connect()
db_cursor = database.cursor()  #选取游标
#————————————————————————————————————————————————————————


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH']=30 * 1024 * 1024

# 实例登录模组
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login_page'
login_manager.init_app(app)
# 实例密码
app.secret_key="secret string"


#主页
@app.route('/')
@app.route('/index')
def index_page():
    return render_template('index.html')


#上传页面
@app.route('/upload',methods=['GET','POST'])
@login_required
def upload_page():
    #获取组织任务
    select_tasks = DB.query_org_task(db_cursor,current_user.org_id)
    #创建任务字典和任务文件路径
    task_list = {}
    task_path_list = {}
    for task_info in select_tasks:
        task_list[task_info[0]] = task_info[1]
        task_path_list[task_info[1]] = task_info[2]
    #实例上传表单
    form = UploadForm(task_list=task_list)
    #创建表单交互
    if form.validate_on_submit():
        #获取表单数据
        file = form.upload_file.data
        select_tasks = form.select_task.data
        msg_task = form.msg_task.data        #暂时用不到这个
        #构造文件路径和存储文件
        if int(select_tasks) in list(task_path_list.keys()):
            file_path = task_path_list[int(select_tasks)] + f"\{str(current_user.id)}_{str(current_user.user_name)}_{str(uuid.uuid4().hex)}_{str(file.filename)}" 
            file.save(file_path)
            flash('Upload success')
            #重定向
            return redirect('/upload')
        #重定向
        return redirect('/mine')
    return render_template("upload.html", form=form, task_list=task_list)


#复查界面
@login_required
@app.route('/check')
def check_page():
    return render_template("check.html")


#个人界面
@app.route('/mine')
@login_required
def mine_page():
    return render_template("mine.html")


#帮助文档
@app.route('/doc')
def doc_page():
    return render_template("doc.html")


#用户引导，请勿修改
@login_manager.user_loader
def load_user(user_id):
    user = DB.user_info(db_cursor,user_id)
    return user


#登录界面
@app.route('/login', methods=['GET','POST'])
def login_page():
    #实例化登录表单
    form = LoginForm()
    if form.validate_on_submit():
        #获取数据
        userid = form.userid.data
        passwd = form.passwd.data
        bool_v = form.switch.data
        #判断 用户是否存在
        if DB.user_info(db_cursor,userid) is not None: 
            user = DB.user_info(db_cursor,userid)
            #用户认证
            if user.is_authenticated(passwd):
                #用户登录
                login_user(user, remember=bool_v)
                return redirect('/mine')
            else:
                flash('Invalid ID or password. Try again.')
                return redirect('/login')
        else:
            flash('Invalid ID or password. Try again.')
            return redirect('/login')
    return render_template("login.html", form=form)


@app.route('/new_task', methods=['GET','POST'])
@login_required
def new_task():
    #实例化新任务表单
    form = NewTaskForm()
    #构造用户
    user = DB.user_info(db_cursor,current_user.id)
    #管理员认证
    if user.is_authenticated_admin(current_user.user_type):
        #判定表单
        if form.validate_on_submit():
            #获取表单数据
            title = form.task_title.data
            date = form.task_date.data
            notes = form.task_notes.data
            #构造任务名
            task_name = (f"{str(date)}_{str(title)}_{str(current_user.org_name)}")
            #构造任务路径
            path = (fr"{str(data_file_path)}\{str(current_user.org_id)}\{str(date)}_{str(title)}_{str(current_user.org_name)}_{str(uuid.uuid4().hex)}")
            os.makedirs(path)
            #数据库写入
            flash(DB.insert_task_info(db_cursor,database,current_user.org_id,title,date,notes,path,task_name))
            #重定向
            return redirect('/upload')
    #管理员认证失败
    else:
        flash('Not authorized')
        return redirect('/mine')
    return render_template("new_task.html", form=form)


#重置密码界面
@app.route('/reset', methods=['GET','POST'])
@login_required
def reset_passwd_page():
    #实例化重置密码表单
    form = ResetPasswdForm()
    #实例化临时用户信息
    user_temp = DB.user_info(db_cursor,current_user.id)
    #判定表单提交
    if form.validate_on_submit():
        #获取数据
        passwd = form.passwd.data
        new_passwd = form.new_passwd.data
        new_passwd_repeat = form.new_passwd_repeat.data
        #判断用户认证
        if user_temp.is_authenticated(passwd):
            #判断新密码是否相同
            if str(new_passwd).strip() == str(new_passwd_repeat).strip(): 
                flash(DB.reset_passwd(db_cursor,database,user_temp.id,new_passwd_repeat))
                return redirect('/login')
            else:
                flash('The two passwords do not match. Try again.')
                return redirect('/reset')
        else:
            flash('Incorrect old password. Try again.')
            return redirect('/reset')
    return render_template("reset.html", form=form)


#登出
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/index')

if __name__=="__main__":
    app.run(debug=True)