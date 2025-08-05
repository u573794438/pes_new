from app import app, db
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
    
    # 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        print(f"- {table[0]}")
        
        # 检查评估表的结构
        if table[0] == 'evaluation':
            cursor.execute("PRAGMA table_info(evaluation);")
            columns = cursor.fetchall()
            print("  evaluation表列信息:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
    
    conn.close()
else:
    print("数据库文件不存在，请检查应用配置。")