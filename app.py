from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan', methods=['GET', 'POST'])
def plan_customization():
    if request.method == 'POST':
        # 获取表单数据，跳转到结果页
        return redirect(url_for('plan_result'))
    return render_template('plan_customization.html')

@app.route('/result')
def plan_result():
    # 这里应根据用户输入生成攻略
    return render_template('plan_result.html')

@app.route('/ticket-guide')
def ticket_guide():
    return render_template('ticket_guide.html')

@app.route('/detail/<item_type>/<item_id>')
def detail(item_type, item_id):
    # item_type: hotel/food/attraction
    # item_id: 数据库或API中的唯一标识
    return render_template('detail.html', item_type=item_type, item_id=item_id)

@app.route('/user')
def user_center():
    return render_template('user_center.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)