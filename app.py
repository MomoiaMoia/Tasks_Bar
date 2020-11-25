from flask import Flask,render_template,redirect,flash
from form import LoginForm, NewTaskForm ,UploadForm
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


app = Flask(__name__)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login_page'
login_manager.init_app(app)

app.secret_key="secret string"

@app.route('/')
@app.route('/index')
def index_page():
    return render_template('index.html')


@app.route('/upload',methods=['GET','POST'])
@login_required
def upload_page():
    select_tasks = DB.query_org_task(db_cursor,current_user.org_id)
    task_list = {}
    task_path_list = {}
    for task_info in select_tasks:
        task_list[task_info[0]] = task_info[1]
        task_path_list[task_info[1]] = task_info[2]
    print(task_path_list)
    form = UploadForm(task_list=task_list)
    if form.validate_on_submit():
        file = form.upload_file.data
        select_tasks = form.select_task.data
        msg_task = form.msg_task.data
        if int(select_tasks) in list(task_path_list.keys()):
            file_path = task_path_list[int(select_tasks)] + f"\{str(current_user.id)}_{str(current_user.user_name)}_{str(file.filename)}" 
            file.save(file_path)
            flash('Upload success')
            return redirect('/upload')
        return redirect('/mine')
    print(form.errors)
    return render_template("upload.html", form=form, task_list=task_list)


@login_required
@app.route('/check')
def check_page():
    return render_template("check.html")


@app.route('/mine')
@login_required
def mine_page():
    return render_template("mine.html")


@app.route('/doc')
def doc_page():
    return render_template("doc.html")


@login_manager.user_loader
def load_user(user_id):
    user = DB.user_info(db_cursor,user_id)
    return user


@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        userid = form.userid.data
        passwd = form.passwd.data
        bool_v = form.switch.data
        if DB.user_info(db_cursor,userid) is not None: 
            user = DB.user_info(db_cursor,userid)
            if user.is_authenticated(passwd):
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
    form = NewTaskForm()
    user = DB.user_info(db_cursor,current_user.id)
    if user.is_authenticated_admin(current_user.user_type):
        if form.validate_on_submit():
            title = form.task_title.data
            date = form.task_date.data
            notes = form.task_notes.data
            task_name = (f"{str(date)}_{str(title)}_{str(current_user.org_name)}")
            path = (fr"G:\Code_project\Html_Web_Design\Database\upload_file\{str(date)}_{str(title)}_{str(current_user.org_name)}_{str(uuid.uuid4().hex)}")
            print(current_user.org_id,title,date,notes,path)
            msg = DB.insert_task_info(db_cursor,database,current_user.org_id,title,date,notes,path,task_name)
            os.mkdir(path=path)
            flash(msg)
            return redirect('/upload')
    else:
        flash('Not authorized')
        return redirect('/mine')
    return render_template("new_task.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/index')


if __name__=="__main__":
    app.run(debug=True)