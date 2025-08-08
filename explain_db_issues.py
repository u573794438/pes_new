from app import app, db
from models import Employee, EvaluationDimension, EvaluationRecord, EvaluationTask, EvaluationScore

def explain_table_creation():
    """解释为什么会创建复数名称的表"""
    print("=== 数据库表创建问题解释 ===")
    print("1. 为何系统启动时会创建复数名称的表？")
    
    # 检查模型定义的表名
    print("\n在models.py中定义的表名:")
    models = [Employee, EvaluationDimension, EvaluationRecord, EvaluationTask, EvaluationScore]
    for model in models:
        print(f"- {model.__name__} 模型: __tablename__ = '{model.__tablename__}'")
    
    # 查看实际数据库中的表
    print("\n系统启动时创建的表(来自日志):")
    created_tables = ['alembic_version', 'dimension_default_scores', 'employee', 'employees', 'evaluation_dimension', 'evaluation_dimensions', 'evaluation_record', 'evaluation_records', 'evaluation_score', 'evaluation_scores', 'evaluation_task', 'evaluation_tasks']
    print(', '.join(created_tables))
    
    # 分析问题
    print("\n问题分析:")
    print("- 从models.py可以看出，所有模型都明确指定了复数形式的表名")
    print("- 但系统启动时创建了单数和复数两种形式的表")
    print("- 这可能是因为应用中存在重复定义或迁移脚本问题")
    print("- 单数表名可能来自其他未在models.py中定义的模型或旧版本的迁移")


def explain_relationship_warning():
    """解释SQLAlchemy关系警告"""
    print("\n=== SQLAlchemy关系警告解释 ===")
    print("2. 系统启动时显示的SQLAlchemy警告是什么意思？")
    
    # 显示警告内容
    print("\n警告内容:")
    print("SAWarning: relationship 'EvaluationScore.record' will copy column evaluation_records.id to column evaluation_scores.evaluation_record_id, which conflicts with relationship(s): 'EvaluationRecord.scores' (copies evaluation_records.id to evaluation_scores.evaluation_record_id).")
    
    # 分析问题
    print("\n问题分析:")
    print("- 这个警告表明在EvaluationScore模型中的record关系和EvaluationRecord模型中的scores关系存在冲突")
    print("- 两个关系都试图映射到同一个外键列evaluation_scores.evaluation_record_id")
    
    # 查看当前关系定义
    print("\n当前关系定义:")
    print(f"- EvaluationRecord.scores: {repr(EvaluationRecord.scores)}")
    print(f"- EvaluationScore.record: {repr(EvaluationScore.record)}")
    
    # 解决方案
    print("\n解决方案:")
    print("- 修改EvaluationScore.record关系，添加overlaps=\"scores\"参数")
    print("- 或者使用back_populates参数正确连接两个关系")
    print("\n建议的修改:")
    print("在models.py文件中，将EvaluationScore类中的record关系修改为:")
    print("record = db.relationship('EvaluationRecord', overlaps=\"scores\")")
    print("或者更推荐的方式是使用back_populates:")
    print("record = db.relationship('EvaluationRecord', back_populates=\"scores\")")
    print("同时在EvaluationRecord类中的scores关系添加back_populates:")
    print("scores = db.relationship('EvaluationScore', cascade='all, delete-orphan', lazy=True, back_populates=\"record\")")

if __name__ == '__main__':
    with app.app_context():
        explain_table_creation()
        explain_relationship_warning()