from flask import Blueprint
from init import db, bcrypt
from datetime import date
from models.card import Card
from models.user import User

db_commands_bp = Blueprint('db', __name__)

@db_commands_bp.cli.command('create')
def create_db():
    db.create_all()
    print("Tables created")

@db_commands_bp.cli.command('drop')
def drop_db():
    db.drop_all()
    print("Tables dropped")

@db_commands_bp.cli.command('seed')
def seed_db():
    users = [
        User(
            email = 'admin@spam.com',
            password= bcrypt.generate_password_hash('eggs').decode('utf-8'),
            is_admin = True
        ),
        User(
            name = 'Chevy Chase',
            email = 'someone@spam.com',
            password= bcrypt.generate_password_hash('12345').decode('utf-8'),
        ),
    ]

    db.session.add_all(users)
    db.session.commit()
    print('Users seeded')

    cards = [
        Card(
            title = 'Start the project',
            description = 'Stage 1 - Create the database',
            status = 'To Do',
            priority = 'High',
            date = date.today(),
            user_id = users[0].id
        ),
        Card(
            title = "SQLAlchemy",
            description = "Stage 2 - Integrate ORM",
            status = "Ongoing",
            priority = "High",
            date = date.today(),
            user = users[0]
        ),
        Card(
            title = "ORM Queries",
            description = "Stage 3 - Implement several queries",
            status = "Ongoing",
            priority = "Medium",
            date = date.today(),
            user_id = users[1].id
        ),
        Card(
            title = "Marshmallow",
            description = "Stage 4 - Implement Marshmallow to jsonify models",
            status = "Ongoing",
            priority = "Medium",
            date = date.today(),
            user = users[1]
        )
    ]
    
    db.session.add_all(cards)
    db.session.commit()
    print('Cards seeded')

# Terminal Response

# Legacy version
# @app.cli.command('all_cards')
# def all_cards():
#     # select * from cards;
#     cards = Card.query.all()
#     print(cards[0].__dict__)

# New version
@db_commands_bp.cli.command('all_cards')
def all_cards():
    # select * from cards;
    # stmt = db.select(Card).where(Card.status == 'To Do')
    # stmt = db.select(Card).filter_by(status= 'To Do')
    stmt = db.select(Card)
    cards = db.session.execute(stmt)
    print(cards)
    for card in cards:
        print(card)
    

# Legacy
# @app.cli.command('first_card')
# def first_card():
#     # select * from cards limit 1;
#     card = Card.query.first()
#     print(card.__dict__)

# New version
@db_commands_bp.cli.command('first_card')
def first_card():
    # select * from cards limit 1;
    stmt = db.select(Card).limit(1)
    card = db.session.scalar(stmt)
    print(card.__dict__)

@db_commands_bp.cli.command('count_ongoing')
def count_ongoing():
    stmt = db.select(db.func.count()).select_from(Card)
    print(stmt)
    cards = db.session.scalar(stmt)
    print(cards)
    # for card in cards:
    #     print(card.title, card.priority)