from flask import Flask, render_template, redirect, url_for, request,session,abort
from flask import request 
import os
from flask import Flask, render_template, redirect, url_for, request,send_from_directory
from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import time
from datetime import timedelta
import os
#from connecttodb import conn
import socket

app = Flask(__name__) 


app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
#app.config['SECRET_KEY']='dd06be55a06c03312b2ab109b5f8f6ab'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = 'please login '

import pymssql

conn = pymssql.connect(host='XXX.XXX.XXX.XXX:XXXX' ,
user = 'username',
password ='password',
database = 'login_db'
)
class User(UserMixin):
    pass

def fetch_cookie():
    cookie = request.cookies
    return f" this is {cookie}"


@app.route('/')
def index1():
    #fetch_cookie()
    return render_template('log.html', length = 10)


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


@login_manager.user_loader
def user_loader(crewid):
	
	crewid = session.get('crewid')
	#avoidtoofast()
	#time.sleep(0.5)
	#password = request.form.get('InputPassword')
	#cursor.execute("SELECT name , crewid, ext FROM departmentuser WHERE crewid =  %(username)s AND password = %(pw)d",{'username':crewid, 'pw':password})
	#print("crewid",crewid)
	#name  = cursor.fetchall()
	#crewid  = cursor.fetchall()
	if len(crewid)==0:
		return 

	user = User()
	user.id = crewid
	# DO NOT ever store passwords in plaintext and always compare password
	# hashes using constant-time comparison!
	# user.is_authenticated = True
	# print('user.is_authenticated',user.is_authenticated)
	
	return user

from flask import request, render_template, url_for, redirect, flash
@app.route('/login', methods=['GET', 'POST'])
def login():
	try:
		if request.method == 'GET':
			if  session.get('name') is None or session.get('name') is False:
				return render_template("login.html")
			else:
				#print(type(session.get('name')))
				return redirect(url_for('index'))
		crewid = request.form['InputAD']
		password = request.form['InputPassword']
		#print('crewid',crewid,type(crewid) )
		#print('password',password,type(password) )
		date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		cursor = conn.cursor()
		cursor.execute("SELECT name , crewid FROM departmentuser WHERE crewid =  %(username)s AND password = %(pw)d",{'username':crewid, 'pw':password})
		nameandid  = cursor.fetchall()
		#print('testsqlinjection:',nameandid)
		hostname = socket.gethostname()
		ip = socket.gethostbyname(hostname)
		#print(nameandid)
		if (len(nameandid)>0):
			name =nameandid[0][0]
			#print(name,type(name))
			crewid =nameandid[0][1]
			#print(crewid,type(crewid))
			user = User()
			user.id = crewid
			login_user(user)
			session['name'] = name
			session['crewid'] = crewid
			#flash(f'{name},您好')
			cursor.execute("INSERT INTO loginlog (loginuserid,loginsuccess,hostname,ip) VALUES(%(crewid)s, %(loginsuccess)d,%(hostname)s,%(ip)s)",{'crewid':crewid, 'loginsuccess':1,'hostname':hostname,'ip':ip})
			conn.commit()
			#print("success")
			#如果temp裡沒有該使用者資料夾，建一個
			#makedir(crewid)
			return redirect(url_for('index'))
		flash('帳號或密碼錯誤...')
		cursor.execute("INSERT INTO loginlog (loginuserid,loginsuccess,hostname,ip) VALUES(%(crewid)s, %(loginsuccess)d,%(hostname)s,%(ip)s)",{'crewid':crewid, 'loginsuccess':0,'hostname':hostname,'ip':ip})
		conn.commit()
		cursor.close()
		return render_template('login.html')
	except:
		app.logger.error("Catch an exception.", exc_info=True)
		abort(500)
	

@app.route('/logout')
@login_required
def logout():
	try:
		crewid = current_user.get_id()
		session['name']=False
		session['crewid']=False
		logout_user()
		flash(f'已成功登出')
		return redirect(url_for('login'))
	except:
		app.logger.error("Catch an exception.", exc_info=True)
		abort(500)




def fetch_cookie():
	cookie = request.cookies
	return f" this is {cookie}"

import atexit
@atexit.register
def goodbye():
	try:
		#cleartempfolder() change to clear content
		conn.close()
		print('Goodbye')
	except:
		app.logger.error("Catch an exception in func.", exc_info=True)
		abort(500)
@app.errorhandler(404)
def page_not_found(e): 
    return render_template('404nopage.html')
@app.errorhandler(500)
def Internal_Server_Error(e): 
    return render_template('500.html')#500 Internal Server Error
if __name__ == '__main__': 
    app.run(debug=True)
