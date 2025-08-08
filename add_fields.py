from flask import Flask
from extensions import db
from models import Employee
import os

basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'performance_evaluation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # 检查并添加role字段
    try:
        # 使用SQL直接添加字段
        db.session.execute('ALTER TABLE employee ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT \'员工\'')
        print('Added role column')
    except Exception as e:
        print(f'Error adding role column: {e}')
        pass

    # 检查并添加position_coefficient字段
    try:
        db.session.execute('ALTER TABLE employee ADD COLUMN position_coefficient FLOAT NOT NULL DEFAULT 1.0')
        print('Added position_coefficient column')
    except Exception as e:
        print(f'Error adding position_coefficient column: {e}')
        pass

    db.session.commit()
    print('Database updated successfully')