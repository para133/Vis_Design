from flask import Flask, request, jsonify,render_template,redirect, url_for,session
from models import db, User, Bill
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'visData.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 上传数据文件
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('index.html', message='请求中没有文件部分',  message_type='error')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', message='没有选择文件',  message_type='error')

    # 检查文件类型
    if not file.filename.endswith('.csv'):
        return render_template('index.html', message='只支持CSV文件',  message_type='error')

    if file:
        # 保存文件到指定目录
        file_path = os.path.join(BASE_DIR, 'uploads', file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        
        # TODO 
        # 这里可以添加文件处理逻辑，比如解析文件内容，存储到数据库等

        return render_template('index.html', message='文件上传成功', message_type='success')
    return render_template('index.html', message='文件上传失败', message_type='error')

# 首页路由
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', username=user.username)

# 用户登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            # 登录成功逻辑
            if user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('index'))
            else:
                # 密码错误提示
                return render_template('login.html', message="密码错误，请重试", username=username)
        else:
            # 如果用户不存在，则添加新用户
            if not user:
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