from app import app
from extensions import db
from sqlalchemy import text

# 要清除的表列表
TABLES_TO_CLEAR = [
    'employees',
    'evaluation_dimensions',
    'evaluation_records',
    'evaluation_scores',
    'evaluation_tasks'
]

with app.app_context():
    print("开始清除数据库表...")
    
    for table in TABLES_TO_CLEAR:
        try:
            # 使用TRUNCATE语句清除表数据
            db.session.execute(text(f"TRUNCATE TABLE {table}"))
            db.session.commit()
            print(f"成功清除表: {table}")
        except Exception as e:
            # 如果TRUNCATE失败（可能因为有外键约束），尝试DELETE
            try:
                db.session.rollback()
                db.session.execute(text(f"DELETE FROM {table}"))
                db.session.commit()
                print(f"使用DELETE成功清除表: {table}")
            except Exception as delete_error:
                db.session.rollback()
                print(f"清除表 {table} 失败: {str(delete_error)}")
    
    print("清除操作完成")