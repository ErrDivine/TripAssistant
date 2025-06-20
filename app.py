from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db  # 只导入db
import models  # 导入模型

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:jfbkn681@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)  # 关键：用app初始化db

def get_user_trips(user_id):
    from models import Trip
    return Trip.query.filter_by(user_id=user_id).all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan', methods=['GET', 'POST'])
def plan_customization():
    if request.method == 'POST':
        # 获取表单数据，跳转到结果页
        return redirect(url_for('plan_result'))
    is_logged_in = 'user_id' in session
    return render_template('plan_customization.html', is_logged_in=is_logged_in)

@app.route('/result')
def plan_result():
    # 这里应根据用户输入生成攻略
    return render_template('plan_result.html')

@app.route('/ticket-guide')
def ticket_guide():
    return render_template('ticket_guide.html')

@app.route('/detail/<item_type>/<item_id>')
def detail(item_type, item_id):
    # item_id: 数据库或API中的唯一标识
    return render_template('detail.html', item_type=item_type, item_id=item_id)

@app.route('/user')
def user_center():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    from models import User, Collection, ScenicSpot, Restaurant, Hotel
    user = User.query.get(session['user_id'])
    trips = get_user_trips(user.id)
    # 查询收藏
    collections = Collection.query.filter_by(user_id=user.id).all()
    # 组装收藏详情
    collection_details = []
    for c in collections:
        if c.scenic_spot_id:
            spot = ScenicSpot.query.get(c.scenic_spot_id)
            collection_details.append({'type': '景点', 'name': spot.name if spot else '未知', 'id': c.scenic_spot_id})
        if c.restaurant_id:
            restaurant = Restaurant.query.get(c.restaurant_id)
            collection_details.append({'type': '餐厅', 'name': restaurant.name if restaurant else '未知', 'id': c.restaurant_id})
        if c.hotel_id:
            hotel = Hotel.query.get(c.hotel_id)
            collection_details.append({'type': '酒店', 'name': hotel.name if hotel else '未知', 'id': c.hotel_id})
    return render_template('user_center.html', user=user, trips=trips, collections=collection_details)

# 删除行程
@app.route('/delete_trip/<int:trip_id>')
def delete_trip(trip_id):
    from models import Trip
    trip = Trip.query.get(trip_id)
    if trip:
        db.session.delete(trip)
        db.session.commit()  # 注意这里是 commit 不是逗号
        flash('行程已删除')
    else:
        flash('未找到该行程')
    return redirect(url_for('user_center'))
@app.route('/help')
def help():
    return render_template('help.html')

# 登录注册路由管理
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username=request.form['username']
        email=request.form['email']
        phone=request.form['phone']
        password=request.form['password']
        # 导入USer类
        from models import User
        if models.User.query.filter((User.username==username)|(User.email==email)|(User.phone==phone)).first():
            flash('用户名，邮箱或手机号已经存在，请重新注册')
            return render_template('register.html')
        user = models.User(
            username=username,
            email=email,
            phone=phone,
            password=generate_password_hash(password)#对用户密码进行加密
        )
        db.session.add(user)  #添加到数据库
        db.session.commit()   #提交
        flash('注册成功，请登录')
        return redirect(url_for('login'))  #请求转发到login路由
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        from models import User
        user =User.query.filter_by(username=username).first()  #通过 SQLAlchemy 查询数据库中是否存在与给定用户名匹配的用户，并返回第一个匹配的用户对象
        if user and check_password_hash(user.password,password):
            session['user_id']=user.id
            session['username']=user.username
            flash('登录成功')
            return redirect(url_for('user_center'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已退出登录')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/change_user_info', methods=['GET', 'POST'])
def change_user_info():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    from models import User
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_email = request.form.get('new_email')
        new_phone = request.form.get('new_phone')
        # 简单校验
        if not new_name or not new_email or not new_phone:
            flash('所有字段均不能为空')
            return render_template('changeUserInfo.html', user=user)
        # 检查用户名，邮箱和手机号唯一性
        if User.query.filter(User.username == new_name, User.id != user.id).first():
            flash('该用户名已被其他用户使用')
            return render_template('changeUserInfo.html', user=user)
        if User.query.filter(User.email == new_email, User.id != user.id).first():
            flash('该邮箱已被其他用户使用')
            return render_template('changeUserInfo.html', user=user)
        if User.query.filter(User.phone == new_phone, User.id != user.id).first():
            flash('该手机号已被其他用户使用')
            return render_template('changeUserInfo.html', user=user)
        user.username = new_name
        user.email = new_email
        user.phone = new_phone
        db.session.commit()
        flash('信息修改成功')
        return redirect(url_for('user_center'))
    return render_template('changeUserInfo.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)