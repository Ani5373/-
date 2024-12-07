from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import re

app = Flask(__name__)


# 数据库连接配置
db_config = {
    'user': 'root',
    'password': '20040406lihao',
    'host': 'localhost',
    'database': 'bda'
}

@app.route('/')
def home():
    return redirect(url_for('admin_login'))

# 管理员登录页面
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证密码格式
        if not (8 <= len(password) <= 15) or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            return "密码必须为8到15位，并且包含字母和数字"
        
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 验证管理员
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = TRUE", (username, password))
        admin = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if admin:
            return redirect(url_for('manage_students'))
        else:
            return "管理员用户名或密码错误"
    
    return render_template('admin_login.html')

# 学生管理页面
@app.route('/manage_students', methods=['GET', 'POST'])
def manage_students():
    # 连接数据库
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        action = request.form['action']
        student_id = request.form.get('id')
        name = request.form.get('name')
        enrollment_date = request.form.get('enrollment_date')
        student_number = request.form.get('student_number')
        grade = request.form.get('grade')
        
        if action == 'add':
            # 查询当前最大ID
            cursor.execute("SELECT MAX(id) AS max_id FROM students")
            result = cursor.fetchone()
            max_id = result['max_id'] if result['max_id'] is not None else 0
            new_id = max_id + 1
            
            cursor.execute("INSERT INTO students (id, name, enrollment_date, student_number, grade) VALUES (%s, %s, %s, %s, %s)", (new_id, name, enrollment_date, student_number, grade))
        
        elif action == 'update' and student_id:
            cursor.execute("UPDATE students SET name = %s, enrollment_date = %s, student_number = %s, grade = %s WHERE id = %s", (name, enrollment_date, student_number, grade, student_id))
        
        elif action == 'delete' and student_id:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            # 重新编号
            cursor.execute("SET @count = 0")
            cursor.execute("UPDATE students SET id = @count:= @count + 1")
        
        conn.commit()
    
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    query = f"SELECT * FROM students ORDER BY {sort_by} {order}"
    cursor.execute(query)
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('manage_students.html', students=students)

if __name__ == '__main__':
    app.run(debug=True)