from app import app
from extensions import db
from sqlalchemy import inspect

with app.app_context():
    # 获取数据库检查器
    inspector = inspect(db.engine)
    
    # 列出所有表
    print("当前数据库中的表:")
    tables = inspector.get_table_names()
    for table in tables:
        print(f"- {table}")
        
        # 打印表结构
        print("  列信息:")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']}: {column['type']} {column['nullable']}")
        
        # 打印外键
        print("  外键信息:")
        foreign_keys = inspector.get_foreign_keys(table)
        for fk in foreign_keys:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        print()