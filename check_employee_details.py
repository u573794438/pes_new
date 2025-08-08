from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    print("=== 员工数据详细检查 ===")
    
    # 检查employee表
    print("\nemployee表数据:")
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM employee"))
        count = result.scalar()
        print(f"记录总数: {count}")
    except Exception as e:
        print(f"查询失败: {str(e)}")
    
    # 检查employees表
    print("\nemployees表数据:")
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM employees"))
        count = result.scalar()
        print(f"记录总数: {count}")
    except Exception as e:
        print(f"查询失败: {str(e)}")
    
    print("\n=== 检查完成 ===")