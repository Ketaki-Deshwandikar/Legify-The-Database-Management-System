from flask import Flask, make_response,render_template,Response,session,request,redirect,url_for,flash
import pymysql
import mysql.connector,hashlib
import matplotlib.pyplot as plt
import numpy as np
import re
import MySQLdb
from fpdf import FPDF

from flask import jsonify
from datetime import datetime
from datetime import timedelta


mydb = mysql.connector.connect(
  host='localhost',
  user='root',
  password='Kddevendra06',
  database = 'lawyer'
)
mycursor = mydb.cursor(buffered=True)

app = Flask(__name__)




@app.route("/",methods = ['POST', 'GET'])
@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method=='POST' :
        query = """SELECT * FROM login WHERE username = '%s'""" %(request.form['username'])
        mycursor.execute(query)
        res = mycursor.fetchall()
        if mycursor.rowcount == 0:
            return render_template('login.html',msg="Login Failed.")
        if request.form['password'] != res[0][1]:
            return render_template('login.html',msg="Login failed")
        else:
            session['login'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            session['isAdmin'] = (request.form['username']=='admin')
            return render_template("first.html",msg="Login Successful")
    return render_template('login.html')

@app.route("/first", methods=['POST','GET'])
def first():
    return render_template('first.html')
@app.route("/home",methods = ['POST','GET'])
def home():
    if not session.get('login'):
        return render_template('first.html'),401
    else:
        if session.get('isAdmin') :
            return render_template('home.html',username=session.get('username'))
        else :
            return render_template('home.html',username=session.get('username'))


@app.route("/add_client_page", methods=['POST','GET'])
def add_client_page():

    cid=request.form['ClientID']
    name=request.form.get("Name")
    add=request.form.get("Address")
    role=request.form.get("ClientRole")
    phone=request.form.get("Phone")
    email=request.form.get("Email")

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(not re.fullmatch(regex, email)):
        return render_template('update.html',msg="Invalid email")
        
    if(int(phone)<1000000000 or int(phone)>9999999999):
        return render_template('update.html',msg="Invalid phone number")

    qry1 = "INSERT INTO Client (ClientID, name, ClientRole, address) values (%s,%s,%s,%s)"
    val1= (cid, name, role, add)
    
    qry2 = "INSERT INTO Contact (ClientID, phone, email) values (%s,%s,%s)"
    val2 = (cid, phone, email)
    
    mycursor = mydb.cursor()

    success = True
    error = False
    msg="Successfully added."
    
    try:
        mycursor.execute(qry1, val1)
        mycursor.execute(qry2, val2)
        
        print( "record inserted.")
    except:
        print("Error : Client not Inserted")
        error = True
        success = False
        msg="ERROR"
        
    mydb.commit()
    return render_template('home.html',msg=msg)



@app.route("/add_contact",methods=['POST','GET'])
def add_contact():
    cid=request.form['ClientID']
    phone=request.form.get("Phone")
    email=request.form.get("Email")

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(not re.fullmatch(regex, email)):
        return render_template('update.html',msg="Invalid email")
        
    if(int(phone)<1000000000 or int(phone)>9999999999):
        return render_template('update.html',msg="Invalid phone number")

    qry2 = "INSERT INTO Contact (ClientID, phone, email) values (%s,%s,%s)"
    val2 = (cid, phone, email)
    
    mycursor = mydb.cursor()

    success = True
    error = False
    msg="Successfully added."
    
    try:
        mycursor.execute(qry2, val2)
        
        print( "record inserted.")
    except:
        print("Error : Client not Inserted")
        error = True
        success = False
        msg="ERROR"
        
    mydb.commit()
    return render_template('home.html',msg=msg)

@app.route("/index", methods=["POST","GET"])
def index():
    return render_template('index.html')
@app.route("/ajaxlivesearch",methods=["POST","GET"])
def ajaxlivesearch():
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from Client "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:
            query = """
        SELECT DISTINCT Client.*, Contact.phone, Contact.email 
        FROM Client 
        LEFT JOIN Contact ON Client.ClientID = Contact.ClientID 
        WHERE Client.ClientID IN (
            SELECT DISTINCT ClientID FROM Contact
            WHERE phone LIKE '%{search_word}%' OR email LIKE '%{search_word}%'
        )
        OR Client.name LIKE '%{search_word}%' 
        OR Client.address LIKE '%{search_word}%' 
        OR Client.clientRole LIKE '%{search_word}%' 
        OR Client.ClientID LIKE '%{search_word}%'
    
    """.format(search_word=search_word)

            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('response.html', employee=employee, numrows=numrows)})

@app.route("/get_update_page")
def get_update_page():
    return render_template("update.html")
@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        add= request.form['add']
        role= request.form['role']
        email = request.form['email']
        phone = request.form['phone']

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(not re.fullmatch(regex, email)):
            return render_template('update.html',msg="Invalid email")
        
        if(int(phone)<1000000000 or int(phone)>9999999999):
            return render_template('update.html',msg="Invalid phone number")
        
        query = "INSERT INTO updated_client values (%s,%s,%s,%s,%s,%s)"
        value= (id_data, name, add, role, phone, email)
        qry=" UPDATE Client SET name=%s, address=%s, ClientRole=%s WHERE ClientID=%s"
        val=(name, add, role, id_data)
        contact_query = "INSERT INTO Contact values (%s,%s,%s)"
        contact_value = (id_data, phone, email)
        
        success = True
        error = False
        msg="Done"
        
        try:
            mycursor.execute(query, value)
            mycursor.execute(qry, val)
            mycursor.execute(contact_query, contact_value)
        except:
            print("Error : Client not updated")
            error = True
            success = False
            msg="Failed"
        
        mydb.commit()
        return render_template("update.html", msg=msg)

    
@app.route("/get_delete_page",methods=['POST','GET'])
def get_delete_page():
    return render_template("delete_client.html")

@app.route('/delete_client',methods=['POST','GET'])
def delete_client():

    if request.method == 'POST':
        cid = request.form.get("cid")
        table='Notes'
        qry1="SET FOREIGN_KEY_CHECKS = 0"
        qry="DELETE FROM Client WHERE ClientID=%s"
        qry2="SET FOREIGN_KEY_CHECKS = 1"
        
        val=(cid,)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            #mycursor.execute(qry1)
            mycursor.execute(qry,val)
            #mycursor.execute(qry2)
        except:
            print("Error : Note not updated")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("delete_client.html",msg=msg)
    
@app.route("/delete_contact",methods=['POST','GET'])
def delete_contact():
    if request.method == 'POST':
        cid = request.form.get("cid")
        phone=request.form.get("phone")
        email=request.form.get("email")
        table='Notes'
        qry="DELETE FROM contact WHERE ClientID=%s and phone=%s and email=%s"
        val=(cid,phone,email)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(qry,val)
        except:
            print("Error : Note not updated")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("delete_client.html",msg=msg)
    
@app.route("/notes",methods=['POST','GET'])
def notes():
    return render_template("add_note.html")

@app.route("/add_note", methods=['POST','GET'])
def add_note():

    note=request.form['note'] 
    urgency=request.form['urgency']
    qry = "INSERT INTO Notes(remark,urgency) values(%s,%s)"
    val=(note,urgency)
    #val= (caseno, casetype, cid, courtn,df,dc)
    
    mycursor = mydb.cursor()

    #mycursor.execute(qry, val)

    #mydb.commit()

    #print(mycursor.rowcount, "record inserted.")
    print(qry)
    print(val)
    success = True
    error = False
    msg="Successfully added."
    try:
        mycursor.execute(qry,val)
    except:
        print("Error : Note not Inserted")
        error = True
        success = False
        msg="ERROR"
    mydb.commit()
    print(error)
    print(success)
    return render_template('add_note.html',msg=msg)

@app.route("/get_search_note_page",methods=['POST','GET'])
def get_search_note_page():
    return render_template("search_note.html")


@app.route("/ajaxlivesearch_note",methods=["POST","GET"])
def ajaxlivesearch_note():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from Notes "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from Notes WHERE noteID LIKE '%{}%'  OR created_on LIKE '%{}%'  OR remark LIKE '%{}%'  OR urgency LIKE '%{}%' ".format(search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('response_note.html', employee=employee, numrows=numrows)})

@app.route("/get_update_note_page",methods=['POST','GET'])
def get_update_note_page():
    return render_template("update_note.html")

@app.route('/update_note',methods=['POST','GET'])
def update_note():

    if request.method == 'POST':
        nid = request.form['nid']
        remark = request.form['remark']
        urgency= request.form['urg']
        
        qry=" UPDATE Notes SET remark=%s, urgency=%s WHERE noteID=%s "
        val=(remark,urgency,nid)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(qry,val)
        except:
            print("Error : Note not updated")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("update_note.html",msg=msg)
    
@app.route("/get_delete_note_page",methods=['POST','GET'])
def get_delete_note_page():
    return render_template("delete_note.html")

@app.route('/delete_note',methods=['POST','GET'])
def delete_note():

    if request.method == 'POST':
        nid = request.form.get("nid")
        table='Notes'
        qry="DELETE FROM Notes WHERE noteID=%s and noteID=%s"
        val=(nid,nid)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(qry,val)
        except:
            print("Error : Note not updated")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("delete_note.html",msg=msg)
    
@app.route("/get_recover_note_page",methods=['POST','GET'])
def get_recover_note_page():
    return render_template("recover_note.html")

@app.route('/recover_note',methods=['POST','GET'])
def recover_note():
    if request.method == 'POST':
        nid = request.form['nid']
        print(nid)
        if nid == '':
            query = "SELECT * from Client "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "DELETE from deleted_Notes WHERE noteID = '{}'  ".format(nid)
            try:
                mycursor.execute(query)
                msg="Recovered successfully."
            except:
                print("ERROR")
                msg="Failed to recover."
        mydb.commit()
        return render_template("delete_note.html",msg=msg)

@app.route("/evidence",methods=['POST','GET'])
def evidence():
    return render_template("add_evidence.html")

@app.route("/add_evidence", methods=['POST','GET'])
def add_evidence():

    caseno=request.form['CaseID']
    casetype=request.form.get("casetype")
    cid=request.form.get("cid")
    evid=request.form.get("evid")
    pos=request.form.get("pos")
    type=request.form.get("type")
    remark=request.form.get("remark")
    
    val=(cid,caseno, casetype, pos, type,remark,evid)
    qry = "INSERT INTO Evidence values (%s,%s,%s,%s,%s,%s,%s)"
    
    mycursor = mydb.cursor()

    #mycursor.execute(qry, val)

    #mydb.commit()

    #print(mycursor.rowcount, "record inserted.")
    print(qry)
    print(val)
    success = True
    error = False
    msg="Successfully added."
    try:
        mycursor.execute(qry,val)
    except:
        print("Error : Evidence not Inserted")
        error = True
        success = False
        msg="ERROR"
    mydb.commit()
    print(error)
    print(success)
    return render_template('add_evidence.html',msg=msg)

@app.route("/get_search_evi_page",methods=['POST','GET'])
def get_search_evi_page():
    return render_template("search_evidence.html")


@app.route("/ajaxlivesearch_evi",methods=["POST","GET"])
def ajaxlivesearch_evi():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from evi_Client "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from evi_Client WHERE caseno LIKE '%{}%'  OR casetype LIKE '%{}%'  OR ClientID LIKE '%{}%'  OR name LIKE '%{}%' OR position LIKE '%{}%' OR evidenceID LIKE '%{}%'  OR type LIKE '%{}%'  OR remark LIKE '%{}%'".format(search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('response_evidence.html', employee=employee, numrows=numrows)})

@app.route("/get_update_evi_page",methods=['POST','GET'])
def get_update_evi_page():
    return render_template("update_evidence.html")

@app.route('/update_evidence',methods=['POST','GET'])
def update_cevidence():

    if request.method == 'POST':
        caseno = request.form['caseno']
        casetype = request.form['casetype']
        cid= request.form['cid']
        type= request.form['type']
        pos = request.form['pos']
        remark = request.form['remark']
        evid = request.form['evid']
        query = "INSERT INTO updated_evidence values (%s,%s,%s,%s,%s,%s,%s)"
        value=(cid,caseno, casetype, pos, type,remark,evid)
        
        qry=" UPDATE Evidence SET type=%s,  position=%s, remark=%s WHERE ClientID=%s and caseno=%s and casetype=%s and evidenceID=%s"
        val=(type, pos,remark,cid, caseno,casetype,evid)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(query,value)
            mycursor.execute(qry,val)
        except:
            print("Error : Evidence not Updated")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("update_evidence.html",msg=msg)

@app.route("/bill",methods=['POST','GET'])
def bill():
    return render_template("bill_add.html")

@app.route("/bill_add", methods=['POST','GET'])
def bill_add():

    cid=request.form.get("ClientID")
    caseno=request.form.get("caseno")
    casetype=request.form.get("casetype")
    totalamt=request.form.get("totalamt")
    amtpaid=request.form.get("amtpaid")
    amtdue=request.form.get("amtdue")
    qry = "INSERT INTO Bill values (%s,%s,%s,%s,%s,%s)"
    val= (cid, caseno, casetype, totalamt, amtpaid, amtdue)
    
    mycursor = mydb.cursor()

    #mycursor.execute(qry, val)

    #mydb.commit()

    #print(mycursor.rowcount, "record inserted.")
    print(qry)
    print(val)
    success = True
    error = False
    msg="Successfully added."
    try:
        mycursor.execute(qry,val)
    except:
        print("Error : Client not Inserted")
        error = True
        success = False
        msg="ERROR"
    mydb.commit()
    print(error)
    print(success)
    return render_template('bill_add.html',msg=msg)

@app.route("/bill_search", methods=["POST","GET"])
def bill_search():
    return render_template('bill_search.html')
@app.route("/ajaxlivesearchbill",methods=["POST","GET"])
def ajaxlivesearchbill():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from BillClient "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from BillClient WHERE caseno LIKE '%{}%'  OR casetype LIKE '%{}%'  OR name LIKE '%{}%'  OR totalamt LIKE '%{}%' OR amtdue LIKE '%{}%' OR ClientID LIKE '%{}%' ".format(search_word,search_word,search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('responsebill.html', employee=employee, numrows=numrows)})

@app.route("/payment",methods=['POST','GET'])
def payment():
    return render_template("payment_add.html")

@app.route("/payment_add", methods=['POST','GET'])
def payment_add():

    cid=request.form.get("ClientID")
    caseno=request.form.get("Caseno")
    casetype=request.form.get("casetype")
    transID=request.form.get("transID")
    mode=request.form.get("mode")
    amount=request.form.get("amount")
    qry = "INSERT INTO Payment values (%s,%s,%s,%s,%s,%s)"
    val= (cid, caseno, casetype, transID, mode, amount)

    
    mycursor = mydb.cursor()

    success = True
    error = False
    msg = "Successfully added."

    try:
        mycursor.execute(qry, val)
        
        # update the Bill table with the new amtdue value
        update_query = "UPDATE Bill SET amtdue = amtdue - %s WHERE caseno = %s AND casetype = %s AND ClientID = %s"
        update_val = (amount, caseno, casetype, cid)
        mycursor.execute(update_query, update_val)

        update_query = "UPDATE Bill SET amtpaid = amtpaid + %s WHERE caseno = %s AND casetype = %s AND ClientID = %s"
        update_val = (amount, caseno, casetype, cid)
        mycursor.execute(update_query, update_val)
        
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
        
    except:
        print("Error: Payment not inserted.")
        error = True
        success = False
        msg = "ERROR"
        
    return render_template('payment_add.html', msg=msg)


@app.route("/payment_search", methods=["POST","GET"])
def payment_search():
    return render_template('payment_search.html')
@app.route("/ajaxlivesearchpayment",methods=["POST","GET"])
def ajaxlivesearchpayment():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from PaymentClient "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from PaymentClient WHERE caseno LIKE '%{}%'  OR casetype LIKE '%{}%'  OR name LIKE '%{}%'  OR transID LIKE '%{}%' OR amount LIKE '%{}%' OR ClientID LIKE '%{}%' ".format(search_word,search_word,search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('responsepayment.html', employee=employee, numrows=numrows)})

@app.route("/casestatus",methods=['POST','GET'])
def casestatus():
    return render_template("add_casestatus.html")

@app.route("/add_casestatus", methods=['POST','GET'])
def add_casestatus():

    cid=request.form.get("cid")
    caseno=request.form.get("caseno")
    casetype=request.form.get("casetype")
    prevdate=request.form.get("prevdate")
    nextdate=request.form.get("nextdate")
    currStage=request.form.get("currStage")
    nextStage=request.form.get("nextStage")
    if not prevdate:
        prevdate = None
    if not nextdate:
        nextdate= None
    val=(caseno, casetype, cid, prevdate,nextdate,currStage,nextStage)
    qry = "INSERT INTO casestatus values (%s,%s,%s,%s,%s,%s,%s)"
    
    mycursor = mydb.cursor()

    #mycursor.execute(qry, val)

    #mydb.commit()

    #print(mycursor.rowcount, "record inserted.")
    print(qry)
    print(val)
    success = True
    error = False
    msg="Successfully added."
    try:
        mycursor.execute(qry,val)
    except:
        print("Error : Client not Inserted")
        error = True
        success = False
        msg="ERROR"
    mydb.commit()
    print(error)
    print(success)
    return render_template('add_casestatus.html',msg=msg)

@app.route("/search_casestatus", methods=["POST","GET"])
def search_casestatus():
    return render_template('search_casestatus.html')
@app.route("/ajaxlivesearchcasestatus",methods=["POST","GET"])
def ajaxlivesearchcasestatus():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from clientstatus "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from clientstatus WHERE caseno LIKE '%{}%'  OR casetype LIKE '%{}%'  OR name LIKE '%{}%'  OR currStage LIKE '%{}%' OR nextStage LIKE '%{}%' OR ClientID LIKE '%{}%' OR prevdate LIKE '%{}%'  OR nextdate LIKE '%{}%' ".format(search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('responsecasestatus.html', employee=employee, numrows=numrows)})


@app.route("/get_update_pagecasestatus",methods=['POST','GET'])
def get_update_pagecasestatus():
    return render_template("update_casestatus.html")

@app.route('/update_casestatus',methods=['POST','GET'])
def update_casestatus():

    if request.method == 'POST':
        caseno = request.form['caseno']
        casetype = request.form['casetype']
        cid= request.form['cid']
        prevdate= request.form['prevdate']
        nextdate = request.form['nextdate']
        currStage = request.form['currStage']
        nextStage = request.form['nextStage']
        cquery= "SELECT currStage, nextStage FROM casestatus WHERE ClientID=%s AND caseno=%s AND casetype=%s"
        v=(cid,caseno,casetype)
        mycursor.execute(cquery,v)
        stat=mycursor.fetchall()
        for x in stat:
            for y in x:
                if y=="closed":
                    return render_template("update_case.html",msg="Case is closed.")
        value=(caseno, casetype, cid, prevdate,nextdate,currStage,nextStage)
        query = "INSERT INTO updated_casestatus values (%s,%s,%s,%s,%s,%s,%s)"
        if not prevdate:
            prevdate = None
        if not nextdate:
            nextdate= None

        qry=" UPDATE casestatus SET prevdate=%s,  nextdate=%s, currStage=%s, nextStage=%s WHERE ClientID=%s and caseno=%s and casetype=%s"
        val=(prevdate,nextdate,currStage,nextStage,cid, caseno,casetype)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(query,value)
            mycursor.execute(qry,val)
        except:
            print("Error : Evidence not Updated")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("update_casestatus.html",msg=msg)
    
@app.route("/case",methods=['POST','GET'])
def case():
    return render_template("add_case.html")
@app.route("/add_case_page", methods=['POST','GET'])
def add_case_page():

    if request.method == 'POST':
        client_id = request.form.get("cid")
        caseno = request.form.get("CaseID")
        casetype = request.form.get("casetype")
        courtname = request.form.get("court")
        datefiled = request.form.get("datef")
        dateclosed = request.form.get("datec")
        judge = request.form.get("judge")
        opp = request.form.get("opp")
        if not dateclosed:
            dateclosed = None
        qry =  "INSERT INTO Cases VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (caseno, casetype, client_id, courtname, datefiled, dateclosed, judge, opp)
        z=0
        query= "INSERT INTO Bill VALUES (%s, %s, %s,%s, %s, %s)"
        value=(client_id,caseno,casetype,z,z,z)
        query1= "INSERT INTO billablehours VALUES (%s, %s, %s, 'partner','0')"
        value1=(client_id,caseno,casetype)
        query2= "INSERT INTO billablehours VALUES (%s, %s, %s, 'associate','0')"
        value2=(client_id,caseno,casetype)
        query3= "INSERT INTO billablehours VALUES (%s, %s, %s, 'paralegal','0')"
        value3=(client_id,caseno,casetype)
        query4= "INSERT INTO billablehours VALUES (%s, %s, %s, 'PI','0')"
        value4=(client_id,caseno,casetype)
        query5= "INSERT INTO billablehours VALUES (%s, %s, %s, 'other','0')"
        value5=(client_id,caseno,casetype)
   
    
    mycursor = mydb.cursor()

    
    print(qry)
    print(val)
    success = True
    error = False
    msg="Successfully added."
    try:
        mycursor.execute(qry,val)
        mycursor.execute(query,value)
        mycursor.execute(query1,value1)
        mycursor.execute(query2,value2)
        mycursor.execute(query3,value3)
        mycursor.execute(query4,value4)
        mycursor.execute(query5,value5)
    except:
        print("Error : Case not Inserted")
        error = True
        success = False
        msg="ERROR"
    mydb.commit()
    print(error)
    print(success)
    return render_template('add_case.html',msg=msg)

@app.route("/get_search_case_page",methods=['POST','GET'])
def get_search_case_page():
    return render_template("search_case.html")


@app.route("/ajaxlivesearch_case",methods=["POST","GET"])
def ajaxlivesearch_case():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from Cases "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from Cases WHERE caseno LIKE '%{}%'  OR casetype LIKE '%{}%' OR Judge LIKE '%{}%'  OR Opposition LIKE '%{}%'  OR ClientID LIKE '%{}%'  OR courtname LIKE '%{}%' OR datefiled LIKE '%{}%' OR dateclosed LIKE '%{}%' ".format(search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('response_case.html', employee=employee, numrows=numrows)})


@app.route('/fetch_casenos')
def fetch_casenos():
    client_id = request.args.get('clientId')
    query = "SELECT caseno FROM cases WHERE ClientID = %s"
    values = (client_id,)
    mycursor.execute(query, values)
    casenos = [row[0] for row in mycursor.fetchall()]
    return jsonify(casenos)

@app.route("/get_update_case_page",methods=['POST','GET'])
def get_update_case_page():
    return render_template("update_case.html")

@app.route('/update_case',methods=['POST','GET'])
def update_case():

    if request.method == 'POST':
        caseno = request.form['caseno']
        casetype = request.form['casetype']
        cid= request.form['cid']
        courtname= request.form['courtname']
        df = request.form['datef']
        dc = request.form['datec']
        judge = request.form['judge']
        opp = request.form['opp']
        q="SELECT dateclosed from Cases WHERE ClientID=%s and caseno=%s and casetype=%s"
        v=(cid,caseno,casetype)
        mycursor.execute(q,v)
        datecc=mycursor.fetchone()
        if datecc and datecc[0] is not None:
            return render_template("update_case.html",msg="Case is closed.")
        if not dc:
            dc = None
        if dc:
            curr_stage = "closed"
            next_stage = "closed"
            prev_date = None
            next_date = None
            qry2 = "UPDATE casestatus SET prevdate=%s, nextdate=%s, currStage=%s, nextStage=%s WHERE ClientID=%s AND caseno=%s AND casetype=%s"
            val2 = (prev_date, next_date, curr_stage, next_stage, cid, caseno, casetype)
            mycursor.execute(qry2, val2)

        query =  "INSERT INTO updated_Cases VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        value = (caseno, casetype, cid, courtname, df, dc, judge, opp)
        

        qry=" UPDATE Cases SET courtname=%s,  datefiled=%s, dateclosed=%s, Judge=%s, Opposition=%s WHERE ClientID=%s and caseno=%s and casetype=%s"
        val=(courtname, df,dc,judge,opp,cid, caseno,casetype)
        print(qry)
        print(val)
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(query,value)
            mycursor.execute(qry,val)
        except:
            print("Error : Client not Inserted")
            error = True
            success = False
            msg="Failed"
        print(error)
        mydb.commit()
        return render_template("update_case.html",msg=msg)
    
@app.route("/get_search_pagecc",methods=['POST','GET'])
def get_search_pagecc():
    return render_template("search_cc.html")


@app.route("/ajaxlivesearchcc",methods=["POST","GET"])
def ajaxlivesearchcc():
    #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from clientcase "
            mycursor.execute(query)
            employee = mycursor.fetchall()
        else:    
            query = "SELECT * from clientcase WHERE caseno LIKE '%{}%'  OR casetype LIKE '%{}%' OR Judge LIKE '%{}%' OR Opposition LIKE '%{}%' OR ClientID LIKE '%{}%'  OR courtname LIKE '%{}%' OR datefiled LIKE '%{}%' OR dateclosed LIKE '%{}%' OR name LIKE '%{}%'  OR currStage LIKE '%{}%' OR nextStage LIKE '%{}%' ".format(search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word,search_word)
            mycursor.execute(query)
            numrows = int(mycursor.rowcount)
            employee = mycursor.fetchall()
            print(numrows)
            print(employee)
    return jsonify({'htmlresponse': render_template('responsecc.html', employee=employee, numrows=numrows)})


@app.route("/display_notes",methods=['POST','GET'])
def display_notes():
    # Select notes marked as "very urgent"
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM notes WHERE urgency = 'very urgent'")
    notes = cursor.fetchall()
    
    # Render the notes on an HTML page
    return render_template('notice.html', notes=notes)

@app.route("/noticeboard",methods=["POST","GET"])
def noticeboard():
    
    cursor=mydb.cursor();  
    query = " SELECT ClientID, caseno, casetype, phone, email, nextdate, courtname FROM clientcases WHERE nextdate <= CURDATE() + 7 AND nextdate >= CURDATE() ORDER BY nextdate"
    mycursor.execute(query)
    numrows = int(mycursor.rowcount)
    employee = mycursor.fetchall()
    print(numrows)
    print(employee)
    cursor.execute("SELECT * FROM notes WHERE urgency = 'very urgent'")
    notes = cursor.fetchall()
    cursor.execute("SELECT * FROM notes WHERE urgency = 'urgent'")
    roses = cursor.fetchall()
    cursor.execute("select distinct * from show_bill natural join contact where show_bill.ClientID=contact.clientID order by total desc")
    numrowss = int(mycursor.rowcount)
    tbill = cursor.fetchall()
    return  render_template('noticeboard.html', employee=employee, numrows=numrows,notes=notes,roses=roses,numrowss=numrowss,tbill=tbill)

@app.route('/totalbill', methods=['GET', 'POST'])
def totalbill():
    if request.method == 'POST':
        # get the clientID entered by the user
        clientID = request.form['clientID']

        # query the Bill table to get the total amount due for the client
        mycursor = mydb.cursor()
        query = "SELECT SUM(amtdue) FROM Bill WHERE ClientID = %s"
        values = (clientID,)
        mycursor.execute(query, values)
        result = mycursor.fetchone()

        # format the result message
        if result[0] is None:
            message = "No amount due for client " + clientID
        else:
            message = "Total amount due for client " + clientID + ": Rs." + str(result[0])
    else:
        message = ""
    
    return render_template('search_totalbill.html', message=message)

@app.route("/add_hours",methods=['POST','GET'])
def add_hours():
    return render_template("add_billable_hours.html")

@app.route('/add_billable_hours', methods=['POST'])
def add_billable_hours():
    if request.method == 'POST':
        client_id = request.form['client_id']
        case_type = request.form['casetype']
        case_no= request.form['caseno']
        worker = request.form['worker']
        h=request.form['hours']
        
        if worker == "partner":
            amt = 2000
        elif worker == "associate" or worker == "paralegal":
            amt = 1000
        elif worker == "PI" or worker == "other":
            amt = 500
        
        amtt=int(amt)*int(h)
        hi=int(h)
        
        qry="UPDATE Bill SET totalamt=totalamt+%s WHERE ClientID=%s AND casetype=%s AND caseno=%s"
        val=(amtt, client_id, case_type, case_no)
        query="UPDATE Bill SET amtdue=amtdue+%s WHERE ClientID=%s AND casetype=%s AND caseno=%s"
        value=(amtt, client_id, case_type, case_no)
        query1="UPDATE billablehours SET hours=hours+%s WHERE ClientID=%s AND casetype=%s AND caseno=%s AND worker=%s"
        value1=(hi,client_id,case_type,case_no,worker)
        
        success = True
        error = False
        msg="Done"
        try:
            mycursor.execute(qry,val)
            mycursor.execute(query,value)
            mycursor.execute(query1,value1)
        except:
            print("Error : bill not updated")
            error = True
            success = False
            msg="Failed"
        
        mydb.commit()
        return render_template("add_billable_hours.html",msg=msg)

@app.route('/upload_form')
def upload_form():
	return render_template('download.html')

@app.route('/generate_bill', methods=['POST','GET'])
def download_bill_pdf():
    # Get client's bills and billable hours
    client_id = request.form['client_id']
    query = "SELECT * FROM Bill WHERE ClientID = %s"
    val = (client_id,)
    mycursor.execute(query, val)
    bills = mycursor.fetchall()
    query = "SELECT * FROM billablehours WHERE ClientID = %s"
    mycursor.execute(query, val)
    hours = mycursor.fetchall()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add header and client information
    pdf.image('logo.png', pdf.w - 40, 10, 30)
    pdf.cell(40)
    pdf.set_font("Arial", size=18, style='B')
    pdf.cell(0, 10, f"Client Bill", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(40)
    pdf.cell(0, 10, f"Client ID: {client_id}", ln=1)
    
    # Add bill and billable hours information
    pdf.cell(10, 10, "")
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(0, 10, "Bills and Billable Hours:", ln=1)
    pdf.set_font("Arial", size=12)
    
    for bill in bills:
        # Add bill information
        pdf.cell(10)
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(0, 10, f"Case No: {bill[1]}, Case Type: {bill[2]}", ln=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(20)
        pdf.cell(0, 10, f"Total Amount: ${bill[3]}", ln=1)
        pdf.cell(20)
        pdf.cell(0, 10, f"Amount Paid: ${bill[4]}", ln=1)
        pdf.cell(20)
        pdf.cell(0, 10, f"Amount Due: ${bill[5]}", ln=1)
        
        # Add billable hours information for the current bill
        pdf.cell(10)
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(0, 10, "Breakdown of Billable Hours:", ln=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(10)
        pdf.cell(30, 10, "Worker", 1, 0, 'C')
        pdf.cell(20, 10, "Hours", 1, 0, 'C')
        pdf.cell(30, 10, "Per Hour", 1, 0, 'C')
        pdf.cell(30, 10, "Total Amount", 1, 0, 'C')
        pdf.ln()
        total_hours = 0
        total_amount = 0
        for hour in hours:
            if hour[1] == bill[1]:
                pdf.cell(10)
                pdf.cell(30, 10, f"{hour[3]}", ln=0)
                pdf.cell(20, 10, f"{hour[4]}", ln=0)
                hourly_rate = get_hourly_rate(hour[3])
                pdf.cell(30, 10, f"${hourly_rate}", ln=0)
                amount = hour[4] * hourly_rate
                total_hours += hour[4]
                total_amount += amount
                pdf.cell(30, 10, f"${amount}", ln=1)
        
        # Add total billable hours and amount for the current bill
        pdf.cell(10)
        pdf.cell(80, 10, f"Total Billable Hours: {total_hours}", ln=0)
        pdf.cell(30, 10, f"Total Amount: ${total_amount}", ln=1)
        pdf.ln()

    # Save PDF file and return fi
    # Set response headers and return PDF as response
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'attachment', filename='client_bill.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

@app.route('/download_month_pdf', methods=['POST','GET'])
def download_month_pdf():
    query = "SELECT * FROM casestatus WHERE prevdate <= CURDATE() AND prevdate >= CURDATE()-30"
    mycursor.execute(query)
    handled = mycursor.fetchall()
    query = "SELECT * FROM cases WHERE dateclosed <= CURDATE() AND dateclosed >= CURDATE()-30"
    mycursor.execute(query)
    closed = mycursor.fetchall()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add header and client information
    pdf.image('logo.png', pdf.w - 40, 10, 30)
    pdf.cell(40)
    pdf.set_font("Arial", size=18, style='B')
    pdf.cell(0, 10, f"Monthly Summary", ln=1)
    pdf.set_font("Arial", size=14)
    pdf.cell(40)
    pdf.ln()
    pdf.ln()
    pdf.ln()

    pdf.cell(10)
    pdf.set_font("Arial", size=13, style='B')
    pdf.cell(0, 10, "Cases Closed:", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.cell(10)
    pdf.cell(25, 10, "Case Number", 1, 0, 'C')
    pdf.cell(22, 10, "Case Type", 1, 0, 'C')
    pdf.cell(25, 10, "Client ID", 1, 0, 'C')
    pdf.cell(30, 10, "Court Name", 1, 0, 'C')
    pdf.cell(25, 10, "Judge", 1, 0, 'C')
    pdf.cell(25, 10, "Opposition", 1, 0, 'C')
    pdf.ln()

    for hand in closed:
        # Add bill information
        pdf.cell(10)
        pdf.cell(25, 10, f"{hand[0]}", ln=0)
        pdf.cell(22, 10, f"{hand[1]}", ln=0)
        pdf.cell(25, 10, f"{hand[2]}", ln=0)
        pdf.cell(30, 10, f"{hand[3]}", ln=0)
        pdf.cell(25, 10, f"{hand[6]}", ln=0)
        pdf.cell(25, 10, f"{hand[7]}", ln=0)
        pdf.ln()


    pdf.ln()
    pdf.cell(10)
    pdf.set_font("Arial", size=13, style='B')
    pdf.cell(0, 10, "Cases Handled:", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.cell(10)
    pdf.cell(25, 10, "Case Number", 1, 0, 'C')
    pdf.cell(25, 10, "Case Type", 1, 0, 'C')
    pdf.cell(25, 10, "Client ID", 1, 0, 'C')
    pdf.cell(25, 10, "Previous Date", 1, 0, 'C')
    pdf.cell(25, 10, "Next Date", 1, 0, 'C')
    pdf.cell(25, 10, "Current Stage", 1, 0, 'C')
    pdf.cell(25, 10, "Next Stage", 1, 0, 'C')
    pdf.ln()

    for hand in handled:
        # Add bill information
        pdf.cell(10)
        pdf.cell(25, 10, f"{hand[0]}", ln=0)
        pdf.cell(25, 10, f"{hand[1]}", ln=0)
        pdf.cell(25, 10, f"{hand[2]}", ln=0)
        pdf.cell(25, 10, f"{hand[3]}", ln=0)
        pdf.cell(25, 10, f"{hand[4]}", ln=0)
        pdf.cell(25, 10, f"{hand[5]}", ln=0)
        pdf.cell(25, 10, f"{hand[6]}", ln=0)
        pdf.ln()
        
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'attachment', filename='generate_month.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response


def get_hourly_rate(worker):
    if worker == "partner":
        return 2000
    elif worker == "associate" or worker == "paralegal":
        return 1000
    elif worker == "PI" or worker == "other":
        return 500




    
     


if __name__ == "__main__":
    app.secret_key = 'sec key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
