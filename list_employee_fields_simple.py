from app import app
from models import db, Employee
from sqlalchemy.inspection import inspect

def list_employee_fields():
    with app.app_context():
        try:
            # 获取Employee模型的所有字段
            inspector = inspect(Employee)
            columns = inspector.columns

            print("employees表字段信息:")
            for column in columns:
                print(f"字段名: {column.name}")
                print(f"  类型: {column.type}")
                print(f"  是否为主键: {column.primary_key}")
                print(f"  默认值: {column.default}")
                print(f"  可为空: {column.nullable}")
                print()

        except Exception as e:
            print(f"查询过程中出错: {str(e)}")

if __name__ == '__main__':
    list_employee_fields()