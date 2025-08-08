from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    print("=== 员工表数据检查 ===")
    
    # 检查employee表
    print("\n1. employee表数据:")
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM employee"))
        count = result.scalar()
        print(f"记录总数: {count}")
        
        if count > 0:
            print("前5条记录:")
            result = db.session.execute(text("SELECT id, name, position FROM employee LIMIT 5"))
            print("ID | 姓名 | 职位")
            for row in result:
                print(f"{row[0]} | {row[1]} | {row[2]}")
    except Exception as e:
        print(f"查询失败: {str(e)}")
    
    # 检查employees表
    print("\n2. employees表数据:")
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM employees"))
        count = result.scalar()
        print(f"记录总数: {count}")
        
        if count > 0:
            print("前5条记录:")
            result = db.session.execute(text("SELECT id, name, position FROM employees LIMIT 5"))
            print("ID | 姓名 | 职位")
            for row in result:
                print(f"{row[0]} | {row[1]} | {row[2]}")
    except Exception as e:
        print(f"查询失败: {str(e)}")
    
    print("\n=== 检查完成 ===")