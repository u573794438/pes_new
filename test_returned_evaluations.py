from app import app
from models import EvaluationRecord, Employee
import sys

with app.app_context():
    # 获取当前用户（假设用户ID为1，实际应根据登录情况调整）
    # 这里我们直接查询第一个非管理员用户
    user = Employee.query.filter_by(is_admin=False).first()
    if not user:
        print("没有找到非管理员用户")
        sys.exit(1)
    
    print(f"测试用户: {user.name} (ID: {user.id})")
    
    # 查询该用户所有状态为'returned'的评估记录
    returned_evaluations = EvaluationRecord.query.filter_by(
        evaluator_id=user.id,
        status='returned'
    ).all()
    
    # 查询该用户所有符合条件的评估记录
    all_evaluations = EvaluationRecord.query.filter(
        EvaluationRecord.evaluator_id == user.id,
        EvaluationRecord.status.in_(['submitted', 'returned', 'withdrawal_requested'])
    ).all()
    
    print(f"符合条件的评估记录总数: {len(all_evaluations)}")
    print(f"状态为'returned'的评估记录数量: {len(returned_evaluations)}")
    
    # 模拟模板中的逻辑
    has_returned_evaluations = False
    for evaluation in all_evaluations:
        if evaluation.status == 'returned':
            has_returned_evaluations = True
            break
    
    print(f"模拟模板逻辑 - has_returned_evaluations: {has_returned_evaluations}")
    
    if has_returned_evaluations:
        print("按钮应该显示")
    else:
        print("按钮不应该显示")