from app import app
from app.user import user
from app.student import student

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(student, url_prefix='/student')
if __name__ == '__main__':
    app.run(host='0.0.0.0')
