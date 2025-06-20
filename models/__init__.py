from extensions import db

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    # 经纬度可用两个float字段分别存储
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

class ScenicSpot(db.Model):
    __tablename__ = 'scenic_spots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
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
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    avg_price = db.Column(db.Float)
    address = db.Column(db.String(256))
    recommend_dishes = db.Column(db.String(256))

class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    price = db.Column(db.Float)
    checkin_time = db.Column(db.String(32))
    checkout_time = db.Column(db.String(32))
    address = db.Column(db.String(256))

# 交通
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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # 改为256或512
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(32), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())# 创建时间

class Admin(db.Model):
    __tablename__='admins'
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(64),unique=True,nullable=False)
    password=db.Column(db.String(256),nullable=False)
    email=db.Column(db.String(128),unique=True,nullable=False)
    phone=db.Column(db.String(32),unique=True,nullable=False)
    created_at= db.Column(db.DateTime, default=db.func.current_timestamp())# 创建时间

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    scenic_spot_id = db.Column(db.Integer, db.ForeignKey('scenic_spots.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 评分，1-5星
    created_at= db.Column(db.DateTime, default=db.func.current_timestamp())# 创建时间

class Order(db.Model):
    __tablename__='orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    scenic_spot_id = db.Column(db.Integer, db.ForeignKey('scenic_spots.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'))
    transport_id = db.Column(db.Integer, db.ForeignKey('transports.id'))
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())# 订单创建时间
    total_amount = db.Column(db.Float, nullable=False)  # 订单总金额
    status = db.Column(db.String(32), nullable=False)  # 订单状态，如待支付、已完成等
    payment_method = db.Column(db.String(32))  # 支付方式，如信用卡、支付宝等
    transaction_id = db.Column(db.String(128), unique=True)  # 交易流水号，支付后由支付平台生成

class Collection(db.Model):
    __tablename__='collections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    scenic_spot_id = db.Column(db.Integer, db.ForeignKey('scenic_spots.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'))
    created_at= db.Column(db.DateTime, default=db.func.current_timestamp())# 收藏时间

class Trip(db.Model):
    __tablename__='trips'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(128),nullable=False)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    destination=db.Column(db.String(128),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    created_at=db.Column(db.DateTime,default=db.func.current_timestamp())  # 创建时间