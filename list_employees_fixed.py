from app import app
from models import db, Employee

def list_all_employees():
    """列出employees表中的所有记录"""
    print("=== 开始列出所有员工记录 ===")

    with app.app_context():
        try:
            # 查询所有员工记录
            employees = Employee.query.all()

            if not employees:
                print("没有找到员工记录。")
                return

            # 打印表头
            print(f"{'ID':<5} {'员工ID':<10} {'姓名':<10} {'职位':<20} {'角色':<10} {'岗位系数':<10} {'是否管理员':<10} {'是否冻结':<10}")
            print("-