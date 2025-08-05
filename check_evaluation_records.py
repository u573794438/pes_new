import sqlite3
import os

# 检查数据库文件是否存在
db_path = os.path.join(os.getcwd(), 'performance_evaluation.db')
print(f"数据库文件路径: {db_path}")
print(f"数据库文件是否存在: {os.path.exists(db_path)}")

# 连接数据库并检查表结构
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查evaluation_record表的结构
    cursor.execute("PRAGMA table_info(evaluation_record);")
    columns = cursor.fetchall()
    print("evaluation_record表列信息:")
    for column in columns:
        print(f"- {column[1]} ({column[2]})")
    
    # 检查evaluation_record表中的记录状态
    cursor.execute("SELECT status, COUNT(*) FROM evaluation_record GROUP BY status;")
    status_counts = cursor.fetchall()
    print("评估记录状态统计:")
    for status, count in status_counts:
        print(f"- {status}: {count}条")
    
    # 检查是否有用户相关的表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%';")
    user_tables = cursor.fetchall()
    print("用户相关的表:")
    for table in user_tables:
        print(f"- {table[0]}")
    
    conn.close()
else:
    print("数据库文件不存在，请检查应用配置。")