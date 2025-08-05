from app import app
from extensions import db
from models import Employee

with app.app_context():
    # 创建所有表（如果表已存在，则不会重复创建）
    db.create_all()
    print('数据库更新成功')