from app import app
from extensions import db

with app.app_context():
    # 检查字段是否已存在
    inspector = db.inspect(db.engine)
    columns = inspector.get_columns('employee')
    column_names = [col['name'] for col in columns]

    if 'is_frozen' not in column_names:
        # 添加is_frozen字段
        db.engine.execute('ALTER TABLE employee ADD COLUMN is_frozen BOOLEAN DEFAULT 0')
        print('成功添加is_frozen字段')
    else:
        print('is_frozen字段已存在')