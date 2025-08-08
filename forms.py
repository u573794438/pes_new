from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, DecimalField, SubmitField, IntegerField, FloatField, FieldList, FormField, HiddenField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Regexp, EqualTo
from models import EvaluationTask
import datetime
import time
class LoginForm(FlaskForm):
    employee_id = StringField('员工ID', validators=[DataRequired()], filters=[lambda x: x.strip() if x else x])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class EmployeeForm(FlaskForm):
    employee_id = StringField('员工ID', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired()])
    position = StringField('职位', validators=[DataRequired()])
    role = SelectField('角色', validators=[DataRequired()], choices=[('员工', '员工'), ('部门负责人', '部门负责人'), ('部门经理', '部门经理'), ('分管领导', '分管领导')])
    position_coefficient = DecimalField('岗位系数', validators=[DataRequired(), NumberRange(min=0.1, max=3.0)], places=1)
    password = PasswordField('默认密码')
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        self.reset_password = kwargs.pop('reset_password', False)
        self.edit_id = kwargs.pop('edit_id', None)
        super(EmployeeForm, self).__init__(*args, **kwargs)

    def validate_employee_id(self, field):
        from models import Employee
        # 检查是否是密码重置场景
        if self.reset_password:
            return  # 密码重置场景下不检查ID是否存在
        
        # 获取表单提交的员工ID
        new_employee_id = field.data
        edit_id = getattr(self, 'edit_id', None)
        # 调试信息
        print(f"验证员工ID: new_employee_id={new_employee_id}, edit_id={edit_id}")
        
        # 检查ID是否存在于其他员工
        existing = Employee.query.filter_by(employee_id=new_employee_id).first()
        
        # 如果是编辑操作
        if edit_id:
            # 获取当前编辑的员工
            current_employee = Employee.query.get(edit_id)
            print(f"当前编辑员工: {current_employee}, ID: {current_employee.employee_id if current_employee else None}")
            
            # 如果当前员工存在且ID与提交的ID相同，允许更新
            if current_employee and current_employee.employee_id == new_employee_id:
                print(f"编辑操作且ID未变化: {new_employee_id}")
                return
            # 如果存在其他员工使用相同ID
            elif existing and existing.id != edit_id:
                print(f"存在其他员工使用ID: {new_employee_id}")
                raise ValidationError('该人员ID已存在，请使用其他ID')
        # 非编辑操作（添加）
        elif existing:
            print(f"添加操作时ID已存在: {new_employee_id}")
            raise ValidationError('该人员ID已存在，请使用其他ID')

class EmployeeImportForm(FlaskForm):
    file = FileField('Excel文件', validators=[FileRequired(), FileAllowed(['xlsx'], '只允许上传XLSX文件')])
    submit = SubmitField('导入')

class DimensionForm(FlaskForm):
    name = StringField('维度名称', validators=[DataRequired(), Length(max=100)])
    weight = DecimalField('权重 (0-1)', validators=[DataRequired(), NumberRange(min=0, max=1)])
    submit = SubmitField('提交')

    def validate_weight(form, field):
        # 检查总权重是否超过1
        if hasattr(form, 'total_weight') and form.total_weight + float(field.data) > 1.0001:
            raise ValidationError('所有维度权重总和不能超过100%')

class ScoreForm(FlaskForm):
    dimension_id = HiddenField(validators=[DataRequired()])
    score = DecimalField('评分', validators=[DataRequired(), NumberRange(min=1, max=5)])

class EvaluationForm(FlaskForm):

    task_id = SelectField('评估任务', coerce=int, validators=[DataRequired()])
    scores = FieldList(FormField(ScoreForm), min_entries=0)
    submit = SubmitField('提交评估')

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)
        from models import Employee, EvaluationTask
        # 加载评估者选项

        # 加载评估任务选项
        self.task_id.choices = [(t.id, t.name) for t in EvaluationTask.query.filter_by(status='published').order_by(EvaluationTask.year.desc(), EvaluationTask.quarter.desc()).all()]

class EvaluationTaskForm(FlaskForm):
    year = StringField('年份', validators=[
        DataRequired(),
        Length(min=2, max=2, message='年份必须为2位数字'),
        Regexp(r'^\d{2}$', message='年份必须为2位数字')
    ])
    quarter = IntegerField('季度', validators=[
        DataRequired(),
        NumberRange(min=1, max=4, message='季度必须为1-4之间的整数')
    ])
    submit = SubmitField('发布任务')

    def __init__(self, *args, **kwargs):
        from flask import request
        import datetime
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1
        
        # 先生成动态选项
        self.year.choices = [(y, str(y)) for y in range(current_year - 2, current_year + 3)]
        self.quarter.choices = [(1, '第一季度'), (2, '第二季度'), (3, '第三季度'), (4, '第四季度')]
        
        # 调用父类构造函数处理表单数据
        super(EvaluationTaskForm, self).__init__(*args, **kwargs)
        

        
        # 初始加载时设置默认值
        if not self.is_submitted():
            self.year.default = current_year
            self.quarter.default = current_quarter
            self.process()

    def validate(self):
        if not super(EvaluationTaskForm, self).validate():
            return False
        existing_task = EvaluationTask.query.filter_by(
            year=self.year.data, 
            quarter=self.quarter.data
        ).first()
        if existing_task:
            self.year.errors.append('该年份和季度的任务已存在，请选择其他季度或年份。')
            return False
        return True

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=8, message='密码长度至少为8个字符'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)', message='密码必须包含字母和数字')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('修改密码')

class EvaluationSearchForm(FlaskForm):
    evaluatee_id = SelectField('评估对象', coerce=int, validators=[DataRequired()])
    submit = SubmitField('查询')

    def __init__(self, *args, **kwargs):
        super(EvaluationSearchForm, self).__init__(*args, **kwargs)
        from models import Employee
        # 加载评估对象选项
        self.evaluatee_id.choices = [(e.id, e.name) for e in Employee.query.all()]