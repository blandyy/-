# coding:utf-8
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class CPFeedbackFrom(Form):
    year = SelectField(u'选择年度', validators=[DataRequired()])
    professional_fit = SelectField(u'专业契合度',
                                   choices=[(u'不契合，非主招专业', u'不契合，非主招专业'), (u'契合，招生专业之一', u'契合，招生专业之一'),
                                            (u'完全契合，主招专业', u'完全契合，主招专业')],
                                   validators=[DataRequired()])
    students_kills_mastery = SelectField(u'学生技能满意度',
                                         choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                  (u'满意', u'满意'),
                                                  (u'非常满意', u'非常满意')],
                                         validators=[DataRequired()])
    professional_satisfaction = SelectField(u'专业满意度',
                                            choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                     (u'满意', u'满意'),
                                                     (u'非常满意', u'非常满意')],
                                            validators=[DataRequired()])
    student_satisfaction = SelectField(u'学生满意度',
                                       choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                (u'满意', u'满意'),
                                                (u'非常满意', u'非常满意')],
                                       validators=[DataRequired()])
    evaluate = TextAreaField(u'对毕业生评价', validators=[DataRequired(u'评价不能为空')])


class EditCPFeedFrom(Form):
    professional_fit = SelectField(u'专业契合度',
                                   choices=[(u'不契合，非主招专业', u'不契合，非主招专业'), (u'契合，招生专业之一', u'契合，招生专业之一'),
                                            (u'完全契合，主招专业', u'完全契合，主招专业')],
                                   validators=[DataRequired()])
    students_kills_mastery = SelectField(u'学生技能满意度',
                                         choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                  (u'满意', u'满意'),
                                                  (u'非常满意', u'非常满意')],
                                         validators=[DataRequired()])
    professional_satisfaction = SelectField(u'专业满意度',
                                            choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                     (u'满意', u'满意'),
                                                     (u'非常满意', u'非常满意')],
                                            validators=[DataRequired()])
    student_satisfaction = SelectField(u'学生满意度',
                                       choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                (u'满意', u'满意'),
                                                (u'非常满意', u'非常满意')],
                                       validators=[DataRequired()])
    evaluate = TextAreaField(u'对毕业生评价', validators=[DataRequired(u'评价不能为空')], render_kw={'rows': 5})


class CheckCPFeedbackFrom(Form):
    specialty = SelectField(u'选择专业', validators=[DataRequired()])
    submit = SubmitField('Post')
