from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies,
    get_csrf_token
)

from . import db
from .models import User
from .utils import hashing_password, compare_password_hash, add_revoked_tokens

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or name == '' or not email or email == '' or not password or password == '':
        return jsonify({'error': 'name, email or password cannot be empty'}), 400
    

    user_exist = User.query.filter_by(email=email).first()
    if user_exist:
        return jsonify({'error': 'user already registered'}), 409
    
    pwhash = hashing_password(password)

    user = User(
        name=name,
        email=email,
        password=pwhash
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'email or password cannot be empty'}), 400
    
    user = User.query.filter_by(email=email).first()

    if not user or not compare_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(
        identity=user.id
    )

    refresh_token = create_refresh_token(
        identity=user.id
    )

    response = jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_csrf_token': get_csrf_token(access_token),
        'refresh_csrf_token': get_csrf_token(refresh_token)
    })

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200

@auth_bp.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']

    add_revoked_tokens(jti)

    response = jsonify({'msg': 'successfully logged out'})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)

    new_access_token = create_access_token(
        identity=user.id
    )

    response = jsonify({
        'access_token': new_access_token,
        'access_csrf_token': get_csrf_token(new_access_token),
        'refresh_csrf_token': get_jwt()['csrf']
    })
    set_access_cookies(response, new_access_token)

    return response, 200
