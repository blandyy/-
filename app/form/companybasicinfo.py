# coding=utf-8
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class FirstCompanyBasicInfoForm(Form):
    company_name = StringField(u'公司全名', validators=[DataRequired()])
    city = StringField(u'公司所在城市', validators=[DataRequired()])
    industry = StringField(u'公司所在行业', validators=[DataRequired()])
    characteristic = StringField(u'公司特点', validators=[DataRequired()])


class CompanyBasicInfoForm(Form):
    city = StringField(u'公司所在城市', validators=[DataRequired()])
    industry = StringField(u'公司所在行业', validators=[DataRequired()])
    characteristic = StringField(u'公司特点', validators=[DataRequired()])