from app import app
from extensions import db
import models  # 确保所有模型都被导入

with app.app_context():
    db.create_all()
    print("所有表已创建。")