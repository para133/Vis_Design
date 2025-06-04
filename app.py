import os

from flask import Flask, request, jsonify,render_template,redirect, url_for,session

from models import db, User, Bill


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

@app.route('/')
def index():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # 如果已登录，渲染主页
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 提取用户名
        user = User.query.filter_by(username=username).first()
        if user:
           # 如果该用户名存在，则检查密码 
            if user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('index'))
            else:
                # 密码错误提示
                return render_template('login.html', message="密码错误，请重试", username=username)
        else:
            # 如果用户不存在，则添加新用户
            if not user:
                # User是一张用户表，包含用户名和密码，new_user是新建的用户对象
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                user = new_user
                # 提示：新用户已创建
                session['user_id'] = user.id
                return render_template('login.html', message=f"新用户 {username} 已创建，请重新登录")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # 清除登录状态
    return redirect(url_for('login'))  # 跳转回登录页

if __name__ == '__main__':
    app.run(debug=True)