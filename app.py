from flask import Flask,flash,render_template, url_for ,request,session,redirect,Response,jsonify 
from flask_mysqldb import MySQL
from datetime import timedelta 
import datetime as dt
from password_strength import PasswordPolicy,PasswordStats
import json
import pandas as pd
from sklearn.tree import DecisionTreeClassifier


app=Flask(__name__)
mysql=MySQL(app)
app.config['MYSQL_HOST']='localhost'

app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='password'
app.config['MYSQL_DB']='myflaskapp'
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(minutes=30)
app.config['SECRET_KEY'] = "abc/djiejdei"  


policy = PasswordPolicy.from_names(
    length=8,  
    uppercase=1,  
    numbers=1,  
    strength=0.54 
)
datacsv = pd.read_csv("Electrode Dataset.csv")
datacsv2 = pd.read_csv("Prescription Data.csv") 

datacsv['Disease'].replace(['Depression','schizophrenia','Parkinson disease','Stroke','Aphasia','Dystonia','ataxia','Dysphagia'], [0,1,2,3,4,5,6,7], inplace=True)
datacsv2['Disease'].replace(['Depression','Schizophrenia','Parkinson\'s Disease','Stroke','Aphasia','Dystonia','Ataxia','Dysphagia'], [0,1,2,3,4,5,6,7], inplace=True)
# print(datacsv2)

datacsv.drop('Unnamed: 5',axis=1,inplace=True)
datacsv2.drop('Unnamed: 4',axis=1,inplace=True)
# print(datacsv2)

datacsv2 = datacsv2.astype({'Voltage':str,'Time Duration':str,'No. of Sessions':str})

# print(datacsv.info())
# print(datacsv2.info())

X = datacsv[['Disease']]
y = datacsv.drop('Disease', axis=1)
# print(y)

X2 = datacsv2[['Disease']]
y2 = datacsv2.drop('Disease', axis=1)


DT = DecisionTreeClassifier()
DT.fit(X,y)

DT2 = DecisionTreeClassifier()
DT2.fit(X2,y2)

def decode(passEncrypted):
    decodedPass = []
    for i in range(len(passEncrypted)):
        decodePass = chr(ord(passEncrypted[i]) + len(passEncrypted))
        decodedPass.append(decodePass)
    passDecoded = "".join(decodedPass)
    print(passDecoded)
    return passDecoded


def encode(save_acc_pass):
    encodedPass = []
    for i in range(len(save_acc_pass)):
        encodePass = chr(ord(save_acc_pass[i]) - len(save_acc_pass))
        encodedPass.append(encodePass)
    passEncrypted = "".join(encodedPass)
    return passEncrypted


@app.route('/')
def home():
    return render_template('view/home.html')


@app.route('/doctorhome')
def doctorhome():
    return render_template('view/doctorhome.html')


@app.route('/adminhome')
def adminhome():
    return render_template('view/adminhome.html')

@app.route('/showDoctor')
def showDoctor():
    if "adminemail" in session:
        cur =mysql.connection.cursor()
        cur.execute("SELECT S_No,Name,Speacialization,Degree,ContactNumber,Email,DOB,Gender,Country,City,Address from myhospitaldoctor ")
        mysql.connection.commit()
        doctors=cur.fetchall()
        cur.close()    
        return render_template('view/showDoctors.html',tup=doctors)
    else:
        flash("Admin must be login to access this page")
        return redirect(url_for('adminlogin'))
        
@app.route('/showPatient')
def showDoctorPatient():
    
    if 'doctoremail' in session:
        cur =mysql.connection.cursor()
        cur.execute("SELECT * FROM hospitalPatients WHERE docId=%s ",(session['docId'],))
        mysql.connection.commit()
        patients=cur.fetchall()
        cur.close()

        return render_template('view/showPatient.html',tup=patients)
    else:
        flash("Doctor must be login to access this page")
        return redirect(url_for('adminlogin'))


@app.route('/electrodes/<string:val>', methods=['POST'])
def electrodes(val):
    data = json.loads(val)
    print(data)
    disease = data['disease']
    patientId = data['mr_no']
    # print(disease)

    if disease == 'Depression':
        dis_val = 0
    elif disease == 'Schizophrenia':
        dis_val = 1
    elif disease == 'Parkinson Disease':
        dis_val = 2
    elif disease == 'Stroke':
        dis_val = 3 
    elif disease == 'Aphasia':
        dis_val = 4
    elif disease == 'Dystonia':
        dis_val = 5
    elif disease == 'Ataxia':
        dis_val = 6
    elif disease == 'Dysphagia':
        dis_val = 7
    
    pred = DT.predict([[dis_val]])
    pred2 = DT2.predict([[dis_val]])
    # print("Prediction2: "+str(pred2))
    patient_electrodes = ', '.join(str(item) for innerlist in pred for item in innerlist)
    procedure_data = [str(item) for innerlist in pred2 for item in innerlist]
    print(procedure_data)

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from patientElectrodes where patientId=%s",(patientId, ))
        patients = cur.fetchall()
        cur.close()
        print(patients)
        
        if patients == ():
            try:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO patientElectrodes VALUES (%s, %s)", (patientId, patient_electrodes))
                mysql.connection.commit()
                cur.close()
            except:
                print("error while inserting")
    except:
        print("error while selecting")

    return json.dumps({'electrode':patient_electrodes, 'procedure_data':procedure_data })



@app.route('/showAdminPatient')
def showAdminPatient():
    
    if "adminemail" in session:
        
        cur =mysql.connection.cursor()
        cur.execute("SELECT * FROM hospitalPatients")
        mysql.connection.commit()
        patients=cur.fetchall()
        cur.close()
        listDoc = []
        for i in range(len(patients)):
            listDoc.append(patients[i][1])
        tupDoc = tuple(listDoc)
        cur =mysql.connection.cursor()
        cur.execute(f"SELECT S_No, Name FROM myhospitaldoctor")
        mysql.connection.commit()
        docNames=cur.fetchall()
        cur.close()
        finalList = []
        for i in patients:
            for j in docNames:
                if i[1] == j[0]:
                    temp = list(i)
                    temp.append(j[1])
                    finalList.append(temp)

        for i in finalList:
            i.pop(1)
        print(finalList)

        return render_template('view/showAdminPatient.html',tup=finalList)
    
    else:
        flash("Doctor must be login to access this page")
        return redirect(url_for('adminlogin'))
        

@app.route('/register',methods=['GET','POST'])
def register():
    
    if "doctoremail" in session:
    
        if request.method=='POST':
            data=request.form
        
            name=data['pname']
            email=data['email']
            parGender=data['gen']
            participantDob=str(data['pardob'])
            phoneNum=str(data['pnum'])
            parAddress=data['Paddress']
            parCountry=data['country']
            parCity=data['parCity']
            dise=data['disease']
            docId = session['docId']
            
            current_date=dt.datetime.now().strftime("%d/%m/%Y").split("/")
            year=current_date[2].split('0')[1]
            month=current_date[1]
            f = open("static/count.txt", "r")
            count=f.read();
            f.close()
            mr=str(year)+str(month)+count
            cur =mysql.connection.cursor()
            cur.execute("INSERT INTO hospitalPatients VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(mr,docId,name,email,parGender,participantDob,parAddress,parCountry,phoneNum,parCity,dise))
            mysql.connection.commit()
            cur.close()
        
            c=int(count)
            c+=1
            print(c)
            f = open("static/count.txt", "w")
            f.write(str(c))
            f.close()
            return redirect(url_for('doctorhome'))
        return render_template('add/patientReg.html')

    else:
        flash('Doctor must be login to access this page')
        return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    
    if request.method=='POST':
        data=request.form
        email=data['email']
        password=data['password']
        cur =mysql.connection.cursor()
        cur.execute("select S_No,password,speacialization from myhospitaldoctor where email=%s ",(email,))
        mysql.connection.commit()
        doctor=cur.fetchone()
        print(doctor)
        
        cur.close()
        if doctor:
            # print(doctor)
            pass_db = decode(doctor[1])

            print(pass_db, password)
            
            if pass_db==password:
                session['doctoremail']=email
                session['doctorspea']=doctor[2]
                session['docId'] = doctor[0]          
                return redirect(url_for('doctorhome'))
        
            else:
                flash('You have entered incorrect  password ')
                return redirect(url_for('login'))
        else:
            flash('You must be registered before accessing this page')
            return redirect(url_for('login'))
    return render_template('add/doctorLogin.html')


@app.route('/doctorReg',methods=['GET','POST'])
def doctorReg():
    if request.method=='POST':
        data=request.form
        name=data['pname']
        email=data['email']
        password=data['passw']
        RePassword=data['rePassword'] 
        parGender=data['gen']
        spea=data['spea']
        degree=data['degree']
        participantDob=str(data['pardob'])
        phoneNum=str(data['pnum'])
        parAddress=data['Paddress']
        parCountry=data['country']
        parCity=data['parCity']

        if password!=RePassword:
            flash('Both passwords should be same')
            return redirect(url_for('signup'))

        stats=PasswordStats(password)
        
        if(stats.strength() < 0.2):
            print(stats.strength())
            flash('Password not strong enough ! , Avoid using consecutive characters and easily guessed words ')
            return redirect(url_for('doctorReg'))
        
        password = encode(password)
        cur =mysql.connection.cursor()
        cur.execute(" INSERT INTO myhospitaldoctor(Name,Speacialization,Degree,ContactNumber,Email,Password,DOB,Gender,Country,City,Address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",(name,spea,degree,phoneNum,email,password,participantDob,parGender,parCountry,parCity,parAddress) )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('adminhome'))    
    return render_template('add/doctorReg.html')


@app.route('/adminLogin',methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        data=request.form
        email=data['email']
        password=data['password']
        cur =mysql.connection.cursor()
        cur.execute("select password from myhospitaladmin  where email=%s ",(email,))
        mysql.connection.commit()
        admin=cur.fetchone()
        print(admin)
        cur.close()
        if admin:
            if admin[0]==password:
                session['adminemail']=email
                return redirect(url_for('adminhome'))        
            else:
                flash('You have entered incorrect password ')
                return redirect(url_for('adminlogin'))
        else:
            flash('You have entered incorrect email and password for admin')
            return redirect(url_for('adminlogin'))    
    return render_template('add/adminLogin.html')

@app.route('/doctorlogout')
def dlogout():
    session.pop('doctoremail')
    return redirect(url_for('home'))

@app.route('/adminlogout')
def alogout():
    session.pop('adminemail')
    return redirect(url_for('home'))


if __name__ =='__main__':
    app.run(debug=True,port=5000)