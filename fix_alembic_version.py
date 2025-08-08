import sqlite3

# 连接到数据库
conn = sqlite3.connect('performance_evaluation.db')
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
if cursor.fetchone():
    # 删除表中的所有记录
    cursor.execute("DELETE FROM alembic_version")
    print("已清除alembic_version表中的记录")
else:
    print("alembic_version表不存在")

# 提交更改并关闭连接
conn.commit()
conn.close()