import os
from datetime import datetime

from flask import Flask, request, jsonify,render_template,redirect, url_for,session

from models.data import db
from models.db import BillDataBase

app = Flask(__name__)

app.secret_key = 'your_secret_key'  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 建立数据库路径，确保目录存在
DB_PATH = os.path.join(BASE_DIR, 'data', 'visData.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 初始化数据库
db.init_app(app)
billdatabase = BillDataBase(app, db)

def get_pie_data():
    """
    获取用户的支出分类饼图数据
    """
    user_id = session.get('user_id')
    data = billdatabase.get_expend_classification_pie_data(user_id)
    return data
def get_username():
    """
    获取当前登录用户的用户名
    """
    user = billdatabase.get_user(session['user_id'])
    return user.username if user else ""


# 缓存用户数据 （登录成功后与上传文件后需要刷新)
def refresh_user_data(user_id):
    # 查询数据库
    total_expend = billdatabase.get_total_expend(user_id)
    total_income = billdatabase.get_total_income(user_id)
    m_expend = billdatabase.get_highest_expend(user_id)
    m_income = billdatabase.get_highest_income(user_id)
    pie_data = get_pie_data()
    # 存到 session
    session['total_expend'] = total_expend
    session['total_income'] = total_income
    session['m_expend'] = m_expend
    session['m_income'] = m_income
    session['pie_data'] = pie_data



# 首页路由
@app.route('/')
def index():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = billdatabase.get_user(session['user_id'])
    if not user:
        # 如果用户不存在，重定向到登录页
        return redirect(url_for('login'))
    else:
        # 如果已登录，渲染主页
        # TODO 首页dashboard渲染


        
        return render_template('index.html',
            username=get_username(),
            total_expend=session.get('total_expend', 0),
            total_income=session.get('total_income', 0),
            m_expend=session.get('m_expend', 0),
            m_income=session.get('m_income', 0),
            pie_data=session.get('pie_data', [])
        )

# 上传数据文件
@app.route('/upload', methods=['POST'])
def upload():
    message = '文件上传成功'
    message_type = 'success'
    if 'file' not in request.files:
        message = '请求中没有文件部分'
    file = request.files['file']
    if file.filename == '':
        message = '没有选择文件'
    # 检查文件类型
    if not file.filename.endswith('.csv'):
        message = '只支持上传CSV文件'
        
    if file:
        if message != '文件上传成功':
            message_type = 'error'
        else:
            message_type = 'success'
            # 保存文件到指定目录
            file_path = os.path.join(BASE_DIR, 'uploads', file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            billdatabase.save_bill(file_path, session['user_id'])
            
            # 刷新数据
            refresh_user_data(session['user_id'])
            
    return render_template('index.html',message=message, message_type=message_type,
        username=get_username(),
        total_expend=session.get('total_expend', 0),
        total_income=session.get('total_income', 0),
        m_expend=session.get('m_expend', 0),
        m_income=session.get('m_income', 0),
        pie_data=session.get('pie_data', [])
    )



# 账单明细
@app.route('/details', methods=['GET'])
def details():
    user = billdatabase.get_user(session['user_id'])
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    data = billdatabase.get_bill_table_data(user.id,start_date=start_date, end_date=end_date)
    page = int(request.args.get('page', 1))
    all_index = list(data.keys())
    total = len(all_index)
    per_page = 20
    # 分页
    index_list = all_index[(page - 1) * per_page: page * per_page]
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page * per_page < len(all_index) else None

    return render_template('details.html',data=data,index_list=index_list,total=total,
                           page=page,prev_page=prev_page,next_page=next_page,username=user.username)
    

# 用户登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 提取用户名
        user = billdatabase.get_user(username)
        if user:
           # 如果该用户名存在，则检查密码 
            if user.password == password:
                session['user_id'] = user.id
                refresh_user_data(user.id)  # 刷新用户数据
                return redirect(url_for('index'))
            else:
                # 密码错误提示
                return render_template('login.html', message="密码错误，请重试", username=username)
        else:
            # 如果用户不存在，则添加新用户
            user = billdatabase.add_user(username, password)
            if not user:
                # 用户已存在提示
                return render_template('login.html', message="用户名已存在，请选择其他用户名", username=username)
            else:
                session['user_id'] = user.id
                return render_template('login.html', message=f"新用户 {username} 已创建，请重新登录")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # 清除登录状态
    return redirect(url_for('login'))  # 跳转回登录页

if __name__ == '__main__':
    app.run(debug=True)