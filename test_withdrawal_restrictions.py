import unittest
from flask import Flask
from extensions import db
from models import Employee, EvaluationRecord, EvaluationTask, EvaluationDimension, EvaluationScore
from app import app
import os
import tempfile

test_db_path = tempfile.mkstemp()[1]

class WithdrawalRestrictionsTest(unittest.TestCase):
    def setUp(self):
        # 配置测试环境
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.client = app.test_client()
        
        # 创建数据库表
        with app.app_context():
            db.create_all()
            
            # 创建测试用户
            self.evaluator = Employee(employee_id='10001', name='测试评估者', position='员工', is_admin=False)
            self.evaluator.set_password('password')
            
            self.evaluatee1 = Employee(employee_id='10002', name='测试被评估者1', position='员工', is_admin=False)
            self.evaluatee2 = Employee(employee_id='10003', name='测试被评估者2', position='员工', is_admin=False)
            
            # 创建测试任务
            self.task = EvaluationTask(year=2023, quarter=4, name='测试任务', status='published')
            
            # 创建测试维度
            self.dimension = EvaluationDimension(name='测试维度', weight=1.0)
            
            # 添加到数据库
            db.session.add_all([self.evaluator, self.evaluatee1, self.evaluatee2, self.task, self.dimension])
            db.session.commit()
            
            # 登录测试用户
            self.client.post('/login', data={
                'employee_id': '10001',
                'password': 'password'
            })
    
    def tearDown(self):
        # 清理测试环境
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.unlink(test_db_path)
    
    def test_batch_evaluation_with_pending_withdrawal(self):
        # 创建待审核的撤回申请
        with app.app_context():
            # 先创建已提交的评估记录
            record = EvaluationRecord(
                evaluator_id=self.evaluator.id,
                evaluatee_id=self.evaluatee1.id,
                task_id=self.task.id,
                status='submitted'
            )
            db.session.add(record)
            db.session.commit()
            
            # 然后将其状态改为撤回申请
            record.status = 'withdrawal_requested'
            record.withdrawal_reason = '测试撤回'
            db.session.commit()
        
        # 尝试访问批量评估页面
        response = self.client.get(f'/batch_evaluate?evaluator_id={self.evaluator.id}&task_id={self.task.id}')
        self.assertEqual(response.status_code, 200)
        
        # 验证页面中是否显示了警告信息
        response_data = response.data.decode('utf-8')
        self.assertIn('该任务已提交撤回申请，待审核中，不能发起新的评估', response_data)
        
        # 验证提交按钮是否被禁用
        self.assertIn('disabled="disabled"', response_data)
        self.assertIn('btn-success disabled', response_data)
    
    def test_batch_evaluation_without_pending_withdrawal(self):
        # 没有待审核的撤回申请
        
        # 尝试访问批量评估页面
        response = self.client.get(f'/batch_evaluate?evaluator_id={self.evaluator.id}&task_id={self.task.id}')
        self.assertEqual(response.status_code, 200)
        
        # 验证页面中是否没有显示警告信息
        response_data = response.data.decode('utf-8')
        self.assertNotIn('该任务已提交撤回申请，待审核中，不能发起新的评估', response_data)
        
        # 验证提交按钮是否未被禁用
        self.assertNotIn('disabled="disabled"', response_data)
        self.assertIn('btn-success', response_data) 
        
    def test_submit_batch_evaluation_with_pending_withdrawal(self):
        # 创建待审核的撤回申请
        with app.app_context():
            # 先创建已提交的评估记录
            record = EvaluationRecord(
                evaluator_id=self.evaluator.id,
                evaluatee_id=self.evaluatee1.id,
                task_id=self.task.id,
                status='submitted'
            )
            db.session.add(record)
            db.session.commit()
            
            # 然后将其状态改为撤回申请
            record.status = 'withdrawal_requested'
            record.withdrawal_reason = '测试撤回'
            db.session.commit()
        
        # 尝试提交批量评估
        response = self.client.post('/submit_batch_evaluation', data={
            'evaluator_id': self.evaluator.id,
            'task_id': self.task.id,
            f'scores[{self.evaluatee2.id}][{self.dimension.id}]': '3.5'
        }, follow_redirects=True)
        
        # 验证是否被重定向并显示错误消息
        self.assertEqual(response.status_code, 200)
        response_data = response.data.decode('utf-8')
        self.assertIn('该任务已提交撤回申请，待审核中，不能发起新的评估', response_data)

if __name__ == '__main__':
    unittest.main()