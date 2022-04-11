from app import create_app
import pymysql
app = create_app()


def create_db():
    from app.models import db, Role, User
    db.drop_all()
    db.create_all()
    Role.insert()
    User.insert()


if __name__ == '__main__':
    # create_db()
    app.run(host='0.0.0.0', threaded=True, port=5000)
