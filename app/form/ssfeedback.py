# coding:utf-8
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class SSFeedbackFrom(Form):
    professional_ranking = SelectField(u'专业排名',
                                       choices=[(u'前10%', u'前10%'), (u'前30%', u'前30%'),
                                                (u'前50%', u'前50%'), (u'50%以后', u'50%以后')],
                                       validators=[DataRequired()])
    course_satisfaction = SelectField(u'课程修习难度',
                                      choices=[(u'困难', u'困难'), (u'一般', u'一般'), (u'容易', u'容易')],
                                      validators=[DataRequired()])
    course_size = SelectField(u'课程量',
                              choices=[(u'巨大', u'巨大'), (u'较大', u'较大'), (u'一般', u'一般'),
                                       (u'较少', u'较少'),
                                       (u'少', u'少')],
                              validators=[DataRequired()])
    teacher_satisfaction = SelectField(u'对老师满意度',
                                       choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                (u'满意', u'满意'),
                                                (u'非常满意', u'非常满意')],
                                       validators=[DataRequired()])
    favorite_courses = StringField(u'最喜欢的课', validators=[DataRequired()])
    favorite_teacher = StringField(u'最喜欢的老师', validators=[DataRequired()])
    self_satisfaction = SelectField(u'自我满意度',
                                    choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                             (u'满意', u'满意'),
                                             (u'非常满意', u'非常满意')],
                                    validators=[DataRequired()])
    school_by_work = SelectField(u'工作中用到学校课程的比例',
                                 choices=[(u'基本没用到', u'基本没用到'), (u'用的比较少', u'用的比较少'), (u'一般', u'一般'),
                                          (u'用的比较多', u'用的比较多')],
                                 validators=[DataRequired()])
    school_class_work = SelectField(u'学校课程对工作选择的影响',
                                    choices=[(u'没有影响，非本专业工作', u'没有影响，非本专业工作'), (u'有影响，交叉专业', u'有影响，交叉专业'),
                                             (u'影响大，本专业工作', u'影响大，本专业工作')],
                                    validators=[DataRequired()])
    evaluate = TextAreaField(u'对专业的评价', validators=[DataRequired(u'评价不能为空')])
