from app import app
from models import db, Employee
from sqlalchemy.inspection import inspect

def list_employee_fields():
    with app.app_context():
        try:
            inspector = inspect(Employee)
            columns = inspector.columns
            print("employees表字段列表:")
            for column in columns:
                print(f"- {column.name} ({column.type}) - 主键: {column.primary_key}, 可为空: {column.nullable}")
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == '__main__':
    list_employee_fields()