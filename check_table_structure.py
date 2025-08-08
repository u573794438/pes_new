import sqlite3

# 连接到数据库
conn = sqlite3.connect('performance_evaluation.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("数据库中的表:")
for table in tables:
    print(f"- {table[0]}")

# 检查evaluation_scores表结构
if any('evaluation_scores' in table for table in tables):
    print("\nevaluation_scores表结构:")
    cursor.execute("PRAGMA table_info(evaluation_scores)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]}: {column[2]}")
else:
    print("\n未找到evaluation_scores表")

# 检查evaluation_score表结构(旧表名)
if any('evaluation_score' in table for table in tables):
    print("\nevaluation_score表结构:")
    cursor.execute("PRAGMA table_info(evaluation_score)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]}: {column[2]}")
else:
    print("\n未找到evaluation_score表")

# 关闭连接
conn.close()