from flask import Flask,render_template,redirect,flash,make_response,request
from flask.helpers import send_from_directory
from form import LoginForm, NewCategoryForm, NewTaskForm, ResetPasswdForm ,UploadForm
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import datetime
import shutil
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
_request = request

def judgement(point):
    if "mobile" in str(_request.user_agent).lower():
        return f'/mobile/m.{point}.html'
    else:
        return f'/desktop/{point}.html'


#主页
@app.route('/')
@app.route('/index')
def index_page():
    return render_template(judgement('index'))


#上传页面
@app.route('/upload',methods=['GET','POST'])
@login_required
def upload_page():
    #获取组织任务
    select_tasks = DB.query_org_task(db_cursor,current_user.org_id,datetime.datetime.now())
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
            date_category = DB.query_tasks_date_category(db_cursor,select_tasks)[0]
            print(date_category)
            msg = DB.update_tasks_upload_info(db_cursor,database,current_user.org_id + "_" + date_category[1].lower(),date_category[0],current_user.id)
            file_path = task_path_list[int(select_tasks)] + f"\{str(current_user.id)}_{str(current_user.user_name)}_{str(uuid.uuid4().hex)}_{str(file.filename)}" 
            file.save(file_path)
            flash(msg)
            #重定向
            return redirect('/upload')
        #重定向
        return redirect('/mine')
    return render_template(judgement('upload'), form=form, task_list=task_list)


 
#复查界面
@app.route('/check')
@app.route('/check/<org_id>')
@app.route('/check/<org_id>/<table_category>')
@login_required
def check_page(org_id='',table_category=''):
    category_list = DB.query_category(db_cursor,current_user.org_id)
    if len(category_list) >= 1:
        try:
            """
            待优化
            此处为非跨组织用户判断
            """
            table_header,table_info = DB.query_check_table(db_cursor,str(org_id) +'_' + str(table_category).lower())
            table_header = [header[0] for header in table_header]
            table_info = [list(info) for info in table_info]
            for info in table_info:
                info[1],info[2] = info[2],info[1]
            return render_template(judgement('check'),table_header=table_header,table_info=table_info,org_id=org_id,category=category_list,now_category=table_category)
        except:
            return render_template(judgement('check'),category=category_list)
    else:
        """
        待优化
        此处为跨组织用户判断
        """
        org_id_temp = current_user.org_id.split(',')
        if len(current_user.org_id.split(',')) > 1:
            category_list = DB.query_category(db_cursor,org_id)
            try:
                table_header,table_info = DB.query_check_table(db_cursor,str(org_id) +'_' + str(table_category).lower())
                table_header = [header[0] for header in table_header]
                table_info = [list(info) for info in table_info]
                for info in table_info:
                    info[1],info[2] = info[2],info[1]
                return render_template(judgement('check'),table_header=table_header,table_info=table_info,org_id=org_id,org_category=org_id_temp,category=category_list,now_category=table_category)
            except:
                return render_template(judgement('check'),org_id=org_id,org_category=org_id_temp,category=category_list)
        return render_template(judgement('check'),org_category=org_id_temp)


#下载界面
@app.route('/download/<org_id>/<category>',methods=['GET'])
@login_required
def download_file(org_id='',category=''):
    directory = f'{str(data_file_path)}\{str(org_id)}'
    try:
        shutil.make_archive(fr"{str(directory)}\{str(category)}", 'zip', root_dir=fr'{str(directory)}\{str(category)}')
        filename = f'{str(category)}.zip'
        response = make_response(send_from_directory(str(directory), filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        return response
    except:
        flash('您或许选择了还未发布过任务的分类。')
        return redirect('/check')

   
#个人界面
@app.route('/mine')
@login_required
def mine_page():
    return render_template(judgement('mine'))


#帮助文档
@app.route('/doc')
def doc_page():
    return render_template(judgement('doc'))


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
    return render_template(judgement('login'), form=form)


@app.route('/new_task', methods=['GET','POST'])
@login_required
def new_task():
    #构造用户
    user = DB.user_info(db_cursor,current_user.id)
    category_list = DB.query_category(db_cursor,current_user.org_id)
    print(category_list)
    #实例化新任务表单
    form = NewTaskForm(category_list=category_list)
    #管理员认证
    if user.is_authenticated_admin(current_user.user_type):
        #判定表单
        if form.validate_on_submit():
            #获取表单数据
            title = form.task_title.data
            category = form.task_category.data
            date = form.task_date.data
            end_date = form.task_end_date.data
            notes = form.task_notes.data
            category = category_list[int(category)]
            #构造任务名
            task_name = (f"{str(date)}_{str(title)}_{str(current_user.org_name)}")
            #构造任务路径
            path = (fr"{str(data_file_path)}\{str(current_user.org_id)}\{str(category).lower()}\{str(date).replace(' ','_').replace(':','_')}_{str(title)}_{str(current_user.org_name)}_{str(uuid.uuid4().hex)}")
            os.makedirs(path)
            #数据库写入
            #复查表录入
            DB.insert_task_check_table_userinfo(db_cursor,database,str(current_user.org_id)+'_'+str(category).lower(),str(date),"未完成")
            #信息录入
            flash(DB.insert_task_info(db_cursor,database,current_user.org_id,title,date,end_date,notes,path,task_name,category.lower()))
            #重定向
            return redirect('/upload')
    #管理员认证失败
    else:
        flash('Not authorized')
        return redirect('/mine')
    return render_template(judgement('new_task'), form=form)


#创建分类
@app.route('/new_task/category', methods=['GET','POST'])
@login_required
def create_category_page():
    #实例化表单
    form = NewCategoryForm()
    category_temp = form.new_category.data
    print(category_temp)
    if form.validate_on_submit():
        category = category_temp.split(',')
        print(category)
        if (',' in list(category_temp) or '，' in list(category_temp)) and len(category) < 2 :
            category = category_temp.split('，')
            print(current_user.org_id,category)
        for item in category:
            if DB.insert_category_tb(db_cursor,database,current_user.org_id,item.lower()):
                table_name = str(current_user.org_id) + '_' + str(item.lower())
                print(table_name)
                DB.create_category_tb(db_cursor,database,current_user.org_id,table_name)
        return redirect('/new_task')
    return render_template(judgement('category'), form=form)


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
    return render_template(judgement('reset'), form=form)


#登出
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/index')


if __name__=="__main__":
    app.run(debug=True)