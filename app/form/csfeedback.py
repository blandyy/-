# coding:utf-8
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class CSFeedbackFrom(Form):
    year = SelectField(u'评价年度', validators=[DataRequired()])
    personality_satisfaction = SelectField(u'学生行为满意度',
                                           choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                    (u'满意', u'满意'),
                                                    (u'非常满意', u'非常满意')],
                                           validators=[DataRequired()])
    skill_satisfaction = SelectField(u'技能满意度',
                                     choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'), (u'满意', u'满意'),
                                              (u'非常满意', u'非常满意')],
                                     validators=[DataRequired()])
    plasticity = SelectField(u'可塑性',
                             choices=[(u'可塑性低', u'可塑性低'), (u'可塑性一般', u'可塑性一般'), (u'可塑性高', u'可塑性高'),
                                      (u'可塑性极高', u'可塑性极高')],
                             validators=[DataRequired()])
    evaluate = TextAreaField(u'对毕业生评价', validators=[DataRequired(u'评价不能为空')])


class EditcsFeedForm(Form):
    personality_satisfaction = SelectField(u'学生行为满意度',
                                           choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'),
                                                    (u'满意', u'满意'),
                                                    (u'非常满意', u'非常满意')],
                                           validators=[DataRequired()])
    skill_satisfaction = SelectField(u'技能满意度',
                                     choices=[(u'非常不满意', u'非常不满意'), (u'不满意', u'不满意'), (u'一般', u'一般'), (u'满意', u'满意'),
                                              (u'非常满意', u'非常满意')],
                                     validators=[DataRequired()])
    plasticity = SelectField(u'可塑性',
                             choices=[(u'可塑性低', u'可塑性低'), (u'可塑性一般', u'可塑性一般'), (u'可塑性高', u'可塑性高'),
                                      (u'可塑性极高', u'可塑性极高')],
                             validators=[DataRequired()])
    evaluate = TextAreaField(u'对毕业生评价', validators=[DataRequired(u'评价不能为空')], render_kw={'rows':5})


class CheckCSFeedbackFrom(Form):
    student = SelectField(u'选择学生', validators=[DataRequired()])
    submit = SubmitField('Post')
