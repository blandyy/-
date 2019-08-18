from flask import render_template, request, redirect, Flask, Blueprint, url_for
from flask_login import login_required
from app import app
from app import db
from app.models import User, Student


@app.route("/")
@app.route("/index")
def index():
    return render_template('index/index.html')


@app.route("/login")
def login():
    # new1 = User(accounts=111, password='sss', name='aaa', category=1, telephone='1112222', email='333333@163.com')
    # db.session.add(new1)
    # db.session.commit()
    # new2 = Student(name='mu', telephone='15655558888', email='1111@163.com', specialty=8, college=5,
    #               student_num='2015111', password='sss', take_office='s', achievement=7, win_a_prize='null',
    #               graduation_destination='beijing')
    # db.session.add(new2)
    # db.session.commit()
    return 'sss'
