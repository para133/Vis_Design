import os

from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'visData.db')
db = SQLAlchemy()

class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 外键关联到用户表
    platform = db.Column(db.String, nullable=False)             # 'wechat' 或 'alipay'
    transaction_time = db.Column(db.DateTime, nullable=False)     # 交易时间
    category = db.Column(db.String, nullable=True)              # 支付宝: 交易分类，微信: 交易类型
    counterparty = db.Column(db.String, nullable=True)          # 对方名称
    product = db.Column(db.String, nullable=True)               # 产品或服务名称
    income_or_expense = db.Column(db.String, nullable=False)    # 'income' 或 'expense'
    amount = db.Column(db.Float, nullable=False)                # 金额
    payment_method = db.Column(db.String, nullable=True)        # 支付方式
    current_status = db.Column(db.String, nullable=True)        # 交易状态
    transaction_id = db.Column(db.String, nullable=False)       # 交易号
    merchant_id = db.Column(db.String, nullable=True)           # 商户号
    remarks = db.Column(db.String, nullable=True)               # 备注

    def __repr__(self):
        return f'<Bill {self.user_id} {self.platform} {self.id}: {self.transaction_time} - {self.amount}>'
    
    
# 存储在 data/visData.db 的用户表
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # 一对多关系：一个用户可以有多条账单
    bills = db.relationship('Bill', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
        
    
