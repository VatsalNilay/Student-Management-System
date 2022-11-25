from flask import redirect
from flask import Flask
from flask import render_template
from flask import request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"    
db = SQLAlchemy()
db.init_app(app)
# app.app_context().push()

class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"))
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"))

    


# ---------------Create--------------------------
@app.route("/student/create",methods = ["GET","POST"])
def create_student():
    if request.method == "GET":
        return render_template("create_student.html")
    if request.method == "POST":
        roll_num = request.form.get("roll")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        courses = request.form.getlist("courses")
        student = Student.query.all()
        for i in student:
            if roll_num == i.roll_number:
                return render_template("already_exist.html")

        # last_s_no = student[-1].student_id

        temp = Student()
        temp.roll_number = roll_num
        temp.first_name = f_name
        temp.last_name = l_name
        db.session.add(temp)
        db.session.commit()

        if courses != []:
            mapp = {"course_1":1, "course_2":2,"course_3":3,"course_4":4}
            for i in courses:
                temp2 = Enrollments()
                temp2.estudent_id = temp.student_id
                temp2.ecourse_id = mapp[i]
                db.session.add(temp2)
                db.session.commit()

        return redirect("/")
        # return redirect(url_for("home.html"))



#-------------------Read-------------------------
@app.route("/", methods = ["GET","POST"])
def landing_page():
    students = Student.query.all()
    return render_template("home.html",student = students)

@app.route("/student/<int:student_id>") 
def student_details(student_id):
    req_student = Student.query.filter_by(student_id = student_id ).first()
    req_enrollments = Enrollments.query.filter_by(estudent_id = student_id).all()
    c_id = []
    for i in req_enrollments:
        c_id.append(i.ecourse_id)
    req_courses = Course.query.filter(Course.course_id.in_(c_id)).all()
    return render_template("details.html", stu = req_student, courses = req_courses)



#----------------------Update---------------------------
@app.route("/student/<int:student_id>/update",methods = ["GET", "POST"])
def update_student(student_id):

    if request.method == "GET":
        stu = Student.query.get(student_id)
        cour = Enrollments.query.filter_by(estudent_id = student_id).all()
        c_id = []
        mapp = {1:"course_1", 2:"course_2",3:"course_3",4:"course_4"}
        for i in cour:
            c_id.append(mapp[i.ecourse_id])
    
        return render_template("update_form.html",stu = stu, c_id = c_id)

    if request.method == "POST":

        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        courses = request.form.getlist("courses")
        mapp = {"course_1":1, "course_2":2,"course_3":3,"course_4":4}
        c_id = []
        for i in courses:
            c_id.append(mapp[i])

        stu = Student.query.get(student_id)
        enroll = Enrollments.query.filter_by(estudent_id = student_id).all()

        for i in enroll:  #deleting unselected course
            if i.ecourse_id not in c_id:
                db.session.delete(i)
                db.session.commit()
        
        enroll = Enrollments.query.filter_by(estudent_id = student_id).all()
        tmp = []
        for i in enroll:
            tmp.append(i.ecourse_id)

        for i in c_id:    #adding new course
            if i not in tmp:
                temp = Enrollments()
                temp.ecourse_id = i
                temp.estudent_id = student_id
                db.session.add(temp)
                db.session.commit()

        stu.first_name = f_name
        stu.last_name = l_name
        db.session.commit()

        return redirect("/")


#----------------------Delete---------------------------

@app.route("/student/<int:student_id>/delete")
def delete_student(student_id):
    enrolls = Enrollments.query.filter_by(estudent_id = student_id).all()

    for i in enrolls:
        db.session.delete(i)
        db.session.commit()
    
    stu = Student.query.get(student_id)

    db.session.delete(stu)
    db.session.commit()
    
    return redirect("/")




#-------------------------Main----------------------------

if __name__ == "__main__":
    app.run()
