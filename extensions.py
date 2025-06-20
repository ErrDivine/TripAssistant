# 目的 该文件是为了解决app.py和__init.py循环导入的问题
# 方法：拆分模型定义和 db 实例
# 该文件只存放db实例


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()