from app import app
from models import db, Employee
from sqlalchemy.inspection import inspect

def list_employee_fields():
    """列出employees表的所有字段信息"""
    print("=== employees表字段信息 ===")

    with app.app_context():
        try:
            # 获取Employee模型的所有字段
            inspector = inspect(Employee)
            columns = inspector.columns

            # 打印字段信息
            print(f"{'字段名':<20} {'类型':<20} {'是否为主键':<10} {'默认值':<20} {'可为空':<10}")
            print("-