from app import app, db
from sqlalchemy import inspect, text
import pandas as pd

# 定义单复数表对
PLURAL_TABLE_PAIRS = [
    ('employee', 'employees'),
    ('evaluation_dimension', 'evaluation_dimensions'),
    ('evaluation_record', 'evaluation_records'),
    ('evaluation_score', 'evaluation_scores'),
    ('evaluation_task', 'evaluation_tasks')
]

def get_table_row_count(table_name):
    """获取表的行数"""
    with app.app_context():
        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        return result


def get_table_sample_data(table_name, limit=5):
    """获取表的样本数据"""
    with app.app_context():
        try:
            query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
            result = db.session.execute(query)
            columns = result.keys()
            data = result.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            print(f"获取表 {table_name} 样本数据时出错: {str(e)}")
            return None


def compare_table_data(singular_table, plural_table):
    """比较单复数表的数据差异"""
    print(f"\n=== 比较 {singular_table} 和 {plural_table} 表数据 ===")
    
    # 获取行数
    singular_count = get_table_row_count(singular_table)
    plural_count = get_table_row_count(plural_table)
    
    print(f"{singular_table} 表行数: {singular_count}")
    print(f"{plural_table} 表行数: {plural_count}")
    
    # 行数差异
    if singular_count != plural_count:
        print(f"行数差异: {abs(singular_count - plural_count)} 行")
    else:
        print("行数相同")
    
    # 获取样本数据
    singular_sample = get_table_sample_data(singular_table)
    plural_sample = get_table_sample_data(plural_table)
    
    # 显示样本数据
    if singular_sample is not None and not singular_sample.empty:
        print(f"\n{singular_table} 表样本数据:")
        print(singular_sample)
    
    if plural_sample is not None and not plural_sample.empty:
        print(f"\n{plural_table} 表样本数据:")
        print(plural_sample)
    
    # 分析迁移可行性
    print("\n=== 迁移可行性分析 ===")
    
    # 检查表结构是否相同
    with app.app_context():
        inspector = inspect(db.engine)
        try:
            singular_columns = inspector.get_columns(singular_table)
            plural_columns = inspector.get_columns(plural_table)
            
            # 比较列名和类型
            singular_col_names = [(col['name'], str(col['type'])) for col in singular_columns]
            plural_col_names = [(col['name'], str(col['type'])) for col in plural_columns]
            
            if singular_col_names == plural_col_names:
                print("表结构相同，列名和数据类型一致")
                structure_compatible = True
            else:
                print("表结构不同:")
                print(f"{singular_table} 列: {singular_col_names}")
                print(f"{plural_table} 列: {plural_col_names}")
                structure_compatible = False
        except Exception as e:
            print(f"检查表结构时出错: {str(e)}")
            structure_compatible = False
    
    # 给出迁移建议
    if structure_compatible:
        if singular_count == 0:
            print("建议: 单数表无数据，无需迁移")
        elif plural_count == 0:
            print(f"建议: 可以将 {singular_table} 表数据迁移到 {plural_table} 表")
            print(f"迁移语句示例: INSERT INTO {plural_table} SELECT * FROM {singular_table}")
        elif singular_count == plural_count:
            print("建议: 两表行数相同，需进一步验证数据是否一致后再决定是否迁移")
            print("验证语句示例: SELECT COUNT(*) FROM (SELECT * FROM {singular_table} EXCEPT SELECT * FROM {plural_table}) AS diff")
        else:
            print("建议: 表结构兼容但行数不同，需分析数据差异后再决定是否迁移")
    else:
        print("建议: 表结构不兼容，无法直接迁移数据")
        print("需要先调整表结构使其兼容，或编写自定义迁移脚本")


def main():
    """主函数"""
    print("=== 单复数表数据差异检查与迁移可行性分析 ===")
    
    for singular, plural in PLURAL_TABLE_PAIRS:
        compare_table_data(singular, plural)
    
    print("\n=== 分析完成 ===")
    print("总体建议:")
    print("1. 确认模型定义中使用的是复数表名")
    print("2. 清理冗余的单数表，避免数据不一致")
    print("3. 迁移前备份数据")
    print("4. 考虑使用数据库迁移工具如Alembic进行表结构和数据迁移")

if __name__ == '__main__':
    main()