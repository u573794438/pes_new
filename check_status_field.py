from flask import Flask
from extensions import db
from models import EvaluationRecord
import os

basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'performance_evaluation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # 查询不同状态的记录数量
    status_counts = db.session.query(
        EvaluationRecord.status,
        db.func.count(EvaluationRecord.id)
    ).group_by(EvaluationRecord.status).all()

    print("评估记录状态分布:")
    for status, count in status_counts:
        print(f'{status}: {count} 条')

    # 查询所有记录的状态
    all_statuses = db.session.query(EvaluationRecord.status).all()
    print(f'\n总记录数: {len(all_statuses)}')
    if len(all_statuses) > 0:
        print(f'第一条记录状态: {all_statuses[0][0]}')