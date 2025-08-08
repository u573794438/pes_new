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
    
    # 检查两表数据差异
    print("\n=== 两表数据差异检查 ===")
    try:
        # 获取employee表有但employees表没有的ID
        result = db.session.execute(text("SELECT id, name FROM employee WHERE id NOT IN (SELECT id FROM employees)"))
        diff_count = 0
        for row in result:
            print(f"仅在employee表中: ID={row[0]}, 姓名={row[1]}")
            diff_count += 1
        
        if diff_count == 0:
            print("employee表中的所有ID都存在于employees表中")
    except Exception as e:
        print(f"差异检查失败: {str(e)}")
    
    print("\n=== 检查完成 ===")