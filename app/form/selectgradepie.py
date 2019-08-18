# coding:utf-8
from flask_wtf import FlaskForm as Form
from wtforms import SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class SelectGradePie(Form):
    grade = SelectField(u'选择年级', validators=[DataRequired()])