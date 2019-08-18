# coding=utf-8
import collections
from flask import render_template, request, redirect, Flask, Blueprint, url_for
from flask_login import login_user, login_required, current_user, logout_user

from app.enum import enum
from app.models import User, Basicinfo, Company, CSFeedback, Student, CompanyProfessionalFeed, Feedback, Specialty, \
    Grade, Year, AbilityCategory, AbilityClassification, SSFeedback
from app import login_manager, db, REMOTE_HOST
from app.user import user
from app.form.login import LoginForm
from app.form.csfeedback import CSFeedbackFrom, CheckCSFeedbackFrom, EditcsFeedForm
from app.form.cpfeedback import CPFeedbackFrom, CheckCPFeedbackFrom, EditCPFeedFrom
from app.form.companybasicinfo import FirstCompanyBasicInfoForm, CompanyBasicInfoForm
from pyecharts import Page, WordCloud, Pie, Line
from app.form.selectgradepie import SelectGradePie
import pymysql
import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@user.before_request
def before_request():
    pass


@user.route('/index', methods=['GET', 'POST'])
@user.route('/', methods=['GET', 'POST'])
@login_required
def index():
    stunum = Student.query.filter().count()
    print stunum
    num = 0
    if stunum:
        num = stunum
    else:
        num = 0
    if request.method == 'GET':
        if current_user.category == 1:
            companyinfo = Company.query.filter(
                Company.company_account == current_user.accounts).first()
            if not companyinfo:
                return redirect(url_for('user.fristbasicinfo', errors=u'您还没有录入基本信息，请录入'))
            strinfo = companyinfo.company_name + '  ' + current_user.name
            return render_template('user/index.html', errors=request.args.get("errors"), nnum=num, datainfo=companyinfo,
                                   strinfo=strinfo)
        else:
            return render_template('user/index.html', errors=request.args.get("errors"), nnum=num)


@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return render_template('user/login.html', form=form)
        users = User.query.filter(User.accounts == form.accounts.data).first()
        if users:
            is_passwd = users.check_password_hash(form.password.data)
            if is_passwd:
                login_user(users)
                return redirect(url_for('user.index'))
            else:
                return render_template('user/login.html', form=form, errors='password error')
        else:
            return render_template('user/login.html', form=form, errors='user error')
    return render_template('user/login.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@user.route('/fristbasicinfo', methods=['GET', 'POST'])
@login_required
def fristbasicinfo():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    form = FirstCompanyBasicInfoForm()
    if request.method == 'POST':
        company_name = form.company_name.data
        city = form.city.data
        industry = form.industry.data
        job = u'暂定'
        characteristic = form.characteristic.data
        claim = u'暂定'
        newcompany = Company(company_account=current_user.accounts, company_name=company_name, city=city,
                             industry=industry, job=job, characteristic=characteristic, claim=claim)
        db.session.add(newcompany)
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('user/firstbasicinfo.html', form=form, errors=u'您还没有录入基本信息，请录入')


@user.route('/basicinfo', methods=['GET', 'POST'])
@login_required
def basicinfo():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    form = CompanyBasicInfoForm()
    info = Company.query.filter(
        Company.company_account == current_user.accounts).first()
    if not info:
        return redirect(url_for('user.fristbasicinfo', errors=u'您还没有录入基本信息，请录入'))
    form.city.render_kw = {'value': info.city}
    form.industry.render_kw = {'value': info.industry}
    form.characteristic.render_kw = {'value': info.characteristic}
    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return redirect(url_for('user.index'))
        updatainfo = Company.query.filter(
            Company.company_account == current_user.accounts).first()
        print updatainfo

        updatainfo.city = form.city.data
        updatainfo.industry = form.industry.data
        updatainfo.job = u'暂定'
        updatainfo.characteristic = form.characteristic.data
        updatainfo.claim = u'暂定'
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('user/basicinfo.html', form=form)


@user.route('/startcsfeedback', methods=['GET', 'POST'])
@login_required
def startcsfeedback():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        companyn = Company.query.filter(Company.company_account == current_user.accounts).first()
        studentinfo = Basicinfo.query.filter(
            Basicinfo.company == companyn.company_name).all()
        studentlist = []
        for i in studentinfo:
            sinfo = Student.query.filter(Student.student_num == i.student_num).first()
            studentlist.append((i.student_num, sinfo.name, sinfo.college, sinfo.specialty))
        if request.args.get('studentnum') and request.args.get('edit') == 'True':
            print request.args.get('studentnum')
            return redirect(
                url_for('user.csfeedback', studentnum=request.args.get('studentnum')))
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/startcsfeedback.html', studentlist=studentlist, specialtylist=specialtylist,
                               gradelist=gradelist)
    if request.method == 'POST':
        companyn = Company.query.filter(Company.company_account == current_user.accounts).first()
        studentinfo = Basicinfo.query.filter(
            Basicinfo.company == companyn.company_name).all()
        studentlist = []
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            studentinfo = Basicinfo.query.filter(
                Basicinfo.company == companyn.company_name).all()
        elif specialty != '选择专业' and grade == '选择年级':
            studentinfo = Basicinfo.query.filter(Basicinfo.company == companyn.company_name,
                                                 Basicinfo.specialty == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            studentinfo = Basicinfo.query.filter(Basicinfo.company == companyn.company_name,
                                                 Basicinfo.specialty == specialty, Basicinfo.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            studentinfo = Basicinfo.query.filter(Basicinfo.company == companyn.company_name,
                                                 Basicinfo.grade == grade).all()
        for i in studentinfo:
            sinfo = Student.query.filter(Student.student_num == i.student_num).first()
            studentlist.append((i.student_num, sinfo.name, sinfo.college, sinfo.specialty))
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/startcsfeedback.html', studentlist=studentlist, specialtylist=specialtylist,
                               gradelist=gradelist)


@user.route('/csfeedback', methods=['GET', 'POST'])
@login_required
def csfeedback():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    companyn = Company.query.filter(Company.company_account == current_user.accounts).first()

    yearlist = []
    tmp = sorted(enum.getyear(), reverse=True)
    for j in tmp:
        ylab = j + u'年'
        yearlist.append((j, ylab))

    csform = CSFeedbackFrom()
    csform.year.choices = yearlist
    companys = current_user.accounts
    if request.method == 'GET':
        if request.args.get('studentnum'):
            print request.args.get('studentnum')
            csinfo = CSFeedback.query.filter(CSFeedback.company == companys,
                                             CSFeedback.student_num == request.args.get('studentnum')).all()
            studensinfo = Student.query.filter(Student.student_num == request.args.get('studentnum')).first()
            grades = studensinfo.grade
            yearlists = []
            tmps = sorted(enum.getyear(), reverse=True)
            for j in tmps:
                intgrade = int(grades)
                intyear = int(j)
                if intyear >= intgrade:
                    ylabs = j + u'年'
                    yearlists.append((j, ylabs))
            csform.year.choices = yearlists
            if csinfo:
                infolist = []
                for i in csinfo:
                    infolist.append(i.year)
                ilist = collections.Counter(infolist)
                flist = []
                for j in ilist.keys():
                    flist.append((j))
            else:
                flist = [(u'对此学生还未录入任何反馈！')]
            return render_template('user/csfeedback.html', form=csform, flist=sorted(flist),
                                   studentnums=request.args.get('studentnum'),
                                   errors=request.args.get("errors"))
    if request.method == 'POST':
        companyn_num = companyn.company_account
        companyn_name = companyn.company_name
        student_num = request.args.get('studentnumss')
        ssname = Student.query.filter(Student.student_num == student_num).first()
        student_name = ssname.name
        personality_satisfaction = csform.personality_satisfaction.data
        skill_satisfaction = csform.skill_satisfaction.data
        plasticity = csform.plasticity.data
        evaluate = csform.evaluate.data
        year = csform.year.data
        csinfo = CSFeedback.query.filter(CSFeedback.company == companyn_num,
                                         CSFeedback.student_num == student_num).all()
        if csinfo:
            infolist = []
            for i in csinfo:
                infolist.append(i.year)
            ilist = collections.Counter(infolist)
            flist = []
            for j in ilist.keys():
                flist.append((j, ilist[j]))
        else:
            flist = [(u'对此学生还未录入任何反馈！')]
        is_save = CSFeedback.query.filter(CSFeedback.company == companyn_num, CSFeedback.student_num == student_num,
                                          CSFeedback.year == year).all()
        if is_save:
            return redirect(
                url_for('user.csfeedback', studentnum=student_num, flist=sorted(flist), errors=u'您已经录入过当前学生的当前年度评价'))
        else:
            stinfo = Student.query.filter(Student.student_num == student_num).first()
            specialty = stinfo.specialty_id
            grade = stinfo.grade
            newcsfeedback = CSFeedback(company=companyn_num, student_num=student_num, company_name=companyn_name,
                                       student_name=student_name, personality_satisfaction=personality_satisfaction,
                                       skill_satisfaction=skill_satisfaction, plasticity=plasticity, evaluate=evaluate,
                                       year=year, specialty=specialty, grade=grade)
            db.session.add(newcsfeedback)
            db.session.commit()
            return redirect(url_for('user.index'))


@user.route('/editcsfeed', methods=['GET', 'POST'])
@login_required
def editcsfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    form = EditcsFeedForm()
    companys = current_user.accounts
    if request.method == 'GET':
        if request.args.get('studentnum') and request.args.get('edit') == 'True' and request.args.get('year'):
            yyear = request.args.get('year')
            sstudentnum = request.args.get('studentnum')
            csinfo = CSFeedback.query.filter(CSFeedback.company == companys, CSFeedback.student_num == sstudentnum,
                                             CSFeedback.year == yyear).first()
            csinfolist = [csinfo.student_num, csinfo.personality_satisfaction, csinfo.skill_satisfaction,
                          csinfo.plasticity, csinfo.evaluate, csinfo.year]
            # form.evaluate.render_kw['value'] = csinfo.evaluate
            form.evaluate.data = csinfo.evaluate
            return render_template('user/editcsfeed.html', form=form, csinfolist=csinfolist)
    if request.method == 'POST':
        student_num = request.args.get('studentnumss')
        print student_num
        yyear = request.args.get('yyear')
        print yyear
        personality_satisfaction = form.personality_satisfaction.data
        skill_satisfaction = form.skill_satisfaction.data
        plasticity = form.plasticity.data
        evaluate = form.evaluate.data
        cs = CSFeedback.query.filter(CSFeedback.company == companys, CSFeedback.student_num == student_num,
                                     CSFeedback.year == yyear).first()
        print cs
        cs.personality_satisfaction = personality_satisfaction
        cs.skill_satisfaction = skill_satisfaction
        cs.plasticity = plasticity
        cs.evaluate = evaluate
        db.session.commit()
        return redirect(url_for('user.csfeedback', studentnum=student_num))


@user.route('/selectgradecsfeed', methods=['GET', 'POST'])
@login_required
def selectgradecsfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    gradelist = sorted(enum.getyear(), reverse=True)
    if request.method == 'GET':
        return render_template('user/selectgradecsfeed.html', gradelist=gradelist,
                               errors=request.args.get("errors"))


@user.route('/selectnextgradecsfeed', methods=['GET', 'POST'])
@login_required
def selectnextgradecsfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get("nnext"):
            yyear = request.args.get("nnext")
            specialty = request.form.get('specialty')
            print yyear
            csinfo = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                             CSFeedback.year == yyear).all()
            if not csinfo:
                return redirect(url_for('user.selectgradecsfeed', errors=yyear + '年下面没有您填写的学生问卷，请重新选择年度'))
            else:
                studentlist = []
                for i in csinfo:
                    ssinfo = Student.query.filter(Student.student_num == i.student_num).first()
                    studentlist.append((i.student_num, i.student_name, ssinfo.specialty))
                specialtylist = []
                specialtyss = Specialty.query.all()
                for i in specialtyss:
                    specialtylist.append((i.specialty_name, i.specialty_id))
                gradelist = sorted(enum.getgrade(), reverse=True)
                return render_template('user/selectnextgradecsfeed.html', studentlist=studentlist, year=yyear,
                                       gradelist=gradelist,
                                       specialtylist=specialtylist,
                                       errors=request.args.get("errors"))
        else:
            return redirect(url_for('user.selectgradecsfeed'))
    if request.method == 'POST':
        if request.args.get("nnext"):
            yyear = request.args.get("nnext")
            print yyear
            csinfo = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                             CSFeedback.year == yyear).all()
            if not csinfo:
                return redirect(url_for('user.selectgradecsfeed', errors=yyear + '年下面没有您填写的学生问卷，请重新选择年度'))
            else:
                studentlist = []
                specialty = request.form.get('specialty')
                grade = request.form.get('grade')
                if specialty == '选择专业' and grade == '选择年级':
                    csinfo = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                                     CSFeedback.year == yyear).all()
                elif specialty != '选择专业' and grade == '选择年级':
                    csinfo = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                                     CSFeedback.year == yyear, CSFeedback.specialty == specialty).all()
                elif specialty != '选择专业' and grade != '选择年级':
                    csinfo = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                                     CSFeedback.year == yyear,
                                                     CSFeedback.specialty == specialty, CSFeedback.grade == grade).all()
                elif specialty == '选择专业' and grade != '选择年级':
                    csinfo = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                                     CSFeedback.year == yyear, CSFeedback.grade == grade).all()
                for i in csinfo:
                    ssinfo = Student.query.filter(Student.student_num == i.student_num).first()
                    studentlist.append((i.student_num, i.student_name, ssinfo.specialty))
                specialtylist = []
                specialty = Specialty.query.all()
                for j in specialty:
                    specialtylist.append((j.specialty_name, j.specialty_id))
                gradelist = sorted(enum.getgrade(), reverse=True)
                return render_template('user/selectnextgradecsfeed.html', studentlist=studentlist, year=yyear,
                                       gradelist=gradelist,
                                       specialtylist=specialtylist,
                                       errors=request.args.get("errors"))
        else:
            return redirect(url_for('user.selectgradecsfeed'))


@user.route('/delcsfeed', methods=['GET', 'POST'])
@login_required
def delcsfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('studentnum') and request.args.get('del') == 'True' and request.args.get('year'):
            yyear = request.args.get('year')
            csnr = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                           CSFeedback.student_num == request.args.get('studentnum'),
                                           CSFeedback.year == yyear).first()
            db.session.delete(csnr)
            db.session.commit()
        if request.args.get('tt') == 'True':
            return redirect(url_for('user.csfeedback', studentnum=request.args.get('studentnum')))
        else:
            return redirect(url_for('user.selectgradecsfeed'))


@user.route('/checkgradecsfeed', methods=['GET', 'POST'])
@login_required
def checkgradecsfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('studentnum') and request.args.get('check') == 'True' and request.args.get('year'):
            yyear = request.args.get('year')
            csnr = CSFeedback.query.filter(CSFeedback.company == current_user.accounts,
                                           CSFeedback.student_num == request.args.get('studentnum'),
                                           CSFeedback.year == yyear).first()
            return render_template('user/checkgradecsfeed.html', datainfo=csnr)
        else:
            return redirect(url_for('user.selectgradecsfeed', errors='参数错误'))


@user.route('/startcpfeedback', methods=['GET', 'POST'])
@login_required
def startcpfeedback():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    specialtytinfo = Specialty.query.all()
    specialtylist = []
    for i in specialtytinfo:
        specialtylist.append((i.school, i.specialty_name))
    if request.method == 'GET':
        if request.args.get('specialty') and request.args.get('edit') == 'True':
            print request.args.get('specialty')
            return redirect(
                url_for('user.cpfeedback', specialty=request.args.get('specialty')))
        return render_template('user/startcpfeedback.html', specialtylist=specialtylist)


@user.route('/cpfeedback', methods=['GET', 'POST'])
@login_required
def cpfeedback():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    cpform = CPFeedbackFrom()
    companyn = Company.query.filter(Company.company_account == current_user.accounts).first()
    yearlist = []
    tmp = sorted(enum.getyear(), reverse=True)
    for j in tmp:
        ylab = j + u'年'
        yearlist.append((j, ylab))
    cpform.year.choices = yearlist
    if request.method == 'GET':
        if request.args.get('specialty'):
            cpinfo = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == current_user.accounts,
                                                          CompanyProfessionalFeed.specialty == request.args.get(
                                                              'specialty')).all()
            if cpinfo:
                infolist = []
                for i in cpinfo:
                    infolist.append(i.year)
                ilist = collections.Counter(infolist)
                flist = []
                for j in ilist.keys():
                    flist.append((j))
            else:
                flist = [(u'对此专业还未录入任何反馈！')]
            return render_template('user/cpfeedback.html', form=cpform, errors=request.args.get("errors"),
                                   specialty=request.args.get('specialty'), flist=flist)
    if request.method == 'POST':
        companyn_num = companyn.company_account
        companyn_name = companyn.company_name
        specialty = request.args.get('specialtyss')
        professional_fit = cpform.professional_fit.data
        students_kills_mastery = cpform.students_kills_mastery.data
        professional_satisfaction = cpform.professional_satisfaction.data
        student_satisfaction = cpform.student_satisfaction.data
        evaluate = cpform.evaluate.data
        year = cpform.year.data
        cpinfo = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == current_user.accounts,
                                                      CompanyProfessionalFeed.specialty == request.args.get(
                                                          'specialty')).all()
        if cpinfo:
            infolist = []
            for i in cpinfo:
                infolist.append(i.year)
            ilist = collections.Counter(infolist)
            flist = []
            for j in ilist.keys():
                flist.append((j))
        else:
            flist = [(u'对此专业还未录入任何反馈！')]
        is_save = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == companyn_num,
                                                       CompanyProfessionalFeed.year == year,
                                                       CompanyProfessionalFeed.specialty == specialty).all()
        if is_save:
            return redirect(url_for('user.cpfeedback', flist=flist, specialty=specialty, errors=u'您已经录入过当前专业的当前年度评价'))
        else:
            newcpfeedback = CompanyProfessionalFeed(company=companyn_num, company_name=companyn_name,
                                                    specialty=specialty, professional_fit=professional_fit,
                                                    students_kills_mastery=students_kills_mastery,
                                                    professional_satisfaction=professional_satisfaction,
                                                    student_satisfaction=student_satisfaction, evaluate=evaluate,
                                                    year=year)
            db.session.add(newcpfeedback)
            db.session.commit()
            return redirect(url_for('user.index'))


@user.route('/editcpfeed', methods=['GET', 'POST'])
@login_required
def editcpfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    form = EditCPFeedFrom()
    if request.method == 'GET':
        if request.args.get('specialty') and request.args.get('edit') == 'True' and request.args.get('year'):
            yyear = request.args.get('year')
            specialty = request.args.get('specialty')
            companys = current_user.accounts
            cpinfo = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == companys,
                                                          CompanyProfessionalFeed.specialty == specialty,
                                                          CompanyProfessionalFeed.year == yyear).first()
            print cpinfo
            cpinfolist = [cpinfo.specialty, cpinfo.professional_fit, cpinfo.students_kills_mastery,
                          cpinfo.professional_satisfaction, cpinfo.student_satisfaction, cpinfo.evaluate, cpinfo.year]
            # form.evaluate.render_kw['value'] = csinfo.evaluate
            form.evaluate.data = cpinfo.evaluate
            return render_template('user/editcpfeed.html', form=form, cpinfolist=cpinfolist)
    if request.method == 'POST':
        specialty = request.args.get('specialty')
        print specialty
        yyear = request.args.get('yyear')
        companys = current_user.accounts
        print yyear
        professional_fit = form.professional_fit.data
        students_kills_mastery = form.students_kills_mastery.data
        professional_satisfaction = form.professional_satisfaction.data
        student_satisfaction = form.student_satisfaction.data
        evaluate = form.evaluate.data
        cp = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == companys,
                                                  CompanyProfessionalFeed.specialty == specialty,
                                                  CompanyProfessionalFeed.year == yyear).first()
        print cp
        cp.professional_fit = professional_fit
        cp.students_kills_mastery = students_kills_mastery
        cp.professional_satisfaction = professional_satisfaction
        cp.student_satisfaction = student_satisfaction
        cp.evaluate = evaluate
        db.session.commit()
        return redirect(url_for('user.cpfeedback', specialty=specialty))


@user.route('/selectyearcpfeed', methods=['GET', 'POST'])
@login_required
def selectyearcpfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    yearlist = sorted(enum.getyear(), reverse=True)
    if request.method == 'GET':
        if request.args.get("errors"):
            return render_template('user/selectyearcpfeed.html', errors=request.args.get("errors"),
                                   yearlist=yearlist)
        return render_template('user/selectyearcpfeed.html', yearlist=yearlist)


@user.route('/selectnextyearcpfeed', methods=['GET', 'POST'])
@login_required
def selectnextyearcpfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get("nnext"):
            yyear = request.args.get("nnext")
            print yyear
            cpinfo = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == current_user.accounts,
                                                          CompanyProfessionalFeed.year == yyear).all()
            if not cpinfo:
                return redirect(url_for('user.selectyearcpfeed', errors=yyear + '年下面没有您填写的学生问卷，请重新选择年度'))
            else:
                specialtylist = []
                for i in cpinfo:
                    sp = Specialty.query.filter(Specialty.specialty_name == i.specialty).first()
                    specialtylist.append((sp.school, i.specialty))
                return render_template('user/selectnextyearcpfeed.html', specialtylist=specialtylist, year=yyear,
                                       errors=request.args.get("errors"))
        else:
            return redirect(url_for('user.selectyearcpfeed'))


@user.route('/checkyearcpfeed', methods=['GET', 'POST'])
@login_required
def checkyearcpfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialty') and request.args.get('check') == 'True' and request.args.get('year'):
            yyear = request.args.get('year')
            cpfeedinfo = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == current_user.accounts,
                                                              CompanyProfessionalFeed.year == yyear,
                                                              CompanyProfessionalFeed.specialty == request.args.get(
                                                                  'specialty')).first()
            return render_template('user/checkyearcpfeed.html', datainfo=cpfeedinfo)
        else:
            return redirect(url_for('user.selectyearcpfeed', errors='参数错误'))


@user.route('/delcpfeed', methods=['GET', 'POST'])
@login_required
def delcpfeed():
    if not (current_user.category == 1):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialty') and request.args.get('del') == 'True' and request.args.get('year'):
            yyear = request.args.get('year')
            cpfeedinfo = CompanyProfessionalFeed.query.filter(CompanyProfessionalFeed.company == current_user.accounts,
                                                              CompanyProfessionalFeed.year == yyear,
                                                              CompanyProfessionalFeed.specialty == request.args.get(
                                                                  'specialty')).first()
            db.session.delete(cpfeedinfo)
            db.session.commit()
        if request.args.get('tt') == 'True':
            return redirect(url_for('user.cpfeedback', specialty=request.args.get('specialty')))
        else:
            return redirect(url_for('user.selectyearcpfeed'))


@user.route('/student_basic_info_wordcloud', methods=['GET', 'POST'])
@login_required
def student_basic_info_wordcloud():
    student_info = Basicinfo.query.filter().all()
    if not student_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入基本信息，无法查看'))
    page = Page()
    if request.method == 'GET':
        companylist = []
        positionlist = []
        for i in student_info:
            companylist.append(i.company)
            positionlist.append(i.position)
        cllist = collections.Counter(companylist)
        pllist = collections.Counter(positionlist)
        cname = []
        cvalue = []
        pname = []
        pvalue = []
        for j in cllist.keys():
            cname.append(j)
            cvalue.append(cllist[j])
        for j in pllist.keys():
            pname.append(j)
            pvalue.append(pllist[j])
        pie = Pie("全部学生就职公司比例图", title_pos='center', width=1000)
        pie.add(
            "",
            cname,
            cvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentbasicinfowordcloud.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        companylist = []
        positionlist = []
        piename = "全部学生就职公司比例图"
        if specialty == '选择专业' and grade == '选择年级':
            student_info = Basicinfo.query.all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业学生就职公司比例图'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业' + grade + '级学生就职公司比例图'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty, Basicinfo.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename = grade + '级学生就职公司比例图'
            student_info = Basicinfo.query.filter(Basicinfo.grade == grade).all()
        for i in student_info:
            companylist.append(i.company)
            positionlist.append(i.position)
        cllist = collections.Counter(companylist)
        pllist = collections.Counter(positionlist)
        cname = []
        cvalue = []
        pname = []
        pvalue = []
        for j in cllist.keys():
            cname.append(j)
            cvalue.append(cllist[j])
        for j in pllist.keys():
            pname.append(j)
            pvalue.append(pllist[j])
        pie = Pie(piename, title_pos='center', width=1000)
        pie.add(
            "",
            cname,
            cvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentbasicinfowordcloud.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/student_year_salary_pie_all', methods=['GET', 'POST'])
@login_required
def student_year_salary_pie_all():
    student_info = Basicinfo.query.filter().all()
    page = Page()
    if not student_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入基本信息，无法查看'))
    if request.method == 'GET':
        yearsalarylist = []
        for i in student_info:
            yearsalarylist.append(i.yearly_salary)
        ylist = collections.Counter(yearsalarylist)
        allname = []
        allvalue = []
        for j in ylist.keys():
            allname.append(j)
            allvalue.append(ylist[j])
        pie = Pie("全部学生年薪比例图", title_pos='center', width=1000)
        pie.add(
            "",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentyearsalarypie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        yearsalarylist = []
        piename = "全部学生年薪比例图"
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            student_info = Basicinfo.query.all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业学生年薪比例图'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业' + grade + '级学生年薪比例图'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty, Basicinfo.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename = grade + '级学生年薪比例图'
            student_info = Basicinfo.query.filter(Basicinfo.grade == grade).all()
        for i in student_info:
            yearsalarylist.append(i.yearly_salary)
        ylist = collections.Counter(yearsalarylist)
        allname = []
        allvalue = []
        for j in ylist.keys():
            allname.append(j)
            allvalue.append(ylist[j])
        pie = Pie(piename, title_pos='center', width=1000)
        pie.add(
            "",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentyearsalarypie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/student_occupation_pie_all', methods=['GET', 'POST'])
@login_required
def student_occupation_pie_all():
    student_info = Basicinfo.query.filter().all()
    page = Page()
    if not student_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入基本信息，无法查看'))
    if request.method == 'GET':
        occupationlist = []
        for i in student_info:
            occupationlist.append(i.relevant)
        olist = collections.Counter(occupationlist)
        allname = []
        allvalue = []

        for j in olist.keys():
            allname.append(j)
            allvalue.append(olist[j])
        pie = Pie("全部学生职业相关度比例图", title_pos='center', width=1000)
        pie.add(
            "",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentoccupationpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        occupationlist = []
        piename = "全部学生职业相关度比例图"
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            student_info = Basicinfo.query.all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业学生职业相关度比例图'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业' + grade + '级学生职业相关度比例图'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty, Basicinfo.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename = grade + '级学生职业相关度比例图'
            student_info = Basicinfo.query.filter(Basicinfo.grade == grade).all()
        for i in student_info:
            occupationlist.append(i.relevant)
        olist = collections.Counter(occupationlist)
        allname = []
        allvalue = []

        for j in olist.keys():
            allname.append(j)
            allvalue.append(olist[j])
        pie = Pie(piename, title_pos='center', width=1000)
        pie.add(
            "",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentoccupationpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/student_quit_pie', methods=['GET', 'POST'])
@login_required
def student_quit_pie():
    student_info = Basicinfo.query.filter().all()
    page = Page()
    if not student_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入基本信息，无法查看'))
    if request.method == 'GET':
        quitlist = []
        quitreasonlist = []
        for i in student_info:
            quitlist.append(i.is_quit)
            quitreasonlist.append(i.quit_reason)
        qlist = collections.Counter(quitlist)
        qrlist = collections.Counter(quitreasonlist)
        allname = []
        allvalue = []
        allrname = []
        allrvalue = []

        for j in qlist.keys():
            allname.append(j)
            allvalue.append(qlist[j])

        for k in qrlist.keys():
            allrname.append(k)
            allrvalue.append(qrlist[k])
        pie = Pie("现在职情况", title_pos='center', width=1000)
        pie2 = Pie("离职（包括上次离职）原因", title_pos='center', width=1000)
        pie.add(
            "现在职情况",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "离职（包括以前）原因",
            allrname,
            allrvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentquitpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(), errors=request.args.get("errors"),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        quitlist = []
        quitreasonlist = []
        piename1 = "现在职情况"
        piename2 = "离职（包括上次离职）原因"
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            student_info = Basicinfo.query.all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename1 = specialtyname + '专业现在职情况'
            piename2 = specialtyname + '专业离职（包括上次离职）原因'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename1 = specialtyname + '专业' + grade + '级现在职情况'
            piename2 = specialtyname + '专业' + grade + '级离职（包括上次离职）原因'
            student_info = Basicinfo.query.filter(Basicinfo.specialty == specialty, Basicinfo.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename1 = grade + '级现在职情况'
            piename1 = grade + '级离职（包括上次离职）原因'
            student_info = Basicinfo.query.filter(Basicinfo.grade == grade).all()
        for i in student_info:
            quitlist.append(i.is_quit)
            quitreasonlist.append(i.quit_reason)
        qlist = collections.Counter(quitlist)
        qrlist = collections.Counter(quitreasonlist)
        allname = []
        allvalue = []
        allrname = []
        allrvalue = []

        for j in qlist.keys():
            allname.append(j)
            allvalue.append(qlist[j])

        for k in qrlist.keys():
            allrname.append(k)
            allrvalue.append(qrlist[k])
        pie = Pie(piename1, title_pos='center', width=1000)
        pie2 = Pie(piename2, title_pos='center', width=1000)
        pie.add(
            "现在职情况",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "离职（包括以前）原因",
            allrname,
            allrvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentquitpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(), errors=request.args.get("errors"),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/student_satisfaction_pie', methods=['GET', 'POST'])
@login_required
def student_satisfaction_pie():
    studentfeed_info = Feedback.query.filter().all()
    page = Page()
    if not studentfeed_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入反馈信息，无法查看'))
    if request.method == 'GET':
        feedlist = []
        zylist = []
        qylist = []
        hylist = []
        for i in studentfeed_info:
            feedlist.append(i.career_satisfaction)
            zylist.append(i.take_office)
            qylist.append(i.corporate_satisfaction)
            hylist.append(i.industry_satisfaction)
        flist = collections.Counter(feedlist)
        fzylist = collections.Counter(zylist)
        fqylist = collections.Counter(qylist)
        fhylist = collections.Counter(hylist)
        allname = []
        allvalue = []
        allzyname = []
        allzyvalue = []
        allqyname = []
        allqyvalue = []
        allhyname = []
        allhyvalue = []

        for j in flist.keys():
            allname.append(j)
            allvalue.append(flist[j])

        for k in fzylist.keys():
            allzyname.append(k)
            allzyvalue.append(fzylist[k])

        for i in fqylist.keys():
            allqyname.append(i)
            allqyvalue.append(fqylist[i])

        for i in fhylist.keys():
            allhyname.append(i)
            allhyvalue.append(fhylist[i])

        pie = Pie("学生就职职业分布比例图", title_pos='center', width=1000)
        pie2 = Pie("学生对自己职业满意度比例图", title_pos='center', width=1000)
        pie3 = Pie("学生对所在企业满意度比例图", title_pos='center', width=1000)
        pie4 = Pie("学生对所在行业满意度比例图", title_pos='center', width=1000)
        pie.add(
            "职业分布",
            allzyname,
            allzyvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "职业满意度",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie3.add(
            "企业满意度",
            allqyname,
            allqyvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie4.add(
            "行业满意度",
            allhyname,
            allhyvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        page.add_chart(pie3)
        page.add_chart(pie4)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentzhiyepie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        feedlist = []
        zylist = []
        qylist = []
        hylist = []
        piename = "学生就职职业分布比例图"
        piename2 = "学生对自己职业满意度比例图"
        piename3 = "学生对所在企业满意度比例图"
        piename4 = "学生对所在行业满意度比例图"
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            studentfeed_info = Feedback.query.all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业学生就职职业分布比例图'
            studentfeed_info = Feedback.query.filter(Feedback.specialty == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename = specialtyname + '专业' + grade + '级学生就职职业分布比例图'
            studentfeed_info = Feedback.query.filter(Feedback.specialty == specialty, Feedback.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename = grade + '级学生就职职业分布比例图'
            studentfeed_info = Feedback.query.filter(Feedback.grade == grade).all()
        for i in studentfeed_info:
            feedlist.append(i.career_satisfaction)
            zylist.append(i.take_office)
            qylist.append(i.corporate_satisfaction)
            hylist.append(i.industry_satisfaction)
        flist = collections.Counter(feedlist)
        fzylist = collections.Counter(zylist)
        fqylist = collections.Counter(qylist)
        fhylist = collections.Counter(hylist)
        allname = []
        allvalue = []
        allzyname = []
        allzyvalue = []
        allqyname = []
        allqyvalue = []
        allhyname = []
        allhyvalue = []

        for j in flist.keys():
            allname.append(j)
            allvalue.append(flist[j])

        for k in fzylist.keys():
            allzyname.append(k)
            allzyvalue.append(fzylist[k])

        for i in fqylist.keys():
            allqyname.append(i)
            allqyvalue.append(fqylist[i])

        for i in fhylist.keys():
            allhyname.append(i)
            allhyvalue.append(fhylist[i])

        pie = Pie(piename, title_pos='center', width=1000)
        pie2 = Pie(piename2, title_pos='center', width=1000)
        pie3 = Pie(piename3, title_pos='center', width=1000)
        pie4 = Pie(piename4, title_pos='center', width=1000)
        pie.add(
            "职业分布",
            allzyname,
            allzyvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "职业满意度",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie3.add(
            "企业满意度",
            allqyname,
            allqyvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie4.add(
            "行业满意度",
            allhyname,
            allhyvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        page.add_chart(pie3)
        page.add_chart(pie4)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentzhiyepie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/student_school_pie', methods=['GET', 'POST'])
@login_required
def student_school_pie():
    ss_info = SSFeedback.query.filter().all()
    page = Page()
    if not ss_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入反馈信息，无法查看'))
    if request.method == 'GET':
        quitlist = []
        quitreasonlist = []
        for i in ss_info:
            quitlist.append(i.course_satisfaction)
            quitreasonlist.append(i.course_size)
        qlist = collections.Counter(quitlist)
        qrlist = collections.Counter(quitreasonlist)
        allname = []
        allvalue = []
        allrname = []
        allrvalue = []

        for j in qlist.keys():
            allname.append(j)
            allvalue.append(qlist[j])

        for k in qrlist.keys():
            allrname.append(k)
            allrvalue.append(qrlist[k])
        pie = Pie("学生对课程修习难度评价", title_pos='center', width=1000)
        pie2 = Pie("学生对课程量评价", title_pos='center', width=1000)
        pie.add(
            "学生对课程修习难度评价",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "学生对课程量评价",
            allrname,
            allrvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentschoolpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(), errors=request.args.get("errors"),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        quitlist = []
        quitreasonlist = []
        piename1 = "学生对课程修习难度评价"
        piename2 = "学生对课程量评价"
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            ss_info = SSFeedback.query.filter().all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename1 = specialtyname + '专业学生对课程修习难度评价'
            piename2 = specialtyname + '专业学生对课程量评价'
            ss_info = SSFeedback.query.filter(SSFeedback.specialty_id == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename1 = specialtyname + '专业' + grade + '级学生对课程修习难度评价'
            piename2 = specialtyname + '专业' + grade + '级学生对课程量评价'
            ss_info = SSFeedback.query.filter(SSFeedback.specialty_id == specialty, SSFeedback.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename1 = grade + '级学生对课程修习难度评价'
            piename1 = grade + '级学生对课程量评价'
            ss_info = SSFeedback.query.filter(SSFeedback.grade == grade).all()
        for i in ss_info:
            quitlist.append(i.course_satisfaction)
            quitreasonlist.append(i.course_size)
        qlist = collections.Counter(quitlist)
        qrlist = collections.Counter(quitreasonlist)
        allname = []
        allvalue = []
        allrname = []
        allrvalue = []

        for j in qlist.keys():
            allname.append(j)
            allvalue.append(qlist[j])

        for k in qrlist.keys():
            allrname.append(k)
            allrvalue.append(qrlist[k])
        pie = Pie(piename1, title_pos='center', width=1000)
        pie2 = Pie(piename2, title_pos='center', width=1000)
        pie.add(
            "学生对课程修习难度评价",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "学生对课程量评价",
            allrname,
            allrvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentschoolpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(), errors=request.args.get("errors"),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/student_school_work_pie', methods=['GET', 'POST'])
@login_required
def student_school_work_pie():
    ss_info = SSFeedback.query.filter().all()
    page = Page()
    if not ss_info:
        return redirect(url_for('user.index', errors=u'还未有学生录入反馈信息，无法查看'))
    if request.method == 'GET':
        quitlist = []
        quitreasonlist = []
        for i in ss_info:
            quitlist.append(i.school_by_work)
            quitreasonlist.append(i.school_class_work)
        qlist = collections.Counter(quitlist)
        qrlist = collections.Counter(quitreasonlist)
        allname = []
        allvalue = []
        allrname = []
        allrvalue = []

        for j in qlist.keys():
            allname.append(j)
            allvalue.append(qlist[j])

        for k in qrlist.keys():
            allrname.append(k)
            allrvalue.append(qrlist[k])
        pie = Pie("工作中用到学校课程的比例", title_pos='center', width=1000)
        pie2 = Pie("学校课程对工作选择的影响", title_pos='center', width=1000)
        pie.add(
            "工作中用到学校课程的比例",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "学校课程对工作选择的影响",
            allrname,
            allrvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentschoolworkpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(), errors=request.args.get("errors"),
                               specialtylist=specialtylist, gradelist=gradelist)
    if request.method == 'POST':
        quitlist = []
        quitreasonlist = []
        piename1 = "工作中用到学校课程的比例"
        piename2 = "学校课程对工作选择的影响"
        specialty = request.form.get('specialty')
        grade = request.form.get('grade')
        if specialty == '选择专业' and grade == '选择年级':
            ss_info = SSFeedback.query.filter().all()
        elif specialty != '选择专业' and grade == '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename1 = specialtyname + '专业学生工作中用到学校课程的比例'
            piename2 = specialtyname + '专业学校课程对工作选择的影响'
            ss_info = SSFeedback.query.filter(SSFeedback.specialty_id == specialty).all()
        elif specialty != '选择专业' and grade != '选择年级':
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialty).first().specialty_name
            piename1 = specialtyname + '专业' + grade + '级学生工作中用到学校课程的比例'
            piename2 = specialtyname + '专业' + grade + '级学校课程对工作选择的影响'
            ss_info = SSFeedback.query.filter(SSFeedback.specialty_id == specialty, SSFeedback.grade == grade).all()
        elif specialty == '选择专业' and grade != '选择年级':
            piename1 = grade + '级学生工作中用到学校课程的比例'
            piename1 = grade + '级学校课程对工作选择的影响'
            ss_info = SSFeedback.query.filter(SSFeedback.grade == grade).all()
        for i in ss_info:
            quitlist.append(i.school_by_work)
            quitreasonlist.append(i.school_class_work)
        qlist = collections.Counter(quitlist)
        qrlist = collections.Counter(quitreasonlist)
        allname = []
        allvalue = []
        allrname = []
        allrvalue = []

        for j in qlist.keys():
            allname.append(j)
            allvalue.append(qlist[j])

        for k in qrlist.keys():
            allrname.append(k)
            allrvalue.append(qrlist[k])
        pie = Pie(piename1, title_pos='center', width=1000)
        pie2 = Pie(piename2, title_pos='center', width=1000)
        pie.add(
            "工作中用到学校课程的比例",
            allname,
            allvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie2.add(
            "学校课程对工作选择的影响",
            allrname,
            allrvalue,
            center=[50, 50],
            is_random=True,
            radius=[30, 70],
            rosetype="radius",
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        page.add_chart(pie)
        page.add_chart(pie2)
        specialtylist = []
        specialty = Specialty.query.all()
        for i in specialty:
            specialtylist.append((i.specialty_name, i.specialty_id))
        gradelist = sorted(enum.getgrade(), reverse=True)
        return render_template('user/studentschoolworkpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(), errors=request.args.get("errors"),
                               specialtylist=specialtylist, gradelist=gradelist)


@user.route('/selectgrade', methods=['GET', 'POST'])
@login_required
def selectgrade():
    if request.method == 'GET':
        gradelist = enum.getgrade()
        if request.args.get("errors"):
            return render_template('user/selectgrade.html', gradelist=sorted(gradelist, reverse=True),
                                   errors=request.args.get("errors"))
        return render_template('user/selectgrade.html', gradelist=sorted(gradelist, reverse=True))


@user.route('/addgrade', methods=['GET', 'POST'])
@login_required
def addgrade():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('user/addgrade.html')
    if request.method == 'POST':
        fgrade = request.form.get('grade')
        gradelist = enum.getgrade()
        if fgrade in gradelist:
            return render_template('user/addgrade.html', errors='要添加的年级已存在')
        else:
            newgrade = Grade(grade=fgrade)
            db.session.add(newgrade)
            db.session.commit()
            return redirect(url_for('user.selectgrade'))


@user.route('/delgrade', methods=['GET', 'POST'])
@login_required
def delgrade():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('grade') and request.args.get('del') == 'True':
            ginfo = Grade.query.filter(Grade.grade == request.args.get('grade')).first()
            db.session.delete(ginfo)
            db.session.commit()
        return redirect(url_for('user.selectgrade'))


@user.route('/selectyear', methods=['GET', 'POST'])
@login_required
def selectyear():
    if request.method == 'GET':
        yearlist = enum.getyear()
        if request.args.get("errors"):
            return render_template('user/selectyear.html', yearlist=sorted(yearlist, reverse=True),
                                   errors=request.args.get("errors"))
        return render_template('user/selectyear.html', yearlist=sorted(yearlist, reverse=True))


@user.route('/addyear', methods=['GET', 'POST'])
@login_required
def addyear():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('user/addyear.html')
    if request.method == 'POST':
        fyear = request.form.get('year')
        yearlist = enum.getyear()
        if fyear in yearlist:
            return render_template('user/addyear.html', errors='要添加的年度已存在')
        else:
            newyear = Year(year=fyear)
            db.session.add(newyear)
            db.session.commit()
            return redirect(url_for('user.selectyear'))


@user.route('/delyear', methods=['GET', 'POST'])
@login_required
def delyear():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('year') and request.args.get('del') == 'True':
            yinfo = Year.query.filter(Year.year == request.args.get('year')).first()
            db.session.delete(yinfo)
            db.session.commit()
        return redirect(url_for('user.selectgrade'))


@user.route('/selectspecialtyforability', methods=['GET', 'POST'])
@login_required
def selectspecialtyforability():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        spinfo = Specialty.query.all()
        specialtylist = []
        for i in spinfo:
            specialtylist.append((i.specialty_name, i.school, i.specialty_id, i.school_id))
        return render_template('user/selectspecialtyforability.html', specialtylist=specialtylist)


@user.route('/editforabilitys', methods=['GET', 'POST'])
@login_required
def editforabilitys():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('edit') == 'True':
            specialtyid = request.args.get('specialtyid')
            ainfo = AbilityCategory.query.filter(AbilityCategory.specialty == request.args.get('specialtyid')).all()
            abilitycategorylist = []
            for i in ainfo:
                sp = Specialty.query.filter(Specialty.specialty_id == i.specialty).first()
                abilitycategorylist.append((i.specialty, i.ability, sp.specialty_name, i.ability_weight))
            return render_template('user/editforability.html', abilitycategorylist=abilitycategorylist,
                                   specialtyid=specialtyid)


@user.route('/addabilityweight', methods=['GET', 'POST'])
@login_required
def addabilityweight():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('ability') and request.args.get('editweight') == 'True':
            specialtyid = request.args.get('specialtyid')
            ability = request.args.get('ability')
            specialtyname = Specialty.query.filter(Specialty.specialty_id == specialtyid).first().specialty_name
            return render_template('user/addabilityweight.html', ability=ability, specialtyid=specialtyid,
                                   specialtyname=specialtyname)
    if request.method == 'POST':
        specialtyid = request.form.get('specialtyid')
        ability = request.form.get('ability')
        abilityweight = request.form.get('abilityweight')
        abilityinfo = AbilityCategory.query.filter(AbilityCategory.specialty == specialtyid,
                                                   AbilityCategory.ability == ability).first()
        abilityinfo.ability_weight = abilityweight
        db.session.commit()
        return redirect(url_for('user.selectspecialtyforability'))


@user.route('/addability', methods=['GET', 'POST'])
@login_required
def addability():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid'):
            specialtyid = request.args.get('specialtyid')
            return render_template('user/addability.html', specialtyid=specialtyid)
    if request.method == 'POST':
        fspecialtyid = request.form.get('specialtyid')
        print fspecialtyid
        fability = request.form.get('ability')
        abilitylist = []
        allability = AbilityCategory.query.filter(AbilityCategory.specialty == fspecialtyid).all()
        for i in allability:
            abilitylist.append(i.ability)
        if fability in abilitylist:
            return render_template('user/addability.html', specialtyid=fspecialtyid, errors='要添加的能力已存在')
        else:
            newability = AbilityCategory(specialty=fspecialtyid, ability=fability, ability_weight=1.0)
            db.session.add(newability)
            db.session.commit()
            return redirect(url_for('user.selectspecialtyforability'))


@user.route('/delability', methods=['GET', 'POST'])
@login_required
def delability():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('ability') and request.args.get('del') == 'True':
            info = AbilityCategory.query.filter(AbilityCategory.specialty == request.args.get('specialtyid'),
                                                AbilityCategory.ability == request.args.get('ability')).first()

            db.session.delete(info)
            db.session.commit()
        return redirect(url_for('user.selectspecialtyforability'))


@user.route('/checkability', methods=['GET', 'POST'])
@login_required
def checkability():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('ability') and request.args.get('check') == 'True':
            infolist = []
            sp = Specialty.query.filter(Specialty.specialty_id == request.args.get('specialtyid')).first()
            info = AbilityClassification.query.filter(
                AbilityClassification.specialty == request.args.get('specialtyid'),
                AbilityClassification.kc_classification == request.args.get('ability'))
            for i in info:
                infolist.append((i.specialty, sp.specialty_name, i.kc_classification, i.kcname, i.kccode, i.kc_weight))
            return render_template('user/checkability.html', infolist=infolist)


@user.route('/selectspecialtyforclass', methods=['GET', 'POST'])
@login_required
def selectspecialtyforclass():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        spinfo = Specialty.query.all()
        specialtylist = []
        for i in spinfo:
            specialtylist.append((i.specialty_name, i.school, i.specialty_id, i.school_id))
        return render_template('user/selectspecialtyforclass.html', specialtylist=specialtylist)


@user.route('/editforclass', methods=['GET', 'POST'])
@login_required
def editforclass():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('edit') == 'True':
            infolist = []
            sp = Specialty.query.filter(Specialty.specialty_id == request.args.get('specialtyid')).first()
            info = AbilityClassification.query.filter(
                AbilityClassification.specialty == request.args.get('specialtyid'))
            for i in info:
                infolist.append((i.specialty, sp.specialty_name, i.kc_classification, i.kcname, i.kccode, i.kc_weight))
            return render_template('user/editforclass.html', infolist=infolist)


@user.route('/editabilityclass', methods=['GET', 'POST'])
@login_required
def editabilityclass():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('kccode') and request.args.get('edit') == 'True':
            spabilit = AbilityCategory.query.filter(AbilityCategory.specialty == request.args.get('specialtyid')).all()
            kcinfo = AbilityClassification.query.filter(
                AbilityClassification.specialty == request.args.get('specialtyid'),
                AbilityClassification.kccode == request.args.get('kccode')).first()
            kcname = kcinfo.kcname
            abilitlist = []
            for i in spabilit:
                abilitlist.append(i.ability)
            return render_template('user/editabilityclass.html', abilitlist=abilitlist,
                                   specialtyid=request.args.get('specialtyid'), kccode=request.args.get('kccode'),
                                   kcname=kcname)
    if request.method == 'POST':
        specialtyid = request.form.get('specialtyid')
        kccode = request.form.get('kccode')
        kcclassification = request.form.get('kcclassification')
        kcweight = request.form.get('kcweight')
        abinfo = AbilityClassification.query.filter(AbilityClassification.specialty == specialtyid,
                                                    AbilityClassification.kccode == kccode).first()

        abinfo.kc_classification = kcclassification
        abinfo.kc_weight = float(kcweight)
        db.session.commit()
        return redirect(url_for('user.editforclass', specialtyid=specialtyid, edit='True'))


@user.route('/selectspecialtyforfx', methods=['GET', 'POST'])
@login_required
def selectspecialtyforfx():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        spinfo = Specialty.query.all()
        specialtylist = []
        for i in spinfo:
            specialtylist.append((i.specialty_name, i.school, i.specialty_id, i.school_id))
        return render_template('user/selectspecialtyforfx.html', specialtylist=specialtylist)


@user.route('/selectgradeforfx', methods=['GET', 'POST'])
@login_required
def selectgradeforfx():
    if not (current_user.category == 0):
        return redirect(url_for('index'))

    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('edit') == 'True':
            conn = pymysql.connect()
            cursor = conn.cursor()
            sql = 'select grade from achievement ' + 'where specialty=' + request.args.get(
                'specialtyid') + ' group by grade;'
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            gradelist = []
            for i in results:
                gradelist.append(i[0])
            return render_template('user/selectsgradeforfx.html', gradelist=sorted(gradelist, reverse=True),
                                   specialtyid=request.args.get('specialtyid'))


@user.route('/selectspecialtyforfxall', methods=['GET', 'POST'])
@login_required
def selectspecialtyforfxall():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        spinfo = Specialty.query.all()
        specialtylist = []
        for i in spinfo:
            specialtylist.append((i.specialty_name, i.school, i.specialty_id, i.school_id))
        return render_template('user/selectspecialtyforfxall.html', specialtylist=specialtylist)


@user.route('/selectgradeforfxall', methods=['GET', 'POST'])
@login_required
def selectgradeforfxall():
    if not (current_user.category == 0):
        return redirect(url_for('index'))

    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('edit') == 'True':
            conn = pymysql.connect()
            cursor = conn.cursor()
            sql = 'select grade from achievement ' + 'where specialty=' + request.args.get(
                'specialtyid') + ' group by grade;'
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            gradelist = []
            for i in results:
                gradelist.append(i[0])
            return render_template('user/selectsgradeforfxall.html', gradelist=sorted(gradelist, reverse=True),
                                   specialtyid=request.args.get('specialtyid'))


@user.route('/checkfx', methods=['GET', 'POST'])
@login_required
def checkfx():
    if request.args.get('specialtyid') and request.args.get('grade') and request.args.get('check') == 'True':
        alllist = []
        allxstudent = []
        specialtyid = request.args.get('specialtyid')
        grade = request.args.get('grade')
        abilitycategory = AbilityCategory.query.filter(AbilityCategory.specialty == specialtyid).all()
        abilitycategorylist = []
        page = Page()
        line = Line("能力积分折线图", height=800, width=1500)
        for i in abilitycategory:
            abilitycategorylist.append(i.ability)
        for j in abilitycategorylist:
            print j
            abilityclassification = AbilityClassification.query.filter(
                AbilityClassification.kc_classification == j, AbilityClassification.specialty == specialtyid).all()
            classlist = []
            classcodeweight = []
            for kc in abilityclassification:
                classlist.append(kc.kcname)
                classcodeweight.append((kc.kccode, kc.kc_weight))
            specifiedvaluelist = []
            classstr = ''
            for k in range(len(classcodeweight)):
                classstr = classstr + classcodeweight[k][0] + ','
            classstr = classstr + 'student_num,name'
            print classstr
            sql = 'select ' + classstr + ' from achievement where specialty=' + specialtyid + ' and grade=' + grade + ';'
            print sql
            conn = pymysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            for l in results:
                nvalue = float(0.0)
                for n in range(len(classlist)):
                    weight = float(classcodeweight[n][1])
                    if l[n] is None:
                        vvaule = 0
                    else:
                        vvaule = l[n]
                    nvalue = nvalue + (weight * vvaule)

                nnn = len(classlist)
                # student = Student.query.filter(Student.student_num == l[nnn]).first()
                # studentname = student.name
                studentname = l[nnn + 1]
                nvalue2 = '%.2f' % nvalue
                specifiedvaluelist.append((l[nnn], studentname, nvalue2))
            xstudent = []
            yvalue = []
            for p in specifiedvaluelist:
                xstudent.append(p[0] + p[1])
                yvalue.append(p[2])
            allxstudent = xstudent
            alllist.append(yvalue)
            line.add(j, xstudent, yvalue, mark_point=["average", "min", "max"], is_label_show=True, yaxis_min=200,
                     legend_text_size=20, xaxis_rotate=90)
        page.add_chart(line)
        if request.args.get('isall') == 'True':
            allability = AbilityCategory.query.all()
            allabilitylist = []
            allyvalue = []
            for t in allability:
                allabilitylist.append(t.ability_weight)
            for i in range(len(allxstudent)):
                yyval = 0.0
                yyval = float(yyval)
                for j in range(len(alllist)):
                    vy = float(alllist[j][i])
                    vyw = float(allabilitylist[j])
                    yyval = yyval + (vy * vyw)
                yyval2 = '%.2f' % yyval
                allyvalue.append(yyval2)
            pageall = Page()
            lineall = Line("综合能力积分折线图", height=600, width=1500)
            lineall.add("综合能力加权得分", allxstudent, allyvalue, mark_point=["average", "min", "max"], is_label_show=True,
                        yaxis_min=2000,
                        legend_text_size=20, xaxis_rotate=90)
            pageall.add_chart(lineall)
            return render_template('user/checkfx.html',
                                   myechart=pageall.render_embed(),
                                   host=REMOTE_HOST,
                                   script_list=pageall.get_js_dependencies())
        else:
            return render_template('user/checkfx.html',
                                   myechart=page.render_embed(),
                                   host=REMOTE_HOST,
                                   script_list=page.get_js_dependencies())


@user.route('/selectspecialtyforfxss', methods=['GET', 'POST'])
@login_required
def selectspecialtyforfxss():
    if not (current_user.category == 0):
        return redirect(url_for('index'))
    if request.method == 'GET':
        spinfo = Specialty.query.all()
        specialtylist = []
        for i in spinfo:
            specialtylist.append((i.specialty_name, i.school, i.specialty_id, i.school_id))
        return render_template('user/selectspecialtyforfxss.html', specialtylist=specialtylist)


@user.route('/selectgradeforfxss', methods=['GET', 'POST'])
@login_required
def selectgradeforfxss():
    if not (current_user.category == 0):
        return redirect(url_for('index'))

    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('edit') == 'True':
            conn = pymysql.connect()
            cursor = conn.cursor()
            sql = 'select grade from achievement ' + 'where specialty=' + request.args.get(
                'specialtyid') + ' group by grade;'
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            gradelist = []
            nowyear = datetime.datetime.now().year
            for i in results:
                if int(i[0]) >= (int(nowyear) - 4):
                    gradelist.append(i[0])
            return render_template('user/selectsgradeforfxss.html', gradelist=sorted(gradelist, reverse=True),
                                   specialtyid=request.args.get('specialtyid'))


@user.route('/checkfxfornextstudentinfo', methods=['GET', 'POST'])
@login_required
def checkfxfornextstudentinfo():
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('grade') and request.args.get('check') == 'True':
            specialtyid = request.args.get('specialtyid')
            grade = request.args.get('grade')
            print specialtyid + grade
            studentlist = []
            allstudent = Student.query.filter(Student.specialty_id == specialtyid, Student.grade == grade).all()
            for i in allstudent:
                studentlist.append((i.student_num, i.name, i.specialty))
            if request.args.get('errors'):
                return render_template('user/checkfxfornextstudentinfo.html', specialtyid=specialtyid,
                                       studentlist=studentlist, grade=grade, errors=request.args.get('errors'))
            return render_template('user/checkfxfornextstudentinfo.html', specialtyid=specialtyid,
                                   studentlist=studentlist, grade=grade)


@user.route('/selectabilityforfx', methods=['GET', 'POST'])
@login_required
def selectabilityforfx():
    if request.method == 'GET':
        if request.args.get('specialtyid') and request.args.get('grade') and request.args.get('check') == 'True':
            specialtyid = request.args.get('specialtyid')
            grade = request.args.get('grade')
            studentnum = request.args.get('studentnum')
            abilitylist = []
            allabilitycate = AbilityCategory.query.filter(AbilityCategory.specialty == specialtyid).all()
            for i in allabilitycate:
                abilitylist.append(i.ability)
            print abilitylist
            conn = pymysql.connect()
            cursor = conn.cursor()
            sql = 'select * from achievement ' + 'where student_num=' + studentnum + ';'
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            if not results:
                return redirect(
                    url_for('user.checkfxfornextstudentinfo', specialtyid=specialtyid, grade=grade, check='True',
                            errors=u'此学生没有录入成绩，请重新选择！'))

            return render_template('user/selectabilityforfx.html', specialtyid=specialtyid, studentnum=studentnum,
                                   grade=grade, abilitylist=abilitylist)


@user.route('/checkfxforstudent', methods=['GET', 'POST'])
@login_required
def checkfxforstudent():
    if request.method == 'GET':
        specialtyid = request.args.get('specialtyid')
        grade = request.args.get('grade')
        abilitycategory = AbilityCategory.query.filter(AbilityCategory.specialty == specialtyid).all()
        abilitycategorylist = []
        for i in abilitycategory:
            abilitycategorylist.append(i.ability)

        grade1 = str((int(grade) - 1))
        grade2 = str((int(grade) - 2))
        gradell = [grade1, grade2]
        print gradell

        studentnextnum = request.args.get('studentnum')
        allgradevalue = []
        for x in gradell:
            j = request.args.get('ability')
            if j:
                print j
                abilityclassification = AbilityClassification.query.filter(
                    AbilityClassification.kc_classification == j, AbilityClassification.specialty == specialtyid).all()
                classlist = []
                classcodeweight = []
                for kc in abilityclassification:
                    classlist.append(kc.kcname)
                    classcodeweight.append((kc.kccode, kc.kc_weight))
                # specifiedvaluelist = []

                classstr = ''
                for k in range(len(classcodeweight)):
                    classstr = classstr + classcodeweight[k][0] + ','
                classstr = classstr + 'student_num,name'
                print classstr

                sql = 'select ' + classstr + ' from achievement where specialty=' + specialtyid + ' and grade=' + x + ';'
                sqlnex = 'select ' + classstr + ' from achievement where student_num=' + studentnextnum + ';'
                print sql
                print sqlnex
                conn = pymysql.connect()
                cursor = conn.cursor()
                cursor.execute(sql)
                results = cursor.fetchall()

                cursor.execute(sqlnex)
                resultsnex = cursor.fetchall()

                cursor.close()
                conn.close()
                keyindex = []
                for o in resultsnex:
                    for n in range(len(classlist)):
                        if (o[n] is not None) and (o[n] != 0):
                            keyindex.append(n)

                    print keyindex

                nextvalue = float(0.0)
                for n in keyindex:
                    nweight = float(classcodeweight[n][1])
                    nvvaule = resultsnex[0][n]
                    nextvalue = nextvalue + (nweight * nvvaule)
                nnextvalue = '%.2f' % nextvalue
                nnextvalue = float(nnextvalue)
                studentnexvalue = (resultsnex[0][len(classlist)], resultsnex[0][len(classlist) + 1], nnextvalue)
                for l in results:
                    nvalue = float(0.0)
                    for n in keyindex:
                        weight = float(classcodeweight[n][1])
                        vvaule = l[n]
                        nvalue = nvalue + (weight * vvaule)

                    nnn = len(classlist)
                    # student = Student.query.filter(Student.student_num == l[nnn]).first()
                    # studentname = student.name
                    studentname = l[nnn + 1]
                    nvalue2 = '%.2f' % nvalue
                    allgradevalue.append((l[nnn], studentname, nvalue2))
                # print specifiedvaluelist
        print allgradevalue
        print studentnexvalue
        allabslist = []
        for i in allgradevalue:
            fvalue = float(i[2])
            svalue = float(studentnexvalue[2])
            absvalue = '%.2f' % abs(svalue - fvalue)
            allabslist.append((i[0], i[1], fvalue, absvalue))
        print allabslist
        tmplist = sorted(allabslist, key=lambda x: x[3])
        tmplist = tmplist[:5]
        allabsall = []
        for i in tmplist:
            conn = pymysql.connect()
            cursor = conn.cursor()
            sqlqx = 'select qx from achievement where student_num=' + i[0] + ';'
            cursor.execute(sqlqx)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            allabsall.append((i[0], i[1], i[2], results[0][0], i[3]))
        print allabsall
        return render_template('user/checkfxforstudent.html', allabsall=allabsall, studentnexvalue=studentnexvalue)
