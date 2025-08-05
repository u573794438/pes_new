import sqlite3
import os

# 数据库文件路径
db_path = os.path.join(os.getcwd(), 'performance_evaluation.db')
print(f"数据库文件路径: {db_path}")
print(f"数据库文件是否存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询第一个非管理员员工
    cursor.execute("SELECT id, name FROM employee WHERE is_admin = 0 LIMIT 1;")
    user = cursor.fetchone()
    if not user:
        print("没有找到非管理员用户")
        conn.close()
        exit(1)
    
    user_id, user_name = user
    print(f"测试用户: {user_name} (ID: {user_id})")
    
    # 查询该用户所有状态为'returned'的评估记录
    cursor.execute("SELECT COUNT(*) FROM evaluation_record WHERE evaluator_id = ? AND status = 'returned';", (user_id,))
    returned_count = cursor.fetchone()[0]
    
    # 查询该用户所有符合条件的评估记录
    cursor.execute("SELECT COUNT(*) FROM evaluation_record WHERE evaluator_id = ? AND status IN ('submitted', 'returned', 'withdrawal_requested');", (user_id,))
    all_count = cursor.fetchone()[0]
    
    print(f"符合条件的评估记录总数: {all_count}")
    print(f"状态为'returned'的评估记录数量: {returned_count}")
    
    # 模拟模板中的逻辑
    has_returned_evaluations = returned_count > 0
    
    print(f"模拟模板逻辑 - has_returned_evaluations: {has_returned_evaluations}")
    
    if has_returned_evaluations:
        print("按钮应该显示")
    else:
        print("按钮不应该显示")
    
    conn.close()
else:
    print("数据库文件不存在，请检查应用配置。")