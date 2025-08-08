from app import app, db
from sqlalchemy import text

def migrate_employee_data():
    """将employee表数据迁移至employees表"""
    print("=== 开始迁移employee表数据到employees表 ===")

    with app.app_context():
        try:
            # 获取employee表的所有记录
            source_query = text("SELECT * FROM employee")
            source_results = db.session.execute(source_query).fetchall()
            source_columns = source_results[0].keys() if source_results else []

            # 获取employees表的字段名
            target_query = text("PRAGMA table_info(employees)")
            target_columns_info = db.session.execute(target_query).fetchall()
            target_columns = [col[1] for col in target_columns_info]

            # 计算字段映射关系
            common_columns = [col for col in source_columns if col in target_columns]
            missing_in_source = [col for col in target_columns if col not in source_columns]

            print(f"源表(employee)字段: {source_columns}")
            print(f"目标表(employees)字段: {target_columns}")
            print(f"共有字段: {common_columns}")
            print(f"目标表中有但源表中没有的字段: {missing_in_source}")

            # 准备迁移数据
            migrated_count = 0
            skipped_count = 0

            for record in source_results:
                # 将记录转换为字典
                record_dict = dict(record._mapping)

                # 检查employee_id是否已存在
                check_query = text("SELECT COUNT(*) FROM employees WHERE employee_id = :employee_id")
                exists = db.session.execute(check_query, {'employee_id': record_dict['employee_id']}).scalar() > 0

                if exists:
                    print(f"跳过已存在的记录: employee_id={record_dict['employee_id']}")
                    skipped_count += 1
                    continue

                # 准备插入数据
                insert_data = {col: record_dict[col] for col in common_columns}

                # 填充缺失字段
                if 'role' in missing_in_source:
                    insert_data['role'] = '员工'
                if 'position_coefficient' in missing_in_source:
                    insert_data['position_coefficient'] = 1.0

                # 构建插入语句
                columns_str = ', '.join(insert_data.keys())
                placeholders = ', '.join([f":{col}" for col in insert_data.keys()])
                insert_query = text(f"INSERT INTO employees ({columns_str}) VALUES ({placeholders})")

                # 执行插入
                db.session.execute(insert_query, insert_data)
                migrated_count += 1

            # 提交事务
            db.session.commit()

            print(f"迁移完成: 成功迁移 {migrated_count} 条记录, 跳过 {skipped_count} 条记录")
            print("=== 迁移操作完成 ===")

        except Exception as e:
            db.session.rollback()
            print(f"迁移过程中出错: {str(e)}")
            print("=== 迁移操作失败 ===")

def main():
    """主函数"""
    migrate_employee_data()

if __name__ == '__main__':
    main()