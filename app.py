from flask import Flask, render_template, request, url_for, session, redirect, flash, make_response
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = '123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flasktest'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if 'admlogin' in request.form:
            amail = request.form['amail']
            apass = request.form['apass']
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM ADMIN WHERE AMAIL=%s AND APASS=%s", [amail, apass])
                rslt = cur.fetchone()
                if rslt:
                    session["aname"] = rslt["aname"]
                    session["amail"] = rslt["amail"]
                    session["apass"] = rslt["apass"]
                    return redirect(url_for('adminhome'))
                else:
                    flash("Invalid email or password", "danger")
                    return render_template("index.html")
            except Exception as e:
                return f"Error: {e}"
            finally:
                cur.close()

        elif 'slogin' in request.form:
            semail = request.form['semail']
            spass = request.form['spass']
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM STUDENT WHERE SEMAIL=%s AND SPASS=%s", [semail, spass])
                rslt = cur.fetchone()
                if rslt:
                    session["sname"] = rslt["sname"]
                    session["semail"] = rslt["semail"]
                    session["spass"] = rslt["spass"]
                    return redirect(url_for('studenthome'))
                else:
                    flash("Invalid email or password", "danger")
                    return render_template("index.html")
            except Exception as e:
                return f"Error: {e}"
            finally:
                cur.close()
        elif 'regn' in request.form:
            if request.method=="POST":
                sname = request.form['sname']
                sage = request.form['sage']
                semail = request.form['semail']
                spass = request.form['spass']
                smobile = request.form['smobile']
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO STUDENT(SNAME,SAGE,SEMAIL,SPASS,SMOBILE) VALUES (%s,%s,%s,%s,%s)",
                            [sname, sage, semail, spass, smobile])
                flash("Student registered successfully", "success")
                mysql.connection.commit()
            return render_template("index.html")
        elif 'admregn' in request.form:
            if request.method=="POST":
                aname = request.form['aname']
                amail = request.form['amail']
                apass = request.form['apass']
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO ADMIN(ANAME,AMAIL,APASS) VALUES (%s,%s,%s)",
                            [aname, amail, apass])
                flash("Admin registered successfully", "success")
                mysql.connection.commit()
            return render_template("index.html")

    return render_template("index.html")

@app.route("/adminhome")
def adminhome():
    if 'amail' not in session:
        return redirect(url_for('index'))  # Redirect if not logged in

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM ADMIN WHERE AMAIL=%s", [session['amail']])
        admin = cur.fetchone()
        cur.close()
        if admin:
            return render_template("adminhome.html", admin=admin)
        else:
            flash('Admin not found.', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while fetching admin details.', 'danger')
        return redirect(url_for('index'))


@app.route("/add_event", methods=['POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        evntdate = request.form['evntdate']
        location=request.form['location']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO EVENTS(TITLE,DESCRIPTION,EVNTDATE,LOCATION) VALUES (%s,%s,%s,%s)",
                    [title, description,evntdate, location])
        mysql.connection.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('adminhome'))

    return redirect(url_for('adminhome'))


@app.route("/studenthome")
def studenthome():
    # Fetch upcoming events
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM EVENTS ORDER BY EVNTDATE")
    events = cur.fetchall()
    cur.close()
    print(events)
    return render_template("studenthome.html", events=events)


@app.route("/studentsprofile")
def studprofile():
    if 'semail' not in session:
        return redirect(url_for('index'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM STUDENT WHERE SEMAIL=%s", [session['semail']])
        student = cur.fetchone()
        return render_template("profile.html", student=student)

    except Exception as e:
        return f"Error: {e}"

@app.route("/updatestuddtl",methods=['POST'])
def studupdate():
    if request.method == 'POST':
        srollnum = request.form['srollnum']
        sname = request.form['sname']
        sage = request.form['sage']
        semail = request.form['semail']
        smobile = request.form['smobile']
        try:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE STUDENT SET SNAME=%s, SAGE=%s, SEMAIL=%s, SMOBILE=%s WHERE SROLLNUM=%s",
                        [sname, sage, semail, smobile, srollnum])
            mysql.connection.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            print(f"Error: {e}")
            flash('Failed to update profile. Please try again.', 'danger')
        finally:
            cur.close()

        return redirect(url_for('studprofile'))
    return render_template("profile.html")


@app.route("/studentslist")
def studlist():
    if 'amail' not in session:
        return redirect(url_for('index'))  # Redirect if not logged in

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM STUDENT")
        studentslist = cur.fetchall()
        cur.close()

        return render_template("studentlist.html", studentslist=studentslist)
    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while fetching student details.', 'danger')
        return redirect(url_for('adminhome'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


# if __name__ == "__main__":
#     app.run(debug=True)
