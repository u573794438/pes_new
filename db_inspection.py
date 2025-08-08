from app import app
from extensions import db
from sqlalchemy import inspect, text

with app.app_context():
    print("=== 数据库检查报告 ===")
    
    # 获取数据库检查器
    inspector = inspect(db.engine)
    
    # 列出所有表
    tables = inspector.get_table_names()
    print(f"总表数量: {len(tables)}")
    print("\n表列表:")
    for table in tables:
        print(f"- {table}")
    
    # 检查重复表名
    print("\n=== 重复表名检查 ===")
    duplicate_tables = []
    for i in range(len(tables)):
        for j in range(i+1, len(tables)):
            if tables[i].lower() == tables[j].lower():
                duplicate_tables.append((tables[i], tables[j]))
    
    if duplicate_tables:
        print("发现以下重复表名:")
        for t1, t2 in duplicate_tables:
            print(f"- {t1} 和 {t2}")
    else:
        print("未发现重复表名.")
    
    # 检查表记录数量
    print("\n=== 表记录数量 ===")
    for table in tables:
        try:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"{table}: {count} 条记录")
        except Exception as e:
            print(f"{table}: 查询失败 - {str(e)}")
    
    # 检查员工表数据
    print("\n=== 员工表数据检查 ===")
    try:
        employee_tables = [t for t in tables if 'employee' in t.lower()]
        if not employee_tables:
            print("未找到员工表.")
        else:
            for emp_table in employee_tables:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {emp_table}"))
                count = result.scalar()
                print(f"{emp_table}: {count} 条记录")
    except Exception as e:
        print(f"员工表查询失败: {str(e)}")
    
    print("\n=== 检查完成 ===")