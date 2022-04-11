import time

from . import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from sqlalchemy import Column, Integer, String, Text
import jwt


class Role(db.Model):
    """
    权限表
    """
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    roleName = Column(String(20))

    @staticmethod
    def insert():
        if not Role.query.filter_by(roleName='admin').first():
            admin = Role(roleName='admin')
            db.session.add(admin)
            user = Role(roleName='user')
            db.session.add(user)
        db.session.commit()


class User(UserMixin, db.Model):
    """
    用户信息
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer)
    username = Column(String(20), index=True, unique=True)
    _password = Column('password', String(128))
    name = Column(String(20))
    phone = Column(String(20))
    create_time = Column(Integer, default=int(time.time()))

    @staticmethod
    def insert():
        if not User.query.filter_by(username='admin').first():
            role = Role.query.filter_by(roleName='admin').first()
            role_id = role.id
            admin = User(username='admin', role_id=role_id, password='admin', name='admin')
            db.session.add(admin)
            db.session.commit()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self._password, pwd)

    def generate_auth_token(self):
        payload = {
            "id": self.id,
            "exp": int(time.time()) + current_app.config['TOKEN_TIME'],
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token

    @staticmethod
    def verify_auth_token(token):
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        if payload:
            user = User.query.get(payload['id'])
            if user:
                return user
            else:
                return False
        return False


class Poetry(db.Model):
    """
    tomcat地址，包地址，替换地址
    """
    __tablename__ = 'poetry'
    id = Column(Integer(), primary_key=True)
    title = Column(String(200))
    author = Column(String(50))
    lines = Column(Text())
    linecount = Column(Integer())
    createTime = Column(Integer(), default=int(time.time()))


