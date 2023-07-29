from . import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    backlogs = db.relationship('Backlog', backref='Users', lazy=True)

class Backlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    is_cleared = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    games = db.relationship('Game', backref='Backlog', lazy=True)
    
    def __init__(self, name, date_created, is_cleared, user_id):
        self.name = name
        self.date_created = date_created
        self.is_cleared = is_cleared
        self.user_id = user_id
    

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    platform = db.Column(db.String, nullable=False)
    howlongtobeat = db.Column(db.Integer)
    purchase_price = db.Column(db.Float)
    is_beat = db.Column(db.Boolean)
    backlog_id = db.Column(db.Integer, db.ForeignKey('backlog.id'), nullable=False)