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


def add_serial_no(data):
    for item in data:
        item['sno'] = data.index(item)+1
    return data


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
    error = None
    if request.method == "GET":
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM hr;")
        result = data_to_dict(cur)
        return render_template('hr.html', session_user_name=username_session, hr_data=add_serial_no(result))
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
        method_type = request.args.get('method_type')
        error = None
        if method_type == 'add':
            return render_template('crud_hr.html', method_type=method_type)
        elif method_type == 'delete':
            delete_query = "DELETE FROM hr WHERE id = %s"
            select_data = (hr_id,)
            try:
                cur.execute(delete_query, select_data)
                db.commit()
            except Exception as ex:
                error = ex
            return redirect(url_for('hr', error=error))
        else:
            select_query = "SELECT * FROM hr where id=%s"
            select_data = (hr_id,)
            cur.execute(select_query, select_data)
            result = data_to_dict(cur)
            return render_template('crud_hr.html', method_type=method_type, hr_data=result[0])
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone_no = request.form['phone']
        sex = request.form['gender_type']
        salary = request.form['salary']
        error = None
        try:
            cur.execute("""
                           UPDATE hr
                           SET name=%s, email_id=%s, phone_no=%s, sex=%s, salary=%s
                           WHERE id=%s
                        """, (name, email, phone_no, sex, salary, id))
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('hr', error=error))


@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    error = None
    if request.method == "GET":
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM students;")
        result = data_to_dict(cur)
        return render_template('students.html', session_user_name=username_session, students_data=add_serial_no(result))
    if request.method == "POST":
        name = request.form['name']
        gender = request.form['gender']
        dept = request.form['dept']
        email = request.form['email']
        batch = request.form['batch']
        phone = request.form['phone']
        add_std = "INSERT INTO students (name, gender, dept, email, batch, phone) VALUES (%s, %s, %s, %s, %s ," \
                  "%s) "
        data_std = (name, gender, dept, email, batch, phone)
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
        method_type = request.args.get('method_type')
        error = None
        if method_type == 'add':
            return render_template('crud_students.html', method_type=method_type)
        elif method_type == 'delete':
            delete_query = "DELETE FROM students WHERE id = %s"
            select_data = (students_id,)
            try:
                cur.execute(delete_query, select_data)
                db.commit()
            except Exception as ex:
                error = ex
            return redirect(url_for('hr', error=error))
        else:
            select_query = "SELECT * FROM students where id=%s"
            select_data = (students_id,)
            cur.execute(select_query, select_data)
            result = data_to_dict(cur)
            print(result)
            return render_template('crud_students.html', method_type=method_type, students_data=result[0])
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        gender = request.form['gender']
        dept = request.form['dept']
        email = request.form['email']
        batch = request.form['batch']
        phone = request.form['phone']
        error = None
        try:
            cur.execute("""
                               UPDATE students
                               SET name=%s, gender=%s,dept=%s ,email=%s ,batch=%s, phone=%s,
                               WHERE id=%s
                            """, (name, gender, dept, email, batch, phone, id))
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('students', error=error))


@app.route('/trainers', methods=['GET', 'POST'])
@login_required
def trainers():
    error = None
    if request.method == 'GET':
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM trainers;")
        result = data_to_dict(cur)
        return render_template('trainers.html', session_user_name=username_session, trainer_data=add_serial_no(result))
    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['gender']
        dept = request.form['specification']
        email = request.form['email']
        phone_no = request.form['phone_no']
        add_trainer = "INSERT INTO trainers (name, gender, specification ,email, phone_no) VALUES (%s, %s, %s, %s, %s)"
        data_trainer = (name, sex, dept, email, phone_no)
        try:
            cur.execute(add_trainer, data_trainer)
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('trainer', error=error))


@app.route('/trainer', methods=['GET', 'POST'])
@login_required
def crud_trainers():
    if request.method == 'GET':
        trainer_id = request.args.get('trainer_id')
        method_type = request.args.get('method_type')
        error = None
        if method_type == 'add':
            return render_template('crud_trainers.html', method_type=method_type)
        elif method_type == 'delete':
            delete_query = "DELETE FROM trainers WHERE id = %s"
            select_data = (trainer_id,)
            try:
                cur.execute(delete_query, select_data)
                db.commit()
            except Exception as ex:
                error = ex
            return redirect(url_for('trainer', error=error))
        else:
            select_query = "SELECT * FROM trainers where id=%s"
            select_data = (trainer_id,)
            cur.execute(select_query, select_data)
            result = data_to_dict(cur)
            return render_template('crud_trainers.html', method_type=method_type, trainer_data=result[0])
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        gender = request.form['gender']
        specification = request.form['specification']
        email = request.form['email']
        phone_no = request.form['phone_no']
        error = None
        try:
            cur.execute("""
                           UPDATE trainers
                           SET name=%s, gender=%s, specification=%s, email=%s, phone_no=%s,
                           WHERE id=%s
                        """, (name, gender, specification, email, phone_no, id))
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('trainer', error=error))


@app.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    error = None
    if request.method == 'GET':
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM course;")
        result = data_to_dict(cur)
        return render_template('course.html', session_user_name=username_session, course_data=add_serial_no(result))
    if request.method == 'POST':
        coursename = request.form['coursename']
        coursedetails = request.form['coursedetails']
        add_course = "INSERT INTO course (coursename, coursedetails) VALUES (%s, %s)"
        data_course = (coursename, coursedetails)
        try:
            cur.execute(add_course, data_course)
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('course', error=error))


@app.route('/courses', methods=['GET', 'POST'])
@login_required
def crud_course():
    if request.method == 'GET':
        course_id = request.args.get('id')
        method_type = request.args.get('method_type')
        error = None
        if method_type == 'add':
            return render_template('crud_course.html', method_type=method_type)
        elif method_type == 'delete':
            delete_query = "DELETE FROM course WHERE id = %s"
            select_data = (course_id,)
            try:
                cur.execute(delete_query, select_data)
                db.commit()
            except Exception as ex:
                error = ex
            return redirect(url_for('course', error=error))
        else:
            select_query = "SELECT * FROM course where id=%s"
            select_data = (course_id,)
            cur.execute(select_query, select_data)
            result = data_to_dict(cur)
            print(result)
            return render_template('crud_course.html', method_type=method_type, trainer_data=result[0])
    if request.method == 'POST':
        id = request.form['id']
        coursename = request.form['coursename']
        coursedetails = request.form['coursedetails']
        error = None
        try:
            cur.execute("""
                           UPDATE course
                           SET coursename=%s, coursedetails=%s WHERE id=%s
                        """, (coursename, coursedetails, id))
            db.commit()
        except Exception as ex:
            error = ex
        return redirect(url_for('course', error=error))


@app.route('/fees')
@login_required
def fees():
    error = None
    if request.method == "GET":
        username_session = escape(session['username']).capitalize()
        cur.execute("SELECT * FROM course;")
        result = data_to_dict(cur)
        return render_template('fees.html', session_user_name=username_session, fees_data=add_serial_no(result))
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        db = cursor.execute("SELECT id, coursename FROM course")
        return render_template('fees.html', workers0=cursor.fetchall())


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)
