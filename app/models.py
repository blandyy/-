# -*- coding:utf-8 -*-
from datetime import datetime

from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    accounts = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    category = db.Column(db.Integer)
    telephone = db.Column(db.String(255))
    email = db.Column(db.String(255))

    __tablename__ = 'user'

    @property
    def password(self):
        raise AttributeError("密码不允许读取")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.accounts)


class Student(db.Model, UserMixin):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    telephone = db.Column(db.String(255))
    email = db.Column(db.String(255))
    student_class = db.Column(db.String(255))
    specialty_id = db.Column(db.String(255))
    specialty = db.Column(db.String(255))
    college = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    student_num = db.Column(db.String(255))
    take_office = db.Column(db.String(255))
    achievement = db.Column(db.Integer)
    win_a_prize = db.Column(db.String(255))
    graduation_destination = db.Column(db.String(255))
    graduation_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Student %r>' % (self.id)


class Feedback(db.Model, UserMixin):
    __tablename__ = 'student_feedback'
    id = db.Column(db.Integer, primary_key=True)
    student_num = db.Column(db.String(255), unique=True)
    inauguration_company = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    career_satisfaction = db.Column(db.String(255))
    corporate_satisfaction = db.Column(db.String(255))
    take_office = db.Column(db.String(255))
    yearly_salary = db.Column(db.String(255))
    industry_satisfaction = db.Column(db.String(255))
    prize_winning = db.Column(db.String(255))
    self_evaluation = db.Column(db.String(255))
    counts = db.Column(db.Integer)
    shengqian = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    specialty = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class Basicinfo(db.Model, UserMixin):
    __tablename__ = 'basicinfo'
    id = db.Column(db.Integer, primary_key=True)
    student_num = db.Column(db.String(255), unique=True)
    company = db.Column(db.String(255))
    position = db.Column(db.String(255))
    relevant = db.Column(db.String(255))
    technology = db.Column(db.String(255))
    yearly_salary = db.Column(db.String(255))
    sex = db.Column(db.String(255))
    is_quit = db.Column(db.String(255))
    quit_reason = db.Column(db.String(255))
    work_time = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    specialty = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class Company(db.Model, UserMixin):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    company_account = db.Column(db.String(255), unique=True)
    company_name = db.Column(db.String(255))
    city = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    job = db.Column(db.String(255))
    characteristic = db.Column(db.String(255))
    claim = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class CSFeedback(db.Model, UserMixin):
    __tablename__ = 'c_s_feedback'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(255))
    student_num = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    student_name = db.Column(db.String(255))
    personality_satisfaction = db.Column(db.String(255))
    skill_satisfaction = db.Column(db.String(255))
    plasticity = db.Column(db.String(255))
    evaluate = db.Column(db.String(255))
    year = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    specialty = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class CompanyProfessionalFeed(db.Model, UserMixin):
    __tablename__ = 'company_professional_feed'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    specialty = db.Column(db.String(255))
    professional_fit = db.Column(db.String(255))
    students_kills_mastery = db.Column(db.String(255))
    professional_satisfaction = db.Column(db.String(255))
    student_satisfaction = db.Column(db.String(255))
    evaluate = db.Column(db.String(255))
    year = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class SSFeedback(db.Model, UserMixin):
    __tablename__ = 's_s_feedback'
    id = db.Column(db.Integer, primary_key=True)
    student_num = db.Column(db.String(255))
    student_name = db.Column(db.String(255))
    specialty_id = db.Column(db.String(255))
    specialty = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    student_class = db.Column(db.String(255))
    professional_ranking = db.Column(db.String(255))
    course_satisfaction = db.Column(db.String(255))
    course_size = db.Column(db.String(255))
    teacher_satisfaction = db.Column(db.String(255))
    favorite_courses = db.Column(db.String(255))
    favorite_teacher = db.Column(db.String(255))
    self_satisfaction = db.Column(db.String(255))
    school_by_work = db.Column(db.String(255))
    school_class_work = db.Column(db.String(255))
    evaluate = db.Column(db.String(255))
    update_time = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class Year(db.Model, UserMixin):
    __tablename__ = 'year'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return '<id %r>' % (self.id)


class Grade(db.Model, UserMixin):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return '<id %r>' % (self.id)


class QuXiang(db.Model, UserMixin):
    __tablename__ = 'quxiang'
    id = db.Column(db.Integer, primary_key=True)
    qx = db.Column(db.String(255))
    qxid = db.Column(db.Integer)

    def __repr__(self):
        return '<id %r>' % (self.id)


class AbilityClassification(db.Model, UserMixin):
    __tablename__ = 'ability_classification'
    id = db.Column(db.Integer, primary_key=True)
    kccode = db.Column(db.String(255))
    kcname = db.Column(db.String(255))
    kc_classification = db.Column(db.String(255))
    kc_weight = db.Column(db.Float)
    specialty = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class Specialty(db.Model, UserMixin):
    __tablename__ = 'specialty'
    id = db.Column(db.Integer, primary_key=True)
    specialty_name = db.Column(db.String(255))
    school = db.Column(db.String(255))
    specialty_id = db.Column(db.String(255))
    school_id = db.Column(db.String(255))

    def __repr__(self):
        return '<id %r>' % (self.id)


class AbilityCategory(db.Model, UserMixin):
    __tablename__ = 'ability_category'
    id = db.Column(db.Integer, primary_key=True)
    specialty = db.Column(db.String(255))
    ability = db.Column(db.String(255))
    ability_weight = db.Column(db.Float)

    def __repr__(self):
        return '<id %r>' % (self.id)
