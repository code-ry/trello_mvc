from flask import Blueprint, request, abort
from init import db, bcrypt
from models.user import User, UserSchema
from datetime import timedelta
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def authorize():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user.is_admin:
        abort(401)


@auth_bp.route('/login/', methods = ['POST'])
def auth_login():

    # Check if user exists and
    stmt = db.select(User).filter_by(email=request.json['email'])
    user = db.session.scalar(stmt)
    if user and bcrypt.check_password_hash(user.password,request.json['password']):
        # create token for client to store and use.
        token = create_access_token(identity= str(user.id), expires_delta=timedelta(days=1))
        return {'user': user.email, 'token': token, 'is_admin': user.is_admin}
    else:
        return {'error': 'Invalid email or password'}, 401

@auth_bp.route('/register/', methods=['POST'])
def auth_register():
    try:
        # retrieve data from incoming POST request and parse the JSON
        # user_info = UserSchema().load(request.json)
        # Creat new user model instance from the user_info
        user = User(
            email = request.json['email'],
            password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8'),
            name  = request.json.get('name')
        )
        # Add and commit user to DB
        db.session.add(user)
        db.session.commit()
        # Respond to Client DB info and Successful creation Code 201
        return UserSchema(exclude=['password']).dump(user), 201

    except IntegrityError:
        return {'error':'Email address already in use'}, 409
