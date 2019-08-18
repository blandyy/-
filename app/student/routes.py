# coding=utf-8
import pymysql
from flask import render_template, request, redirect, Flask, Blueprint, url_for
from flask_login import login_user, login_required, current_user, logout_user
from app.models import Student, Basicinfo, Feedback, Company, User, SSFeedback, AbilityCategory, AbilityClassification, \
    Specialty
from app import login_manager, db
from app.student import student
from app.form.login import LoginForm, StudentLoginForm
from app.form.feedback import FeedbackForm
from app.form.basicinfo import BasicInfoForm, FristBasicInfoForm
from app.form.ssfeedback import SSFeedbackFrom
import time
from app.util.cos_sim import cosine
import collections
from app.enum import enum
from app import login_manager, db, REMOTE_HOST
from pyecharts import Page, WordCloud, Pie, Line


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@student.before_request
def before_request():
    pass


@student.route('/index', methods=['GET', 'POST'])
@student.route('/', methods=['GET', 'POST'])
@login_required
def index():
    info = Basicinfo.query.filter(
        Basicinfo.student_num == current_user.accounts).first()
    if current_user.category == 4:
        return redirect(url_for('student.zxindex'))
    if info:
        return render_template('student/index.html', datainfo=info)
    else:
        return redirect(url_for('student.fristbasicinfo'))


@student.route('/zxindex', methods=['GET', 'POST'])
@login_required
def zxindex():
    stunum = Student.query.filter().count()
    print stunum
    num = 0
    if stunum:
        num = stunum
    else:
        num = 0
    return render_template('student/zxindex.html', errors=request.args.get("errors"), nnum=num)


@student.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = StudentLoginForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return render_template('student/login.html', form=form)
        users = User.query.filter(User.accounts == form.accounts.data).first()
        if users:
            is_passwd = users.check_password_hash(form.password.data)
            if is_passwd:
                login_user(users)
                if users.category == 4:
                    return redirect(url_for('student.zxindex'))
                else:
                    return redirect(url_for('student.index'))
            else:
                return render_template('student/login.html', form=form, errors='password error')
        else:
            return render_template('student/login.html', form=form, errors='user error')
    return render_template('student/login.html', form=form)


@student.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@student.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    info = Basicinfo.query.filter(
        Basicinfo.student_num == current_user.accounts).first()
    if not info:
        return redirect(url_for('student.fristbasicinfo'))
    feedform = FeedbackForm()
    form = FeedbackForm()
    if request.method == 'GET':
        stinfo = Feedback.query.filter(Feedback.student_num == current_user.accounts).first()
        print stinfo
        if stinfo:
            form.prize_winning.data = stinfo.prize_winning
            feedform.prize_winning.data = stinfo.prize_winning
            form.shengqian.data = stinfo.shengqian
            feedform.shengqian.data = stinfo.shengqian
            form.self_evaluation.data = stinfo.self_evaluation
            feedform.self_evaluation.data = stinfo.self_evaluation
            form.occupation.render_kw = {'value': stinfo.industry}
            feedform.occupation.render_kw = {'value': stinfo.industry}
            form.take_office.render_kw = {'value': stinfo.take_office}
            feedform.take_office.render_kw = {'value': stinfo.take_office}
        return render_template('student/feedback.html', form=feedform, errors=request.args.get("errors"))
    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return redirect(url_for('student.feedback'))
        feedbackf = Feedback.query.filter(
            Feedback.student_num == current_user.accounts).first()
        if feedbackf:
            foccupation = form.occupation.data
            fcareer_satisfaction = form.career_satisfaction.data
            fcorporate_satisfaction = form.corporate_satisfaction.data
            ftake_office = form.take_office.data
            findustry_satisfaction = form.industry_satisfaction.data
            fshengqian = form.shengqian.data
            fprize_winning = form.prize_winning.data
            fself_evaluation = form.self_evaluation.data
            finfo = Feedback.query.filter(
                Feedback.student_num == current_user.accounts).first()
            finfo.industry = foccupation
            finfo.career_satisfaction = fcareer_satisfaction
            finfo.corporate_satisfaction = fcorporate_satisfaction
            finfo.take_office = ftake_office
            finfo.shengqian = fshengqian
            finfo.industry_satisfaction = findustry_satisfaction
            finfo.prize_winning = fprize_winning
            finfo.self_evaluation = fself_evaluation
            finfo.yearly_salary = info.yearly_salary
            db.session.commit()
            return redirect(url_for('student.index'))
        else:
            print 'frist feedback'
            foccupation = form.occupation.data
            fcareer_satisfaction = form.career_satisfaction.data
            fcorporate_satisfaction = form.corporate_satisfaction.data
            ftake_office = form.take_office.data
            findustry_satisfaction = form.industry_satisfaction.data
            fshengqian = form.shengqian.data
            fprize_winning = form.prize_winning.data
            fself_evaluation = form.self_evaluation.data
            students_num = info.student_num
            icompany = info.company
            iyearly = info.yearly_salary
            studentinfo = Student.query.filter(Student.student_num == students_num).first()
            grade = studentinfo.grade
            specialty = studentinfo.specialty_id
            newfeedback = Feedback(student_num=students_num, inauguration_company=icompany,
                                   career_satisfaction=fcareer_satisfaction, industry=foccupation,
                                   corporate_satisfaction=fcorporate_satisfaction, take_office=ftake_office,
                                   yearly_salary=iyearly, industry_satisfaction=findustry_satisfaction,
                                   prize_winning=fprize_winning, self_evaluation=fself_evaluation, counts=1,
                                   shengqian=fshengqian, grade=grade, specialty=specialty)
            db.session.add(newfeedback)
            db.session.commit()
            return redirect(url_for('student.index'))
    return render_template('student/feedback.html', form=feedform)


@student.route('/basicinfo', methods=['GET', 'POST'])
@login_required
def basicinfo():
    form = BasicInfoForm()
    choicelist = []
    chcompany = Company.query.filter().order_by(Company.company_name.asc()).all()
    for i in chcompany:
        choicelist.append((i.company_name, i.company_name))
    form.company.choices = choicelist
    info = Basicinfo.query.filter(
        Basicinfo.student_num == current_user.accounts).first()
    if not info:
        return redirect(url_for('student.fristbasicinfo'))
    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return redirect(url_for('student.index'))
        updatainfo = Basicinfo.query.filter(
            Basicinfo.student_num == current_user.accounts).first()
        updatainfo.company = form.company.data
        updatainfo.position = form.position.data
        updatainfo.technology = form.technology.data
        updatainfo.yearly_salary = form.yearly_salary.data
        updatainfo.is_quit = form.is_quit.data
        updatainfo.quit_reason = form.quit_reason.data
        updatainfo.work_time = form.work_time.data
        updatainfo.relevant = form.relevant.data
        print form.relevant.data
        db.session.commit()
        return redirect(url_for('student.index'))
    return render_template('student/basicinfo.html', form=form)


@student.route('/fristbasicinfo', methods=['GET', 'POST'])
@login_required
def fristbasicinfo():
    choicelist = []
    chcompany = Company.query.filter().order_by(Company.company_name.asc()).all()
    for i in chcompany:
        choicelist.append((i.company_name, i.company_name))
    info = Basicinfo.query.filter(
        Basicinfo.student_num == current_user.accounts).first()
    if info:
        return redirect(url_for('student.index'))
    form = FristBasicInfoForm()
    form.company.choices = choicelist
    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return redirect(url_for('student.index'))
        students_num = current_user.accounts
        company = form.company.data
        position = form.position.data
        technology = form.technology.data
        yearly_salary = form.yearly_salary.data
        sex = form.sex.data
        is_quit = form.is_quit.data
        quit_reason = form.quit_reason.data
        work_time = form.work_time.data
        relevant = form.relevant.data
        studentinfo = Student.query.filter(Student.student_num == students_num).first()
        grade = studentinfo.grade
        specialty = studentinfo.specialty_id
        print relevant
        fristbasic = Basicinfo(student_num=students_num, company=company, position=position, relevant=relevant,
                               technology=technology, yearly_salary=yearly_salary, sex=sex, is_quit=is_quit,
                               quit_reason=quit_reason, work_time=work_time, grade=grade, specialty=specialty)
        db.session.add(fristbasic)
        db.session.commit()
        return redirect(url_for('student.index'))
    bform = FristBasicInfoForm()
    bform.company.choices = choicelist
    return render_template('student/firstbasicinfo.html', form=bform, errors=u'您还没有录入基本信息，请录入')


@student.route('/checkfeedback', methods=['GET', 'POST'])
@login_required
def checkfeedback():
    finfo = Feedback.query.filter(
        Feedback.student_num == current_user.accounts).first()
    if not finfo:
        return redirect(url_for('student.feedback', errors=u'您还没有录入信息，请录入'))
    return render_template('student/checkfeedback.html', datainfo=finfo)


@student.route('/ssfeedback', methods=['GET', 'POST'])
@login_required
def ssfeedback():
    info = Basicinfo.query.filter(
        Basicinfo.student_num == current_user.accounts).first()
    if not info:
        return redirect(url_for('student.fristbasicinfo'))
    form = SSFeedbackFrom()
    if request.method == 'GET':
        ffinfo = SSFeedback.query.filter(SSFeedback.student_num == current_user.accounts).first()
        if ffinfo:
            form.favorite_courses.render_kw = {'value': ffinfo.favorite_courses}
            form.favorite_teacher.render_kw = {'value': ffinfo.favorite_teacher}
            form.evaluate.data = ffinfo.evaluate
        return render_template('student/ssfeedback.html', form=form, errors=request.args.get("errors"))
    if request.method == 'POST':
        if not form.validate_on_submit():
            print form.errors
            return redirect(url_for('student.ssfeedback'))
        ssfeedbackf = SSFeedback.query.filter(
            SSFeedback.student_num == current_user.accounts).first()
        if ssfeedbackf:
            professional_ranking = form.professional_ranking.data
            course_satisfaction = form.course_satisfaction.data
            course_size = form.course_size.data
            teacher_satisfaction = form.teacher_satisfaction.data
            favorite_courses = form.favorite_courses.data
            favorite_teacher = form.favorite_teacher.data
            self_satisfaction = form.self_satisfaction.data
            school_by_work = form.school_by_work.data
            school_class_work = form.school_class_work.data
            evaluate = form.evaluate.data
            print evaluate
            update_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            finfo = SSFeedback.query.filter(
                SSFeedback.student_num == current_user.accounts).first()
            finfo.professional_ranking = professional_ranking
            finfo.course_satisfaction = course_satisfaction
            finfo.course_size = course_size
            finfo.teacher_satisfaction = teacher_satisfaction
            finfo.favorite_courses = favorite_courses
            finfo.favorite_teacher = favorite_teacher
            finfo.self_satisfaction = self_satisfaction
            finfo.school_by_work = school_by_work
            finfo.school_class_work = school_class_work
            finfo.evaluate = evaluate
            finfo.update_time = update_time
            db.session.commit()
            return redirect(url_for('student.index'))
        else:
            print 'frist ssfeedback'
            professional_ranking = form.professional_ranking.data
            course_satisfaction = form.course_satisfaction.data
            course_size = form.course_size.data
            teacher_satisfaction = form.teacher_satisfaction.data
            favorite_courses = form.favorite_courses.data
            favorite_teacher = form.favorite_teacher.data
            self_satisfaction = form.self_satisfaction.data
            school_by_work = form.school_by_work.data
            school_class_work = form.school_class_work.data
            evaluate = form.evaluate.data
            update_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            student_num = current_user.accounts
            student_name = current_user.name
            sinfo = Student.query.filter(Student.student_num == current_user.accounts).first()
            specialty = sinfo.specialty
            grade = sinfo.grade
            specialty_id = sinfo.specialty_id
            student_class = sinfo.student_class
            newssfeedback = SSFeedback(student_num=student_num, student_name=student_name, specialty=specialty,
                                       grade=grade, student_class=student_class,
                                       professional_ranking=professional_ranking,
                                       course_satisfaction=course_satisfaction, course_size=course_size,
                                       teacher_satisfaction=teacher_satisfaction, favorite_courses=favorite_courses,
                                       favorite_teacher=favorite_teacher, self_satisfaction=self_satisfaction,
                                       school_by_work=school_by_work, school_class_work=school_class_work,
                                       evaluate=evaluate, update_time=update_time, specialty_id=specialty_id)
            db.session.add(newssfeedback)
            db.session.commit()
            return redirect(url_for('student.index'))
    return render_template('student/basicinfo.html', form=form)


@student.route('/checkssfeedback', methods=['GET', 'POST'])
@login_required
def checkssfeedback():
    finfo = SSFeedback.query.filter(
        SSFeedback.student_num == current_user.accounts).first()
    if not finfo:
        return redirect(url_for('student.ssfeedback', errors=u'您还没有录入信息，请录入'))
    return render_template('student/checkssfeedback.html', datainfo=finfo)


@student.route('/selectabilityforfx', methods=['GET', 'POST'])
@login_required
def selectabilityforfx():
    if request.method == 'GET':
        if request.args.get('check') == 'True':
            studentnum = current_user.accounts
            ssinfo = Student.query.filter(Student.student_num == studentnum).first()
            specialtyid = ssinfo.specialty_id
            grade = ssinfo.grade
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
                    url_for('student.zxindex', errors=u'没有录入成绩，无法查看！'))

            return render_template('student/selectabilityforfx.html', specialtyid=specialtyid, studentnum=studentnum,
                                   grade=grade, abilitylist=abilitylist)


@student.route('/zxcheckfx', methods=['GET', 'POST'])
@login_required
def zxcheckfx():
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
        allres = []
        for x in gradell:
            j = request.args.get('ability')
            if j:
                print j
                abilityclassification = AbilityClassification.query.filter(
                    AbilityClassification.kc_classification == j, AbilityClassification.specialty == specialtyid).all()
                classlist = []
                classcodeweight = []
                nextkey = []
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
                allres.append(results)

                cursor.execute(sqlnex)
                resultsnex = cursor.fetchall()

                cursor.close()
                conn.close()
                keyindex = []
                nextkc = []
                for o in resultsnex:
                    for n in range(len(classlist)):
                        if (o[n] is not None):
                            keyindex.append(n)
                        else:
                            nextkc.append(classlist[n])
                            nextkey.append(n)
                    print keyindex

                nextvalue = float(0.0)
                cjtmp = []
                for n in keyindex:
                    nweight = float(classcodeweight[n][1])
                    nvvaule = resultsnex[0][n]
                    cjtmp.append(nvvaule)
                    nextvalue = nextvalue + (nweight * nvvaule)
                zxstudentclass = []
                unum = 0
                for u in keyindex:
                    zxstudentclass.append((classlist[u], cjtmp[unum]))
                    unum = unum + 1
                nnextvalue = '%.2f' % nextvalue
                nnextvalue = float(nnextvalue)
                studentnexvalue = (resultsnex[0][len(classlist)], resultsnex[0][len(classlist) + 1], nnextvalue)
                for l in results:
                    nvalue = float(0.0)
                    for n in keyindex:
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
                    allgradevalue.append((l[nnn], studentname, nvalue2))
                # print specifiedvaluelist
        allabslist = []
        for i in allgradevalue:
            fvalue = float(i[2])
            absvalue = '%.2f' % abs(studentnexvalue[2] - fvalue)
            allabslist.append((i[0], i[1], fvalue, absvalue))
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
        allnextnum = []
        for res in allres:
            nextkeynum = []
            for i in nextkey:
                indnum = 0
                for j in range(len(res)):
                    if res[j][i]:
                        indnum = indnum + 1
                nextkeynum.append(indnum)
            allnextnum.append(nextkeynum)
        zxnextkcvalue = []
        for i in range(len(allnextnum[0])):
            llnum = 0
            for j in allnextnum:
                llnum = llnum + j[i]
            zxnextkcvalue.append(llnum)
        print zxnextkcvalue
        print nextkey
        return render_template('student/checkfxforstudent.html', allabsall=allabsall,
                               studentnexvalue=studentnexvalue, nextkc=nextkc, zxstudentclass=zxstudentclass,
                               zxnextkcvalue=zxnextkcvalue)


@student.route('/zxcheckfxall', methods=['GET', 'POST'])
@login_required
def zxcheckfxall():
    if request.method == 'GET':
        studentnextnum = request.args.get('studentnum')
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        grade = sssinfo.grade
        abilitycategory = AbilityCategory.query.filter(AbilityCategory.specialty == specialtyid).all()
        abilitycategorylist = []
        for i in abilitycategory:
            abilitycategorylist.append(i.ability)

        grade1 = str((int(grade) - 1))
        grade2 = str((int(grade) - 2))
        gradell = [grade1, grade2]
        print gradell
        allgradevalue = []
        allstudentinfo = []
        for x in gradell:
            studentabi4list = []
            allabilist = []
            ssstudent = []
            for j in abilitycategorylist:
                print j
                fllabi = []
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
                        if (o[n] is not None):
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
                studentabi4list.append(studentnexvalue)
                for l in results:
                    nvalue = float(0.0)
                    for n in keyindex:
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
                    fenvalue = (l[nnn], studentname, nvalue2)
                    fllabi.append(fenvalue)
                xstudent = []
                yvalue = []
                for p in fllabi:
                    xstudent.append((p[0], p[1]))
                    yvalue.append(p[2])
                ssstudent = xstudent
                allabilist.append(yvalue)
            allstudentinfo.append(ssstudent)
            allgradevalue.append(allabilist)

        sssnum = 0
        allvalueforss = []
        for i in allgradevalue:
            studentforall = []
            for j in range(len(allstudentinfo[sssnum])):
                studentforfen = []
                for n in i:
                    studentforfen.append(float(n[j]))
                studentforall.append(studentforfen)
            allvalueforss.append(studentforall)
            sssnum = sssnum + 1

        zxstudentinfo = (studentabi4list[0][0], studentabi4list[0][1])
        zxstudentvalue = []
        for i in studentabi4list:
            zxstudentvalue.append(i[2])
        nnum = 0
        cosineall = []
        for i in allvalueforss:
            studentinfo = allstudentinfo[nnum]
            snnum = 0
            for j in i:
                cosinevalue = cosine(zxstudentvalue, j)
                cosineall.append((studentinfo[snnum][0], studentinfo[snnum][1], cosinevalue))
                snnum = snnum + 1
            nnum = nnum + 1

        tmplist = sorted(cosineall, key=lambda x: x[2], reverse=True)
        tmplist = tmplist[:5]
        allcosall = []
        for i in tmplist:
            conn = pymysql.connect()
            cursor = conn.cursor()
            sqlqx = 'select qx from achievement where student_num=' + i[0] + ';'
            cursor.execute(sqlqx)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            allcosall.append((i[0], i[1], results[0][0], i[2]))
        return render_template('student/checkallfxforstudent.html', allcosall=allcosall, zxstudentinfo=zxstudentinfo)


@student.route('/zxstudent_basic_info_wordcloud', methods=['GET', 'POST'])
@login_required
def zxstudent_basic_info_wordcloud():
    student_info = Basicinfo.query.filter().all()
    if not student_info:
        return redirect(url_for('student.zxindex', errors=u'还未有学生录入基本信息，无法查看'))
    page = Page()
    if request.method == 'GET':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        specialtyname = Specialty.query.filter(Specialty.specialty_id == specialtyid).first().specialty_name
        piename = specialtyname + '专业学生就职公司比例图'
        student_info = Basicinfo.query.filter(Basicinfo.specialty == specialtyid).all()
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentbasicinfowordcloud.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx
                               )
    if request.method == 'POST':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        specialty = specialtyid
        zxgrade = sssinfo.grade
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentbasicinfowordcloud.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)


@student.route('/zxstudent_year_salary_pie_all', methods=['GET', 'POST'])
@login_required
def zxstudent_year_salary_pie_all():
    student_info = Basicinfo.query.filter().all()
    page = Page()
    if not student_info:
        return redirect(url_for('student.zxindex', errors=u'还未有学生录入基本信息，无法查看'))
    if request.method == 'GET':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        specialtyname = Specialty.query.filter(Specialty.specialty_id == specialtyid).first().specialty_name
        piename = specialtyname + '专业学生年薪比例图'
        student_info = Basicinfo.query.filter(Basicinfo.specialty == specialtyid).all()
        yearsalarylist = []
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentyearsalarypie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)
    if request.method == 'POST':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        student_info = Basicinfo.query.filter(Basicinfo.specialty == specialtyid).all()
        yearsalarylist = []
        piename = "全部学生年薪比例图"
        specialty = specialtyid
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentyearsalarypie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)


@student.route('/zxstudent_occupation_pie_all', methods=['GET', 'POST'])
@login_required
def zxstudent_occupation_pie_all():
    student_info = Basicinfo.query.filter().all()
    page = Page()
    if not student_info:
        return redirect(url_for('student.zxindex', errors=u'还未有学生录入基本信息，无法查看'))
    if request.method == 'GET':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        specialtyname = Specialty.query.filter(Specialty.specialty_id == specialtyid).first().specialty_name
        piename = specialtyname + '专业学生职业相关度比例图'
        student_info = Basicinfo.query.filter(Basicinfo.specialty == specialtyid).all()
        occupationlist = []
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentoccupationpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)
    if request.method == 'POST':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        student_info = Basicinfo.query.filter(Basicinfo.specialty == specialtyid).all()
        occupationlist = []
        piename = "全部学生职业相关度比例图"
        specialty = specialtyid
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentoccupationpie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)


@student.route('/zxstudent_satisfaction_pie', methods=['GET', 'POST'])
@login_required
def zxstudent_satisfaction_pie():
    studentfeed_info = Feedback.query.filter().all()
    page = Page()
    if not studentfeed_info:
        return redirect(url_for('student.zxindex', errors=u'还未有学生录入反馈信息，无法查看'))
    if request.method == 'GET':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        specialtyname = Specialty.query.filter(Specialty.specialty_id == specialtyid).first().specialty_name
        pienamess = specialtyname + '专业'
        specialty = specialtyid
        studentfeed_info = Feedback.query.filter(Feedback.specialty == specialty).all()
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

        pie = Pie(pienamess + "学生就职职业分布比例图", title_pos='center', width=1000)
        pie2 = Pie(pienamess + "学生对自己职业满意度比例图", title_pos='center', width=1000)
        pie3 = Pie(pienamess + "学生对所在企业满意度比例图", title_pos='center', width=1000)
        pie4 = Pie(pienamess + "学生对所在行业满意度比例图", title_pos='center', width=1000)
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentzhiyepie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)
    if request.method == 'POST':
        studentnextnum = current_user.accounts
        sssinfo = Student.query.filter(Student.student_num == studentnextnum).first()
        specialtyid = sssinfo.specialty_id
        zxgrade = sssinfo.grade
        specialty = specialtyid
        feedlist = []
        zylist = []
        qylist = []
        hylist = []
        piename = "学生就职职业分布比例图"
        piename2 = "学生对自己职业满意度比例图"
        piename3 = "学生对所在企业满意度比例图"
        piename4 = "学生对所在行业满意度比例图"
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
        gradezx = []
        for i in gradelist:
            if i <= zxgrade:
                gradezx.append(i)
        return render_template('student/zxstudentzhiyepie.html',
                               myechart=page.render_embed(),
                               host=REMOTE_HOST,
                               script_list=page.get_js_dependencies(),
                               specialtylist=specialtylist, gradelist=gradezx)
