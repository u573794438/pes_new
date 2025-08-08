from extensions import db
from flask_login import UserMixin
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
class Employee(UserMixin, db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_frozen = db.Column(db.Boolean, default=False)
    # 角色字段：员工、部门经理、部门负责人、分管领导
    role = db.Column(db.String(20), default='员工', nullable=False)
    # 岗位系数字段，精确到一位小数
    position_coefficient = db.Column(db.Float, default=1.0, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Employee {self.name}>'

class EvaluationDimension(db.Model):
    __tablename__ = 'evaluation_dimensions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='published', nullable=False)
    weight = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Dimension {self.name} ({self.weight*100}%)>'

class EvaluationRecord(db.Model):
    __tablename__ = 'evaluation_records'
    id = db.Column(db.Integer, primary_key=True)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    evaluatee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('evaluation_tasks.id'), nullable=False)
    status = db.Column(db.String(20), default='submitted')  # submitted, returned, withdrawal_requested
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    withdrawal_reason = db.Column(db.Text)

    # 关系
    evaluator = db.relationship('Employee', foreign_keys=[evaluator_id], backref='evaluations_made')
    evaluatee = db.relationship('Employee', foreign_keys=[evaluatee_id], backref='evaluations_received')
    scores = db.relationship('EvaluationScore', cascade='all, delete-orphan', lazy=True)
    task = db.relationship('EvaluationTask', back_populates='records')

    def __repr__(self):
        return f'<Evaluation {self.evaluator.name} -> {self.evaluatee.name} ({self.status})>'

    @property
    def total_score(self):
        # 仅计算已发布维度的加权总分 (5分制 -> 百分制)
        published_scores = self.scores  # 包含所有维度的评分，不限制发布状态
        total = sum(score.score * score.dimension.weight for score in published_scores)
        # 验证权重总和是否超过1.0，防止总分超过100
        total_weight = sum(score.dimension.weight for score in published_scores)
        if total_weight == 0:
            return 0  # 避免除以零错误
        if total_weight > 1.0001:
            from flask import current_app
            current_app.logger.warning(f"评估维度权重总和超过100%: {total_weight:.4f}")
        return round(min(total * 20, 100.0), 2)  # 确保总分不超过100分

class EvaluationTask(db.Model):
    __tablename__ = 'evaluation_tasks'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)  # 1-4
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='published', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系: 一个任务包含多个评估记录，删除任务时级联删除所有相关评估记录
    records = db.relationship('EvaluationRecord', back_populates='task', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return self.name
    
    def __lt__(self, other):
        if self.year != other.year:
            return self.year < other.year
        return self.quarter < other.quarter

class EvaluationScore(db.Model):
    __tablename__ = 'evaluation_scores'

    id = db.Column(db.Integer, primary_key=True)
    evaluation_record_id = db.Column(db.Integer, db.ForeignKey('evaluation_records.id'), nullable=False)
    dimension_id = db.Column(db.Integer, db.ForeignKey('evaluation_dimensions.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(500))

    # 关系
    record = db.relationship('EvaluationRecord', overlaps="scores")
    dimension = db.relationship('EvaluationDimension')

    def __repr__(self):
        return f'<EvaluationScore {self.evaluation_record_id}-{self.dimension_id}: {self.score}>'


class DimensionDefaultScore(db.Model):
    __tablename__ = 'dimension_default_scores'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False)
    dimension_id = db.Column(db.Integer, db.ForeignKey('evaluation_dimensions.id'), nullable=False)
    default_score = db.Column(db.Float, nullable=False)

    # 确保每个用户对每个维度只有一个默认值
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'dimension_id'),
    )

    # 关系
    employee = db.relationship('Employee', backref=db.backref('dimension_defaults', lazy=True))
    dimension = db.relationship('EvaluationDimension')

    def __repr__(self):
        return f'<DimensionDefaultScore {self.employee_id}-{self.dimension_id}: {self.default_score}>'