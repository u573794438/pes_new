from app import app
from models import db

with app.app_context():
    # 获取所有表名
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print("数据库中的表:")
    for table in tables:
        print(f"- {table}")

    # 如果存在evaluation_scores表，检查其外键
    if 'evaluation_scores' in tables:
        print("\nevaluation_scores表的外键:")
        foreign_keys = inspector.get_foreign_keys('evaluation_scores')
        for fk in foreign_keys:
            print(f"- 列名: {fk['constrained_columns']}, 引用表: {fk['referred_table']}, 引用列: {fk['referred_columns']}")
    else:
        print("\n未找到evaluation_scores表")