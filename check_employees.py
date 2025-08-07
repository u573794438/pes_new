import os
from flask import Flask
from extensions import db
from models import Employee

# 创建一个最小的Flask应用实例用于数据库查询
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'performance_evaluation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # 查询employee_id小于"2"的员工
    count = Employee.query.filter(Employee.employee_id < "2").count()
    print(f'employee_id小于2的员工数量: {count}')

    # 查看具体员工信息
    employees = Employee.query.filter(Employee.employee_id < "2").all()
    if employees:
        print('员工列表:')
        for emp in employees:
            print(f'- id: {emp.id}, employee_id: {emp.employee_id}, name: {emp.name}')

    # 查询employee_id大于"2"的员工
    count = Employee.query.filter(Employee.employee_id > "2").count()
    print(f'employee_id大于2的员工数量: {count}')

    # 查看具体员工信息
    employees = Employee.query.filter(Employee.employee_id > "2").all()
    if employees:
        print('员工列表:')
        for emp in employees:
            print(f'- id: {emp.id}, employee_id: {emp.employee_id}, name: {emp.name}')