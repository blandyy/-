# coding=utf-8 
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class LoginForm(Form):
    accounts = StringField(u'账号', validators=[
        DataRequired(u'账号不能为空')], render_kw={
        'placeholder': '请输入账号',
        'required': '',
        'autofocus': ''
    })
    password = PasswordField(u'密码', validators=[
        DataRequired('password is null')], render_kw={
        'placeholder': '请输入密码',
        'required': '',
        'autofocus': ''
    })
    submit = SubmitField('Log In')


class StudentLoginForm(Form):
    accounts = StringField(u'学号', validators=[
        DataRequired('学号不能为空')], render_kw={
        'class': 'form-control',
        'placeholder': '请输入学号',
        'required': '',
        'autofocus': ''
    })
    password = PasswordField(u'密码', validators=[
        DataRequired('password is null')], render_kw={
        'class': 'form-control',
        'placeholder': '请输入密码',
        'required': '',
        'autofocus': ''
    })
    submit = SubmitField('Log In')
