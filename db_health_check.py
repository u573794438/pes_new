from app import app
from extensions import db
from sqlalchemy import inspect, text

with app.app_context():
    print("=== 数据库健康检查报告 ===")
    
    # 获取数据库检查器
    inspector = inspect(db.engine)
    
    # 列出所有表
    tables = inspector.get_table_names()
    print(f"总表数量: {len(tables)}")
    print("\n表列表:")
    for table in tables:
        print(f"- {table}")
    
    # 检查重复表名（单数/复数形式）
    print("\n=== 重复表名检查 ===")
    singular_plural_pairs = []
    checked = set()
    for table in tables:
        if table in checked:
            continue
        if table.endswith('s'):
            singular = table[:-1]
            if singular in tables:
                singular_plural_pairs.append((singular, table))
                checked.add(singular)
                checked.add(table)
        else:
            plural = table + 's'
            if plural in tables:
                singular_plural_pairs.append((table, plural))
                checked.add(table)
                checked.add(plural)
    
    if singular_plural_pairs:
        print("发现以下单数/复数形式的重复表:")
        for singular, plural in singular_plural_pairs:
            print(f"- {singular} 和 {plural}")
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