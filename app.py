from flask import Flask, render_template, request, jsonify
from tooled_llm import llm_action # Using your core function

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan_customization')
def plan_customization():
    return render_template('plan_customization.html')

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
    return render_template('user_center.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)