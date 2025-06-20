from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from tooled_llm import llm_action # Using your core function, session, flash
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

@app.route('/plan_customization')
def plan_customization():
    is_logged_in = 'user_id' in session
    return render_template('plan_customization.html', is_logged_in=is_logged_in)

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    user_input = request.json['travel_plan']

    # V4 Prompt: Demanding animated, layered components.
    system_prompt = """
    你是一位富有创造力的视觉叙事者和顶级的旅行规划师。你的任务是将一份旅行计划转化为一个极具动态感、层次分明、充满动画的纯HTML片段。

    **核心理念:** 告别无聊的文本块。将每一个活动拆解成一系列带有动画的、独立的步骤和信息点。

    **你的思考流程:**
    1.  **深度解析:** 理解用户的核心需求。
    2.  **数据驱动:** 使用工具获取天气、交通等实时数据。
    3.  **组件化构建:** 将所有信息包装在下面定义的、带有特定CSS类的HTML组件中。

    **内容与动画组件要求 (最关键的部分):**
    -   **不要使用 `<p>` 或 `<ul>` 标签写长段落。** 必须将每个句子或短语拆分到下面的组件中。
    -   **每一个动作是一个步骤:** `<div class="plan-step">...</div>` (例如: "从正门进入", "步行至山顶约需1小时")
    -   **每一个提示是一个技巧:** `<div class="pro-tip">...</div>` (例如: "建议从中山陵南门进入，可以少走回头路")
    -   **每一个警告是一个提醒:** `<div class="warning-note">...</div>` (例如: "注意：中山陵周一闭馆")
    -   **每一条信息是一个资料点:** `<div class="info-bit">...</div>` (例如: "门票：免费", "开放时间：8:30-17:30")

    **HTML结构与CSS类 (保持不变):**
    -   主容器: `<div class="result-container">`
    -   手风琴容器: `<div class="plan-accordion">`
    -   每日计划项: `<div class="accordion-item">` -> `<button class="accordion-header">` -> `<div class="accordion-content">`

    **至关重要:**
    -   输出**必须**是纯HTML代码，**所有文本内容必须是中文**。
    -   **不能**包含 `<html>`, `<head>`, `<body>`, `<script>`, 或 `<style>` 标签。
    -   **不能**使用Markdown。

    **输出格式示例 (展示了如何将一个活动拆解成多个动画组件):**
    ```html
    <div class="result-container">
      <div class="plan-accordion">
        <div class="accordion-item">
          <button class="accordion-header"><h3>第一天：抵达南京，初探古都</h3></button>
          <div class="accordion-content">
            <h4>下午：拜谒中山陵</h4>
            <div class="plan-step">前往钟山风景区的核心——<strong>中山陵</strong>。</div>
            <div class="info-bit">这是中国现代史上第一位总统孙中山先生的陵墓。</div>
            <div class="pro-tip">建议乘坐景区观光车（约10元）直达陵墓脚下，节省体力。</div>
            <div class="plan-step">从正门入口进入，准备开始登山。</div>
            <div class="info-bit">全程共有392级台阶，象征着当时中国的3亿9千200万同胞。</div>
            <div class="plan-step">步行至山顶的祭堂约需45分钟。</div>
            <div class="warning-note">注意：中山陵每周一关闭进行维护。</div>
            <div class="info-bit">门票：免费，但需在官方小程序上提前预约。</div>
            <p><strong>天气:</strong> ☀️ 25°C, 晴朗，非常适合户外活动和拍照。</p>
          </div>
        </div>
      </div>
    </div>
    ```
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    generated_html, _ = llm_action(messages)
    
    if generated_html.strip().startswith("```html"):
        generated_html = generated_html.strip()[7:-3].strip()

    return jsonify({'html': generated_html})


@app.route('/user_center')
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
    from models import User  
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        # 检查用户名、邮箱、手机号是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在，请更换后重试。')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册，请更换后重试。')
            return render_template('register.html')
        if User.query.filter_by(phone=phone).first():
            flash('手机号已被注册，请更换后重试。')
            return render_template('register.html')
        # 创建新用户
        new_user = User(username=username, email=email, phone=phone, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录。')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        from models import User
        user = User.query.filter_by(username=username).first()
        print('用户对象:', user)
        if user:
            print('数据库密码:', user.password)
            print('输入密码:', password)
            print('密码校验:', check_password_hash(user.password, password))
        if user and check_password_hash(user.password, password):
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

@app.route('/plan_result/<int:trip_id>')
def plan_result(trip_id):
    from models import Trip
    trip = Trip.query.get(trip_id)
    if not trip:
        flash('未找到该行程')
        return redirect(url_for('user_center'))
    return render_template('plan_result.html', trip=trip)

if __name__ == '__main__':
    app.run(debug=True, port=5001)