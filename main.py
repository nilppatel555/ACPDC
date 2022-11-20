import os
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from ML.app import OCR
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'Marksheet'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tiger@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.secret_key="hi"

db = SQLAlchemy(app)
# @app.route('/')

@app.route('/profile')
def Profile():
    return render_template('Profile.html')
@app.route('/Contact')
def Contact():
    return render_template('Contact.html')
@app.route('/Qualification')
def Qualification():
    return render_template('Qualification.html')

@app.route('/marksheet',methods=['GET','POST'])
def marksheet():
    # english_marks,maths_marks,science_marks = OCR("samples\\8.jpeg")
    e_content="passed"
    m_content="passed"
    s_content="passed"
    if request.method == "POST":
        docnum = request.form["docnum"]
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        f = request.files['file']
        filename = secure_filename(f.filename)
        filename = docnum+'_10_marksheet.jpg'
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        english_marks,maths_marks,science_marks,name,seat = OCR("Marksheet\\"+docnum+"_10_marksheet.jpg")
        if english_marks<33:
            e_content="failed"
        if maths_marks<33:
            m_content="failed"
        if science_marks<33:
            s_content="failed"
 
        #return "ENGLISH:"+name +" "+"MATHEMATICS:"+seat +" "+"SCIENCE:"+str(science_marks)+str(maths_marks)+str(english_marks)
        return render_template("DiplayMarksheet.html",e_status=e_content,m_status=m_content,s_status=s_content,m_marks=maths_marks,s_marks=science_marks,e_marks=english_marks,name=name,seat=seat) #"ENGLISH:"+str(english_marks) +" "+"MATHEMATICS:"+str(maths_marks) +" "+"SCIENCE:"+str(science_marks)
    return render_template("Marksheet.html")
    #return "ENGLISH:"+name +" "+"MATHEMATICS:"+seat +" "+"SCIENCE:"+str(science_marks)+str(maths_marks)+str(english_marks)
@app.route('/Upload')
def upload():
    return render_template('Upload.html')

if __name__=='__main__': 
    app.run(debug = True)
