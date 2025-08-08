from app import app, db
from models import EvaluationRecord, EvaluationScore

def fix_relationship_warning():
    """修复SQLAlchemy关系警告"""
    print("=== 修复SQLAlchemy关系警告 ===")
    
    # 解释问题
    print("问题原因:")
    print("- EvaluationScore模型中的record关系和EvaluationRecord模型中的scores关系存在冲突")
    print("- 两个关系都试图映射到同一个外键列evaluation_scores.evaluation_record_id")
    
    # 查看当前关系定义
    print("\n当前关系定义:")
    print(f"- EvaluationRecord.scores: {repr(EvaluationRecord.scores)}")
    print(f"- EvaluationScore.record: {repr(EvaluationScore.record)}")
    
    # 应用修复
    print("\n应用修复...")
    try:
        # 注意：这里不能直接修改模型类，因为SQLAlchemy不允许运行时修改映射
        # 我们只能输出修复建议
        print("\n修复建议已生成，请手动修改models.py文件:")
        print("\n1. 在EvaluationRecord类中，修改scores关系:")
        print("scores = db.relationship('EvaluationScore', cascade='all, delete-orphan', lazy=True, back_populates='record')")
        print("\n2. 在EvaluationScore类中，修改record关系:")
        print("record = db.relationship('EvaluationRecord', back_populates='scores')")
        print("\n或者，如果不想建立双向关系，只需添加overlaps参数:")
        print("record = db.relationship('EvaluationRecord', overlaps='scores')")
        print("\n修复完成后，警告将不再出现。")
    except Exception as e:
        print(f"修复过程中出错: {str(e)}")


def explain_table_issue():
    """解释表名复数问题"""
    print("\n=== 表名复数问题解释 ===")
    print("问题原因:")
    print("- 从models.py可以看出，所有模型都明确指定了复数形式的表名")
    print("- 但系统启动时创建了单数和复数两种形式的表")
    print("- 这很可能是因为应用中存在以下问题之一:")
    print("  1. 存在未在当前models.py中定义的旧模型")
    print("  2. 数据库迁移脚本创建了额外的表")
    print("  3. 应用中存在重复的模型定义")
    
    print("\n解决方案建议:")
    print("1. 检查并删除未使用的旧模型文件")
    print("2. 检查迁移脚本，确保只创建需要的表")
    print("3. 清理数据库，删除不需要的单数表")
    print("4. 确保所有模型都明确设置__tablename__属性")

if __name__ == '__main__':
    with app.app_context():
        fix_relationship_warning()
        explain_table_issue()