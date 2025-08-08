from app import app
from models import db, Employee
from sqlalchemy.inspection import inspect

def list_employees_detailed():
    """列出employees表中的所有记录，包含每个字段"""
    print("=== 开始列出所有员工记录 ===")

    with app.app_context():
        try:
            # 获取Employee模型的所有字段名
            inspector = inspect(Employee)
            column_names = [column.name for column in inspector.columns]

            # 查询所有员工记录
            employees = Employee.query.all()

            if not employees:
                print("没有找到员工记录。")
                return

            # 打印表头
            header = " | ".join([f"{col:<20}" for col in column_names])
            print(header)
            print("-" * len(header))

            # 打印每条记录
            for emp in employees:
                row = []
                for col in column_names:
                    # 获取字段值
                    value = getattr(emp, col)
                    # 如果值为None，显示为空字符串
                    if value is None:
                        row.append(""[:20])
                    else:
                        row.append(str(value)[:20])
                print(" | ".join(row))

            print(f"\n共找到 {len(employees)} 条员工记录。")
            print("=== 列出员工记录完成 ===")

        except Exception as e:
            print(f"查询过程中出错: {str(e)}")
            print("=== 列出员工记录失败 ===")


def main():
    """主函数"""
    list_employees_detailed()

if __name__ == '__main__':
    main()