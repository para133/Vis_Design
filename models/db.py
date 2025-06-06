import csv
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask import Flask
from models.data import User, Bill

class BillDataBase:
    def __init__(self, app: Flask, db: SQLAlchemy):
        self.app = app
        self.db = db
        with self.app.app_context():
            self.db.create_all()
            
    # 获取用户
    def get_user(self, userinfo):
        if isinstance(userinfo, int):
            # 如果传入的是用户ID
            user = User.query.get(userinfo)
        elif isinstance(userinfo, str):
            user = User.query.filter_by(username=userinfo).first()
        return user
        
    # 添加用户
    def add_user(self, username: str, password: str):
        existing = User.query.filter_by(username=username).first()
        # 如果用户已存在
        if existing:
            return None
        user = User(username=username, password=password)
        self.db.session.add(user)
        self.db.session.commit()
        return user
        
    # 保存账单数据
    def save_bill(self, bill_path, user_id):
        user = User.query.get(user_id)
        encoding = 'utf-8'
        try:
            with open(bill_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if '微信支付账单明细' in first_line:
                    platform = 'wechat'
                else:
                    platform = 'alipay'
        except Exception as e:
            encoding = 'gbk'
            with open(bill_path, 'r', encoding='gbk') as f:
                first_line = f.readline().strip()
                if '微信支付账单明细' in first_line:
                    platform = 'wechat'
                else:
                    platform = 'alipay'
                
        if platform == 'wechat':
            self.import_wechat_csv(bill_path, user,encoding)
        elif platform == 'alipay':
            self.import_alipay_csv(bill_path, user,encoding)
    
    # 按照日期获取用户的账单
    def get_bills(self, user_id, start_date=None, end_date=None):
        query = Bill.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        return query.all()
    
    # 获取用户最新的账单日期
    def get_latest_billdate(self, user_id):
        latest_bill = Bill.query.filter_by(user_id=user_id).order_by(Bill.transaction_time.desc()).first()
        if latest_bill:
            return latest_bill.transaction_time
        else:
            return datetime.now()
        
    # 获取用户最早的账单日期
    def get_earliest_billdate(self, user_id):
        earliest_bill = Bill.query.filter_by(user_id=user_id).order_by(Bill.transaction_time.asc()).first()
        if earliest_bill:
            return earliest_bill.transaction_time
        else:
            return datetime.now()
    
    def import_wechat_csv(self, bill_path, user: User,encoding):
        with open(bill_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            # 跳过头部说明行
            while True:
                line = next(reader)
                if line and line[0].startswith('交易时间'):
                    header = line
                    break

            for row in reader:
                if len(row) < 11:  # 跳过空行或分隔行
                    continue
                transaction_time = row[0]
                category = row[1]
                counterparty = row[2]
                product = row[3]
                income_or_expense = row[4]
                amount = row[5].replace('¥', '').replace(',', '').strip()
                payment_method = row[6]
                current_status = row[7]
                transaction_id = row[8]
                merchant_id = row[9]
                remarks = row[10]

                # 跳过中性交易
                if income_or_expense == '/':
                    continue
                
                # 跳过已经存在的交易
                existing = Bill.query.filter_by(transaction_id=transaction_id, user_id=user.id).first()
                if existing:
                    continue
                
                bill = Bill(
                    user_id=user.id,
                    platform='微信',
                    transaction_time=datetime.strptime(transaction_time, "%Y-%m-%d %H:%M:%S"),
                    category=category,
                    counterparty=counterparty,
                    product=product,
                    income_or_expense=income_or_expense,
                    amount=float(amount),
                    payment_method=payment_method,
                    current_status=current_status,
                    transaction_id=transaction_id,
                    merchant_id=merchant_id,
                    remarks=remarks
                )

                self.db.session.add(bill)
            self.db.session.commit()
            
    def import_alipay_csv(self, bill_path, user: User,encoding):
        with open(bill_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            # 跳过头部说明行
            while True:
                line = next(reader)
                if line and line[0].startswith('交易时间'):
                    header = line
                    break            

            for row in reader:
                if len(row) < 12:
                    continue
                transaction_time = row[0]
                category = row[1]
                counterparty = row[2]
                # row[3]：对方账号
                product = row[4]
                income_or_expense = row[5]
                amount_str = row[6].replace(',', '').strip()
                payment_method = row[7]
                current_status = row[8]
                transaction_id = row[9]
                merchant_id = row[10]
                remarks = row[11]

                # 跳过中性交易
                if income_or_expense == '/':
                    continue
                
                # 跳过已经存在的交易
                existing = Bill.query.filter_by(transaction_id=transaction_id, user_id=user.id).first()
                if existing:
                    continue
                
                bill = Bill(
                    user_id=user.id,
                    platform='支付宝',
                    transaction_time=datetime.strptime(transaction_time, "%Y-%m-%d %H:%M:%S"),
                    category=category,
                    counterparty=counterparty,
                    product=product,
                    income_or_expense=income_or_expense,
                    amount=float(amount_str),
                    payment_method=payment_method,
                    current_status=current_status,
                    transaction_id=transaction_id,
                    merchant_id=merchant_id,
                    remarks=remarks
                )
                self.db.session.add(bill)
            self.db.session.commit()
            
    def show_tables(self):
        with self.app.app_context():
            users = User.query.all()
            bills = Bill.query.all()
            print("Users:")
            for user in users:
                print(user)
            print("\nBills:")
            for bill in bills:
                print(bill)

    def get_bill_table_data(self, user_id, start_date=None, end_date=None):
        """
        查询账单明细，返回适合表格渲染的 data 字典
        """
        query = Bill.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        bills = query.order_by(Bill.transaction_time.desc()).all()

        data = {}
        for idx, bill in enumerate(bills, 1):
            data[idx] = [
                idx,  # 序号
                bill.platform,
                bill.transaction_time.strftime("%Y-%m-%d %H:%M:%S") if bill.transaction_time else "",
                bill.category or "",
                bill.product or "",
                bill.counterparty or "",
                bill.income_or_expense or "",
                bill.amount,
                bill.payment_method or "",
                bill.current_status or ""
            ]
        return data
    
    def get_expend_classification_pie_data(self, user_id, start_date=None, end_date=None):
        """
        获取支出分类饼图数据
        """
        query = Bill.query.filter_by(user_id=user_id, income_or_expense='支出')
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        
        results = query.with_entities(
            Bill.category,
            func.sum(Bill.amount).label('total_amount')
        ).group_by(Bill.category).all()
        
        dict = {category: total_amount for category, total_amount in results}
        data = [{"value": v, "name": k} for k, v in dict.items()]
        return data
    
    def get_last_week_expend_bar_data(self, user_id):
        today = datetime.now()
        last_week_start = today - timedelta(days=6)
        bills = self.get_bills(user_id, start_date=last_week_start, end_date=today)
        # 只统计支出
        expend_bills = [bill for bill in bills if hasattr(bill, "income_or_expense") and bill.income_or_expense == "支出"]
        # 初始化每天的金额为0，key为"MM-DD"
        date_list = [(last_week_start + timedelta(days=i)).strftime("%m-%d") for i in range(7)]
        date_amount = {d: 0.0 for d in date_list}
        for bill in expend_bills:
            day = bill.transaction_time.strftime("%m-%d")
            if day in date_amount:
                date_amount[day] += bill.amount
        dates = list(date_amount.keys())
        counts = list(date_amount.values())
        return {"date": dates, "counts": counts}

    def get_highest_expend(self, user_id, start_date=None, end_date=None):
        """
        获取最高支出数值（保留3位小数，字符串类型）
        """
        query = Bill.query.filter_by(user_id=user_id, income_or_expense='支出')
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        
        result = query.order_by(Bill.amount.desc()).first()
        if result:
            return f"{result.amount:.3f}"
        else:
            return "0.000"
    def get_highest_income(self, user_id, start_date=None, end_date=None):
        """
        获取最高收入数值（保留3位小数，字符串类型）
        """
        query = Bill.query.filter_by(user_id=user_id, income_or_expense='收入')
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        
        result = query.order_by(Bill.amount.desc()).first()
        if result:
            return f"{result.amount:.3f}"
        else:
            return "0.000"
        
    def get_total_expend(self, user_id, start_date=None, end_date=None):
        """
        获取总支出，保留三位小数，返回字符串
        """
        query = Bill.query.filter_by(user_id=user_id, income_or_expense='支出')
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        
        total = query.with_entities(func.sum(Bill.amount)).scalar() or 0
        return f"{total:.3f}"
    
    def get_total_income(self, user_id, start_date=None, end_date=None):
        """
        获取总收入
        """
        query = Bill.query.filter_by(user_id=user_id, income_or_expense='收入')
        if start_date:
            query = query.filter(Bill.transaction_time >= start_date)
        if end_date:
            query = query.filter(Bill.transaction_time <= end_date)
        
        total = query.with_entities(func.sum(Bill.amount)).scalar() or 0
        return f"{total:.3f}"
                
        