from app import app, db
from sqlalchemy import inspect

# 定义单复数表对
PLURAL_TABLE_PAIRS = [
    ('employee', 'employees'),
    ('evaluation_dimension', 'evaluation_dimensions'),
    ('evaluation_record', 'evaluation_records'),
    ('evaluation_score', 'evaluation_scores'),
    ('evaluation_task', 'evaluation_tasks')
]

def get_table_columns(table_name):
    """获取表的列信息"""
    inspector = inspect(db.engine)
    try:
        columns = inspector.get_columns(table_name)
        return {col['name']: col for col in columns}
    except Exception as e:
        print(f"获取表 {table_name} 结构时出错: {str(e)}")
        return {}


def compare_table_structures(table1, table2):
    """比较两个表的结构差异"""
    print(f"\n=== 比较 {table1} 和 {table2} 表结构 ===")
    
    # 获取两个表的列信息
    cols1 = get_table_columns(table1)
    cols2 = get_table_columns(table2)
    
    if not cols1 or not cols2:
        print("无法获取表结构，比较失败。")
        return
    
    # 找出差异
    only_in_table1 = [col for col in cols1 if col not in cols2]
    only_in_table2 = [col for col in cols2 if col not in cols1]
    common_columns = [col for col in cols1 if col in cols2]
    
    # 打印结果
    if only_in_table1:
        print(f"仅在 {table1} 中存在的列:")
        for col in only_in_table1:
            print(f"- {col} ({cols1[col]['type']})")
    
    if only_in_table2:
        print(f"仅在 {table2} 中存在的列:")
        for col in only_in_table2:
            print(f"- {col} ({cols2[col]['type']})\n")
    
    if common_columns:
        print(f"两表共有的列及其类型差异:")
        print("{:<20} {:<20} {:<20} {:<10}".format("列名", f"{table1} 类型", f"{table2} 类型", "状态"))
        for col in common_columns:
            type1 = str(cols1[col]['type'])
            type2 = str(cols2[col]['type'])
            status = "相同" if type1 == type2 else "不同"
            print("{:<20} {:<20} {:<20} {:<10}".format(col, type1, type2, status))
    
    if not only_in_table1 and not only_in_table2 and common_columns:
        print(f"\n结论: {table1} 和 {table2} 表结构完全相同。")
    elif common_columns:
        print(f"\n结论: {table1} 和 {table2} 表结构存在差异。")
    else:
        print(f"\n结论: 未找到共同列，表结构完全不同。")


def main():
    """主函数"""
    print("=== 数据库单复数表结构比较 ===")
    
    with app.app_context():
        # 遍历所有单复数表对进行比较
        for singular, plural in PLURAL_TABLE_PAIRS:
            compare_table_structures(singular, plural)

if __name__ == '__main__':
    main()