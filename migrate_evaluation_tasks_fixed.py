from app import app
from extensions import db
from models import EvaluationTask
from datetime import datetime
import logging
import pandas as pd

def migrate_evaluation_tasks():
    with app.app_context():
        try:
            # 查询旧表evaluation_task中的所有记录
            old_tasks = db.session.execute('SELECT * FROM evaluation_task').fetchall()
            logging.info(f"找到 {len(old_tasks)} 条旧任务记录")

            # 获取旧表的列名
            old_columns = [desc[0] for desc in db.session.execute('SELECT * FROM evaluation_task LIMIT 0').cursor.description]
            logging.info(f"旧表列名: {old_columns}")

            # 获取新表的列名（排除id，因为它是自增主键）
            new_columns = [column.name for column in EvaluationTask.__table__.columns if column.name != 'id']
            logging.info(f"新表列名: {new_columns}")

            # 计算交集，按字段名迁移
            common_columns = list(set(old_columns) & set(new_columns))
            logging.info(f"共同列名: {common_columns}")

            # 迁移数据
            migrated_count = 0
            for old_task in old_tasks:
                # 创建新任务字典
                new_task_data = {col: getattr(old_task, col) for col in common_columns}

                # 处理日期时间字段
                datetime_columns = ['created_at', 'updated_at']
                for col in datetime_columns:
                    if col in new_task_data and new_task_data[col] is not None:
                        # 尝试转换字符串到datetime
                        try:
                            if isinstance(new_task_data[col], str):
                                # 处理不同的日期时间格式
                                if 'Z' in new_task_data[col]:
                                    # ISO格式带时区
                                    new_task_data[col] = datetime.fromisoformat(new_task_data[col].replace('Z', '+00:00'))
                                else:
                                    # 尝试常见格式
                                    for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                                        try:
                                            new_task_data[col] = datetime.strptime(new_task_data[col], fmt)
                                            break
                                        except ValueError:
                                            continue
                        except Exception as e:
                            logging.warning(f"转换字段 {col} 的值 {new_task_data[col]} 到datetime失败: {str(e)}")
                            new_task_data[col] = datetime.utcnow()
                    elif col not in new_task_data:
                        # 如果字段不存在，设置默认值
                        new_task_data[col] = datetime.utcnow()

                # 处理status字段
                if 'status' not in new_task_data or new_task_data['status'] is None:
                    new_task_data['status'] = 'published'

                # 创建新任务记录
                new_task = EvaluationTask(**new_task_data)
                db.session.add(new_task)
                migrated_count += 1

            db.session.commit()
            logging.info(f"成功迁移 {migrated_count} 条记录到evaluation_tasks表")
            return True, f"迁移成功，共迁移 {migrated_count} 条记录"

        except Exception as e:
            db.session.rollback()
            logging.error(f"迁移过程中出错: {str(e)}")
            return False, f"迁移失败: {str(e)}"

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    success, message = migrate_evaluation_tasks()
    print(f"=== {'迁移成功' if success else '迁移失败'} ===")
    print(message)