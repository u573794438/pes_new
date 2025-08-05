from app import app, db
from models import Evaluation, User
import sys

with app.app_context():
    # 获取当前用户（假设用户ID为1，实际应根据登录情况调整）
    user_id = 1
    user = User.query.get(user_id)
    if not user:
        print(f"用户ID {user_id} 不存在")
        sys.exit(1)
    
    # 查询该用户所有状态为'returned'的评估记录
    returned_evaluations = Evaluation.query.filter_by(
        user_id=user_id,
        status='returned'
    ).all()
    
    total_evaluations = Evaluation.query.filter_by(user_id=user_id).count()
    
    print(f"用户 {user.username} (ID: {user_id}) 的评估记录总数: {total_evaluations}")
    print(f"状态为'returned'的评估记录数量: {len(returned_evaluations)}")
    
    if returned_evaluations:
        print("已退回评估记录详情:")
        for eval in returned_evaluations:
            print(f"- 评估ID: {eval.id}, 任务ID: {eval.task_id}, 提交时间: {eval.submitted_at}")
    else:
        print("没有找到已退回的评估记录")