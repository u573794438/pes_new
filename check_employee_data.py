from app import app
from extensions import db
from models import Employee

with app.app_context():
    # 查询员工数量
    employee_count = Employee.query.count()
    print(f"当前数据库中的员工数量: {employee_count}")
    
    # 如果有员工，打印前5名员工的信息
    if employee_count > 0:
        print("\n前5名员工信息:")
        employees = Employee.query.limit(5).all()
        for emp in employees:
            print(f"ID: {emp.id}, 姓名: {emp.name}, 职位: {emp.position}")
    else:
        print("数据库中没有员工数据。")