# coding:utf-8
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class FristBasicInfoForm(Form):
    company = SelectField(u'就职公司', validators=[DataRequired()])
    position = StringField(u'职位', validators=[DataRequired('职位不能为空')])
    technology = StringField(u'使用技术', validators=[DataRequired('技术不能为空')])
    relevant = SelectField(
        '职业与本专业相关度', choices=[(u'相关,本专业', u'相关,本专业'), (u'相关度小,交叉专业', u'相关度小,交叉专业'),
                              (u'不相关,非本专业', u'不相关,非本专业')],
        validators=[DataRequired()])
    work_time = SelectField(
        '工作年限', choices=[(u'3年以下', u'3年以下'), (u'3年以上5年以下', u'3年以上5年以下'),
                         (u'5年以上10年以下', u'5年以上10年以下'), (u'10年以上20年以下', u'10年以上20年以下'),
                         (u'20年以上30年以下', u'20年以上30年以下'), (u'30年以上', u'30年以上')],
        validators=[DataRequired()])
    yearly_salary = SelectField(
        '年薪', choices=[(u'10万以下', u'10万以下'), (u'10-29万', u'10-29万'), (u'30-50万', u'30-49万'), (u'50-99万', u'50-99万'),
                       (u'100-499万', u'100-499万'), (u'500-999万', u'500-999万'), (u'1千万以上1亿以下', u'1千万以上1亿以下'),
                       (u'1亿以上', u'1亿以上')],
        validators=[DataRequired()])
    sex = SelectField(
        '性别', choices=[(u'男', u'男'), (u'女', u'女')], validators=[DataRequired()])
    is_quit = SelectField(
        '是否离职', choices=[(u'离职', u'离职'), (u'在职', u'在职')], validators=[DataRequired()])
    quit_reason = SelectField(
        '离职原因(如在职则选择上次离职原因或选择第一份工作未离职)', choices=[(u'找到更好的工作', u'找到更好的工作'), (u'家庭或身体原因', u'家庭或身体原因'),
                                                  (u'因公司规定离职', u'因公司规定离职'), (u'其他(如个人辞职)', u'其他(如个人辞职)'),
                                                  (u'第一份工作未离职', u'第一份工作未离职')],
        validators=[DataRequired()])


class BasicInfoForm(Form):
    company = SelectField(u'就职公司', validators=[DataRequired()])
    position = StringField(u'职位', validators=[DataRequired('职位不能为空')])
    technology = StringField(u'使用技术', validators=[DataRequired('技术不能为空')])
    relevant = SelectField(
        '职业与本专业相关度', choices=[(u'相关,本专业', u'相关,本专业'), (u'相关度小,交叉专业', u'相关度小,交叉专业'),
                              (u'不相关,非本专业', u'不相关,非本专业')],
        validators=[DataRequired()])
    work_time = SelectField(
        '工作年限', choices=[(u'3年以下', u'3年以下'), (u'3年以上5年以下', u'3年以上5年以下'),
                         (u'5年以上10年以下', u'5年以上10年以下'), (u'10年以上20年以下', u'10年以上20年以下'),
                         (u'20年以上30年以下', u'20年以上30年以下'), (u'30年以上', u'30年以上')],
        validators=[DataRequired()])
    yearly_salary = SelectField(
        '年薪', choices=[(u'10万以下', u'10万以下'), (u'10-29万', u'10-29万'), (u'30-50万', u'30-49万'), (u'50-99万', u'50-99万'),
                       (u'100-499万', u'100-499万'), (u'500-999万', u'500-999万'), (u'1千万以上1亿以下', u'1千万以上1亿以下'),
                       (u'1亿以上', u'1亿以上')],
        validators=[DataRequired()])
    is_quit = SelectField(
        '是否离职', choices=[(u'离职', u'离职'), (u'在职', u'在职')], validators=[DataRequired()])
    quit_reason = SelectField(
        '离职原因(如在职则选择上次离职原因或选择第一份工作未离职)', choices=[(u'找到更好的工作', u'找到更好的工作'), (u'家庭或身体原因', u'家庭或身体原因'),
                                                  (u'因公司规定离职', u'因公司规定离职'), (u'其他(如个人辞职)', u'其他(如个人辞职)'),
                                                  (u'第一份工作未离职', u'第一份工作未离职')],
        validators=[DataRequired()])
