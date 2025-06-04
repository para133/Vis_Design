from flask import Flask, request, jsonify,render_template
# from flask import SQLAlchemy



app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bill.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    f = request.files['file']
    if f:
        file_path = app.config["UPLOAD_FOLDER"] + f.filename
        f.save(file_path)
        # TODO: 解析与入库
        
        return '上传成功'
    return '上传失败'

if __name__ == '__main__':
    app.run(debug=True)