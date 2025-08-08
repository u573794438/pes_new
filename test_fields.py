from flask import Flask
from extensions import db
from models import Employee
import os

basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'performance_evaluation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # 查询所有员工，验证字段是否存在
    employees = Employee.query.all()
    print(f'Found {len(employees)} employees')
    
    # 打印第一个员工的信息（如果有）
    if employees:
        first_employee = employees[0]
        print(f'First employee: {first_employee.name}')
        print(f'Role: {first_employee.role}')
        print(f'Position coefficient: {first_employee.position_coefficient}')
        
        # 更新角色和岗位系数
        first_employee.role = '部门经理'
        first_employee.position_coefficient = 1.5
        db.session.commit()
        print('Updated employee information')
        
        # 重新查询验证更新
        updated_employee = Employee.query.get(first_employee.id)
        print(f'Updated role: {updated_employee.role}')
        print(f'Updated position coefficient: {updated_employee.position_coefficient}')
    
    # 创建新员工，验证默认值
    new_employee = Employee(
        employee_id='9999',
        name='测试员工',
        position='测试岗位',
        password_hash='test'
    )
    db.session.add(new_employee)
    db.session.commit()
    print('Created new employee')
    
    # 验证新员工的默认值
    test_employee = Employee.query.filter_by(employee_id='9999').first()
    print(f'New employee role: {test_employee.role}')
    print(f'New employee position coefficient: {test_employee.position_coefficient}')