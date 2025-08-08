from app import app
from models import db, Employee

def list_employees():
    with app.app_context():
        employees = Employee.query.all()
        print(f"共找到 {len(employees)} 条员工记录:")
        for emp in employees:
            print(f"ID: {emp.id}, 员工ID: {emp.employee_id}, 姓名: {emp.name}")

if __name__ == '__main__':
    list_employees()