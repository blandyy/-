# coding=utf-8
from app.models import Year, Grade


def getyear():
    yearlist = []
    year = Year().query.filter().all()
    for i in year:
        yearlist.append(i.year)
    return yearlist


def getgrade():
    gradelist = []
    grade = Grade().query.filter().all()
    for i in grade:
        gradelist.append(i.grade)
    return gradelist
