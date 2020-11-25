from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField,SubmitField,BooleanField,DateField,TextAreaField,SelectField,FileField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    userid = StringField(validators=[DataRequired()], render_kw={'type':'text','placeholder':'Enter your ID or Organization ID','class':'layui-input','style':'width: 390px;'})
    passwd = PasswordField(validators=[DataRequired(),Length(8,128)], render_kw={'type':'password','placeholder':'Enter password','class':'layui-input','style':'width: 390px;'})
    switch = BooleanField(render_kw={'type':'checkbos','lay-skin':'switch'})
    submit = SubmitField('Login')

class NewTaskForm(FlaskForm):
    task_title = StringField(validators=[DataRequired()])
    task_date = DateField(validators=[DataRequired()])
    task_notes = TextAreaField(validators=[DataRequired()])
    task_submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    select_task = SelectField(validators=[DataRequired()])
    upload_file = FileField(validators=[DataRequired(),FileAllowed(['zip','rar','7z'])])
    msg_task = StringField(validators=[DataRequired()])
    file_submit = SubmitField('Upload')

    def __init__(self,task_list,*arg,**kwargs) -> None:
        self.task_list = task_list
        super(UploadForm,self).__init__(*arg,**kwargs)
        self.select_task.choices = [(task_info[1],task_info[0]) for task_info in self.task_list.items()]
