from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField,SubmitField,BooleanField,DateField,TextAreaField,SelectField,FileField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    userid = StringField(validators=[DataRequired()], render_kw={'type':'text','placeholder':'Enter your ID','class':'layui-input','style':'width: 390px;'})
    passwd = PasswordField(validators=[DataRequired(),Length(8,128)], render_kw={'type':'password','placeholder':'Enter password','class':'layui-input','style':'width: 390px;'})
    switch = BooleanField(render_kw={'type':'checkbos','lay-skin':'switch'})
    submit = SubmitField('Login')


class NewTaskForm(FlaskForm):
    task_title = StringField(validators=[DataRequired()])
    task_category = SelectField(validators=[DataRequired()])
    task_date = DateField(validators=[DataRequired()])
    task_notes = TextAreaField()
    task_submit = SubmitField('Submit')

    def __init__(self,category_list,*arg,**kwargs) -> None:
        self.category_list = category_list
        super(NewTaskForm,self).__init__(*arg,**kwargs)
        self.task_category.choices = [(item[0],item[1]) for item in self.category_list.items()]


class UploadForm(FlaskForm):
    select_task = SelectField(validators=[DataRequired()])
    upload_file = FileField(validators=[DataRequired(),FileAllowed(['zip','rar','7z','jpg','jpeg','png','doc','docx','pdf'])])
    msg_task = StringField()
    file_submit = SubmitField('上传')

    def __init__(self,task_list,*arg,**kwargs) -> None:
        self.task_list = task_list
        super(UploadForm,self).__init__(*arg,**kwargs)
        self.select_task.choices = [(task_info[1],task_info[0]) for task_info in self.task_list.items()]


class NewCategoryForm(FlaskForm):
    new_category = StringField(validators=[DataRequired()])
    category_submit = SubmitField('提交')
        

class ResetPasswdForm(FlaskForm):
    passwd = PasswordField(validators=[DataRequired(),Length(8,128)], render_kw={'type':'password','placeholder':'Enter the old password','class':'layui-input','style':'width: 390px;'})
    new_passwd = PasswordField(validators=[DataRequired(),Length(8,128)], render_kw={'type':'password','placeholder':'Enter the new password','class':'layui-input','style':'width: 390px;'})
    new_passwd_repeat = PasswordField(validators=[DataRequired(),Length(8,128)], render_kw={'type':'password','placeholder':'Repeat the new password','class':'layui-input','style':'width: 390px;'})
    submit = SubmitField('Reset')