from flask import Blueprint, request
from init import db, bcrypt
from models.user import User, UserSchema
from datetime import date
from flask_jwt_extended import jwt_required
from controllers.auth_controller import authorize

users_bp = Blueprint('users', __name__, url_prefix='/users')
    
@users_bp.route('/')
@jwt_required()
def all_users():
    authorize()

    # stmt = db.select(User).where(User.status == 'To Do')
    # stmt = db.select(User).filter_by(status= 'To Do')

    stmt = db.select(User).order_by(User.name.desc(), User.is_admin)
    users = db.session.scalars(stmt).all()
    return UserSchema(many=True).dump(users)

@users_bp.route('/<int:id>')
def one_user(id):
    stmt = db.select(User).filter_by(id=id)
    user = db.session.scalar(stmt)
    if user:
        return UserSchema().dump(user)
    else:
        return {'error': f'User not found with id {id}'}, 404

@users_bp.route('/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_one_User(id):
    # find the User
    stmt = db.select(User).filter_by(id=id)
    user = db.session.scalar(stmt)
    # if it exists, update it
    if user:
        # ue get method to retrieve data as it returns 'none' instead of exception.
        user.email = request.json.get('email') or user.email
        user.name = request.json.get('name') or user.name
        user.is_admin = request.json.get('is_admin') or user.is_admin
        return UserSchema().dump(user)
    else:
        return {'error': f'User not found with id {id}'}, 404

@users_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_one_user(id):
        # need admin status
    authorize()

    stmt = db.select(User).filter_by(id=id)
    user = db.session.scalar(stmt)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User {user.name} deleted successfully'}
    else:
        return {'error': f'User not found with id {id}'}, 404

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_User():
    # retrieve data from incoming POST request and parse the JSON
    # Creat new User model instance from the user_info
    user = User(
        name = request.json['name'],
        password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8'),
        email = request.json['email'],
        is_admin = request.json['is_admin']
    )

    # Add and commit User to DB
    db.session.add(user)
    db.session.commit()
    # Respond to Client DB info and Successful creation Code 201
    return UserSchema().dump(user), 201