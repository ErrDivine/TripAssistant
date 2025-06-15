from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from app import db

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    location = db.Column(Geometry('POINT'))  # 经纬度

class ScenicSpot(db.Model):
    __tablename__ = 'scenic_spots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    location = db.Column(Geometry('POINT'))
    open_time = db.Column(db.String(32))
    close_time = db.Column(db.String(32))
    ticket_price = db.Column(db.Float)
    has_tour_bus = db.Column(db.Boolean)
    has_luggage_storage = db.Column(db.Boolean)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    location = db.Column(Geometry('POINT'))
    avg_price = db.Column(db.Float)
    address = db.Column(db.String(256))
    recommend_dishes = db.Column(db.String(256))

class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    location = db.Column(Geometry('POINT'))
    price = db.Column(db.Float)
    checkin_time = db.Column(db.String(32))
    checkout_time = db.Column(db.String(32))
    address = db.Column(db.String(256))

class Transport(db.Model):
    __tablename__ = 'transports'
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    type = db.Column(db.String(32))  # 地铁/公交/高铁/飞机/步行/打车
    line = db.Column(db.String(64))
    start_station = db.Column(db.String(128))
    end_station = db.Column(db.String(128))
    start_time = db.Column(db.String(32))
    end_time = db.Column(db.String(32))
    price = db.Column(db.Float)
    duration = db.Column(db.Integer)  # 单位：分钟