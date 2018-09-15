from flask import Flask, session, redirect, url_for, escape, request, render_template
import mysql.connector as mysql
from functools import wraps


app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

#######################
#   DATABASE CONFIG   #
#######################

db = mysql.connect(host="localhost", user="root", password="rootroot", database="users")
cur = db.cursor()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def data_to_dict(cursor):
    columns = cursor.description
    result = [{columns[position][0]: column for position, column in enumerate(value)} for value in cursor.fetchall()]
    return result


@app.route('/')
@login_required
def index():
    username_session = escape(session['username']).capitalize()
    return render_template('dashboard.html', session_user_name=username_session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username_form = request.form['username']
        password_form = request.form['password']
        cur.execute("SELECT COUNT(1) FROM users WHERE name = %s;", [username_form])  # CHECKS IF USERNAME EXSIST
        if cur.fetchone()[0]:
            cur.execute("SELECT pass FROM users WHERE name = %s;", [username_form])  # FETCH THE HASHED PASSWORD
            for row in cur.fetchall():
                if password_form == row[0]:
                    session['username'] = request.form['username']
                    return redirect(url_for('index'))
                else:
                    error = "Invalid Credential"
        else:
            error = "Invalid Credential"
    return render_template('login.html', error=error)


@app.route('/hr', methods=['GET', 'POST'])
@login_required
def hr():
    error= None
    if request.method == "GET":
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM hr;")
        result = data_to_dict(cur)
        return render_template('hr.html', session_user_name=username_session, hr_data=result)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_no = request.form['phone']
        sex = request.form['gender_type']
        salary = request.form['salary']
        add_hr = "INSERT INTO hr (name, email_id, phone_no, sex, salary) VALUES (%s, %s, %s, %s, %s)"
        data_hr = (name, email, phone_no, sex, salary)
        try:
            cur.execute(add_hr, data_hr)
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('hr', error=error))


@app.route('/hre', methods=['GET', 'POST'])
@login_required
def crud_hr():
    if request.method == 'GET':
        hr_id = request.args.get('hr_id')
        select_query = "SELECT * FROM hr where id=%s"
        select_data = (hr_id,)
        cur.execute(select_query, select_data)
        result = data_to_dict(cur)
        print(result)
        return render_template('crud_hr.html')


@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    if request.method == "GET":
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM students;")
        result = data_to_dict(cur)
        return render_template('students.html', session_user_name=username_session, students_data=result)
    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['gender_type']
        dept = request.form['dept']
        email = request.form['email']
        batch = request.form['batch']
        phone_no = request.form['phone']
        add_std = "INSERT INTO students (name, gender, dept, email, batch, phone) VALUES (%s, %s, %s, %s, %s ," \
                  "%s) "
        data_std = (name, sex, dept, email, batch, phone_no)
        try:
            cur.execute(add_std, data_std)
            db.commit()
        except Exception as ex:
            print(ex)
            error = ex
        return redirect(url_for('students', error=error))


@app.route('/studentse', methods=['GET', 'POST'])
@login_required
def crud_students():
    if request.method == 'GET':
        students_id = request.args.get('students_id')
        select_query = "SELECT * FROM students where id=%s"
        select_data = (students_id,)
        cur.execute(select_query, select_data)
        result = data_to_dict(cur)
        print(result)
        return render_template('crud_students.html')


@app.route('/trainers', methods=['GET', 'POST'])
@login_required
def trainers():
    username_session = escape(session['username']).capitalize()
    cur.execute("SELECT * FROM trainers;")
    result = data_to_dict(cur)
    return render_template('trainers.html', session_username_name=username_session, trainer_data=result)


@app.route('/trainerse', methods=['GET', 'POST'])
@login_required
def crud_trainers():
    if request.method == 'GET':
        trainers_id = request.args.get('trainers_id')
        select_query = "SELECT * FROM trainers where id=%s"
        select_data = (trainers_id,)
        cur.execute(select_query, select_data)
        result = data_to_dict(cur)
        print(result)
        return render_template('crud_trainers.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)
