# -*- encoding:utf-8 -*-

import json
import requests
from functools import wraps
from . import main
from flask import render_template, jsonify, request, abort
from app.models import db, Poetry, User, Role
from app import logger


def check_login(fun):
    # print('进入：', fun)
    @wraps(fun)
    def wrapper(*args, **kwargs):
        # print(request.form)
        token = request.form.get('token')
        if not token:
            token = request.args.get('token')
        if not token:
            data = request.data
            if data:
                try:
                    data = json.loads(data)
                except:
                    return fun(None)
                token = data.get('token')
        # print('装饰器中的token：', token)
        if token:
            user = User.verify_auth_token(token=token)
            return fun(user)
        else:
            return fun(None)

    return wrapper


@main.route('/api/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return {'code': -1, 'msg': 'false', 'data': 'pass'}, 405
    data = request.data
    if not data:
        return {'result': 'false', 'message': 'need username and password'}, 201
    try:
        data = json.loads(request.data)
    except:
        return {'result': 'false', 'message': 'data error'}, 400
    username = data.get('username')
    password = data.get('password')
    if not (username and password):
        return {'result': 'false', 'message': 'need username and password'}, 201
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'result': 'false', 'message': 'username or password error'}, 201
    result = user.check_password(password)
    # print(result)
    if not result:
        return {'result': 'false', 'message': 'username or password error'}, 201
    else:
        token = user.generate_auth_token()
        return {'result': 'true', 'message': 'login success', 'token': token}, 200


@main.route('/api/add/user', methods=['POST'])
@check_login
def add_user(user):
    if request.method != 'POST':
        return {'code': -1, 'msg': 'false', 'data': 'pass'}, 405
    if not user:
        return {'result': 'false', 'message': 'not login'}, 403
    role = Role.query.get(user.role_id)
    if role.roleName != 'admin':
        return {'result': 'false', 'message': 'not admin'}, 403
    data = request.data
    if not data:
        return {'result': 'false', 'message': 'need username and password and name'}, 201
    try:
        data = json.loads(data)
    except:
        return {'result': 'false', 'message': 'data error'}, 400
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    if not (username and password and name):
        return {'result': 'false', 'message': 'please give username, password and name'}, 201
    exist = User.query.filter_by(username=username).first()
    if exist:
        return {'result': 'false', 'message': 'this username was exist'}, 201
    role = Role.query.filter_by(roleName='user').first()
    role_id = role.id
    add_user_tmp = User(username=username, password=password, name=name, role_id=role_id)
    try:
        db.session.add(add_user_tmp)
        db.session.commit()
        return {'result': 'true', 'message': 'add user success'}, 200
    except Exception as e:
        db.session.rollback()
        return {'result': 'false', 'message': 'add user error'}, 201


@main.route('/api/could_add', methods=['GET'])
def could_add():
    url = "https://poetrydb.org/author"
    response = requests.get(url)
    if response.status_code != 200:
        return {'result': 'false', 'message': 'query authors error'}, response.status_code
    else:
        resp_json = response.json()
        return resp_json, response.status_code


@main.route('/api/add', methods=['POST'])
@check_login
def add(user):
    """
    :return:
    """
    # print(user)
    if request.method != 'POST':
        return jsonify({'code': -1, 'msg': 'false', 'data': 'pass'})
    if not user:
        return {'result': 'false', 'message': 'not login'}, 403
    data = request.data
    if not data:
        return {'result': 'false', 'message': 'not login'}, 403
    try:
        data = json.loads(request.data)
    except:
        return {'result': 'false', 'message': 'data error'}, 400
    author = data.get('author')
    if not author:
        return {'result': 'false', 'message': 'need author'}, 201
    url = 'https://poetrydb.org/author/' + author
    response = requests.get(url)
    if response.status_code != 200:
        return False
    resp_json = response.json()
    if not resp_json:
        return False
    for resp_one in resp_json:
        title = resp_one.get('title')
        author = resp_one.get('author')
        lines = resp_one.get('lines')
        lines_str = ''
        if not lines:
            lines_str = ''
        else:
            for line_one in lines:
                lines_str += '<' + line_one + '>'

        linecount = resp_one.get('linecount')
        exist = Poetry.query.filter_by(title=title, author=author, linecount=linecount).first()
        if not exist:
            add_poetry = Poetry(title=title, author=author, lines=lines_str, linecount=linecount)
            db.session.add(add_poetry)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return {'result': 'false', 'message': 'add false'}, 400
    return {'result': 'true', 'message': 'add success'}, 200


@main.route('/api/delete', methods=['POST'])
@check_login
def delete(user):
    if request.method != 'POST':
        return jsonify({'code': -1, 'msg': 'false', 'data': 'pass'})
    if not user:
        return {'result': 'false', 'message': 'not login'}, 403
    role = Role.query.get(user.role_id)
    if role.roleName != 'admin':
        return {'result': 'false', 'message': 'not admin'}, 403
    try:
        data = request.json
    except:
        return {'result': 'false', 'message': 'data error'}, 400

    poetry_id = data.get('id')
    if not poetry_id:
        return {'result': 'false', 'message': 'need id'}, 400
    try:
        poetry_id = int(poetry_id)
    except:
        return {'result': 'false', 'message': 'id should be int'}, 400

    poetry = Poetry.query.get(poetry_id)
    if not poetry:
        return {'result': 'false', 'message': 'id is not exists'}, 400
    try:
        db.session.delete(poetry)
        db.session.commit()
        return {'result': 'true', 'message': 'delete success'}, 200
    except:
        db.session.rollback()
        return {'result': 'false', 'message': 'delete failed'}, 400


@main.route('/api/update', methods=['POST'])
@check_login
def update(user):
    """
    :return:
    """
    if request.method != 'POST':
        return jsonify({'code': -1, 'msg': 'false', 'data': 'pass'})
    if not user:
        return {'result': 'false', 'message': 'not login'}, 403
    data = request.data
    try:
        data = json.loads(data)
    except:
        return {'result': 'false', 'message': 'data error'}, 400
    author_id = data.get('id')
    author = data.get('author')
    title = data.get('title')
    lines = data.get('lines')
    lines_str = ''
    if lines:
        if not isinstance(lines, list):
            return {'result': 'false', 'message': 'lines should be list'}, 400
        for lines_one in lines:
            lines_str += '<' + str(lines_one) + '>'
    linecount = data.get('linecount')

    if not author_id:
        return {'result': 'false', 'message': 'need id'}, 400
    else:
        try:
            author_id = int(author_id)
        except:
            return {'result': 'false', 'message': 'id should be int'}, 400
    update_poetry = Poetry.query.get(author_id)
    if not update:
        return {'result': 'false', 'message': 'not found the author'}, 200
    if title:
        update_poetry.title = title
    if author:
        update_poetry.author = author
    if lines_str:
        update_poetry.lines = lines_str
    if linecount:
        try:
            linecount = int(linecount)
            update_poetry.linecount = linecount
        except:
            return {'result': 'false', 'message': 'linecount should be int'}, 400
    try:
        db.session.add(update_poetry)
        db.session.commit()
        return {'result': 'true', 'message': 'update successed'}, 200
    except:
        db.session.rollback()
        return {'result': 'false', 'message': 'update failed'}, 200


@main.route('/api/query/author', methods=['GET'])
def query_author():
    author = request.args['author']
    result_list = []
    if author:
        query_poetry = Poetry.query.filter_by(author=author).all()
        # print(query_poetry)
        if not query_poetry:
            result_list = []
        else:
            for query_one in query_poetry:
                result_dict = {}
                result_dict['id'] = query_one.id
                result_dict['author'] = query_one.author
                result_dict['title'] = query_one.title
                query_lines = query_one.lines
                if query_lines:
                    query_lines = query_lines.lstrip('<')
                    query_lines = query_lines.rstrip('>')
                    query_lines = query_lines.split('><')
                result_dict['lines'] = query_lines
                result_dict['linecount'] = query_one.linecount
                result_list.append(result_dict)
    return {'result': 'true', 'message': 'success', 'data': result_list}, 200


@main.route('/api/query', methods=['GET'])
def query():

    page = request.args.get('page')
    limit = request.args.get('limit')
    result_list = []
    if not page:
        page = 1
    else:
        try:
            page = int(page)
        except:
            return {'result': 'false', 'message': 'page should be int', 'data': []}, 201
    if not limit:
        limit = 10
    else:
        try:
            limit = int(limit)
        except:
            return {'result': 'false', 'message': 'limit should be int', 'data': []}, 201
    query_poetry = Poetry.query.paginate(page=page, per_page=limit).items
    if not query_poetry:
        result_list = []
    else:
        for query_one in query_poetry:
            result_dict = {}
            result_dict['id'] = query_one.id
            result_dict['author'] = query_one.author
            result_dict['title'] = query_one.title
            query_lines = query_one.lines
            if query_lines:
                query_lines = query_lines.lstrip('<')
                query_lines = query_lines.rstrip('>')
                query_lines = query_lines.split('><')
            result_dict['lines'] = query_lines
            result_dict['linecount'] = query_one.linecount
            result_list.append(result_dict)
    return {'result': 'true', 'message': 'success', 'data': result_list}, 200
