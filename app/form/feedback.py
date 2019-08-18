# coding:utf-8 
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class FeedbackForm(Form):
    occupation = StringField(u'就职行业', validators=[DataRequired(u'行业不能为空')])
    career_satisfaction = SelectField(
        u'职业满意度', choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'), (u'满意', u'满意'), (u'非常满意', u'非常满意')],
        validators=[DataRequired()])
    corporate_satisfaction = SelectField(
        u'企业满意度', choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'), (u'满意', u'满意'), (u'非常满意', u'非常满意')],
        validators=[DataRequired()])
    take_office = StringField(u'任职', validators=[DataRequired(u'职位不能为空')])
    industry_satisfaction = SelectField(
        u'行业满意度', choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'), (u'满意', u'满意'), (u'非常满意', u'非常满意')],
        validators=[DataRequired()])
    shengqian = TextAreaField(u'升迁变化', validators=[DataRequired(u'不能为空')])
    prize_winning = TextAreaField(u'在公司获奖(没有请填无)', validators=[
        DataRequired(u'获奖不能为空')])
    self_evaluation = TextAreaField(
        u'自我评价', validators=[DataRequired(u'自我评价不能为空')])
