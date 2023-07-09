# import flask module
from flask import Flask, render_template,request,redirect

import pymysql

from db import DBConnection

import datetime

# Initialize Flask app
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def login():
	if request.method == 'POST':
		a_email = request.form["email"]
		a_password = request.form["password"]

		dbConn = DBConnection()
		conn,cur = dbConn.mysqlconnect()

		query = "SELECT * FROM users WHERE username='%s' and password='%s';" % (a_email,a_password)
		print(query)
		cur.execute(query)
		output = cur.fetchall()
		conn.close()

		if len(output) > 0:
			return redirect("/home")
		else:
			return render_template('login.html',message="Username/Password combination failed")
		
	return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
	if request.method == 'POST':
		r_first_name = request.form["first_name"]
		r_last_name = request.form["last_name"]
		r_email = request.form["email"]
		r_password = request.form["password"]

		dbConn = DBConnection()
		conn,cur = dbConn.mysqlconnect()
		
		
		query = "INSERT INTO `users` (`first_name`, `last_name`, `username`, `password`) VALUES ('%s', '%s', '%s', '%s');" % (r_first_name,r_last_name,r_email,r_password)

		print(query)
		cur.execute(query)
		#output = cur.fetchall()
		conn.commit()
		conn.close()

		return redirect('/')

	return render_template('register.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/forgot-password')
def forget_password():
	return render_template('forgot_password.html')

@app.route('/list-users')
def list_users():
	return render_template('users/list.html')

@app.route('/blogs')
def view_blogs():

	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	# SQL Query for selecting all blogs
	query = '''SELECT b.id as blog_id,
					b.name as title,
					b.slug as blog_slug,
					b.created_at,
					b.status,
					u.first_name,
					u.last_name
				FROM   blogs b
					JOIN users u
						ON u.id = b.user_id; '''
	
	print(query)
	cur.execute(query)
	output = cur.fetchall()
	conn.close()

	# Pass data to frontend	
	return render_template('blogs/list.html',blogs=output)

@app.route('/blogs/create',methods=['POST','GET'])
def create_blog():

	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	if request.method == 'GET':
		# SQL Query for selecting all blogs
		query = '''SELECT * FROM users; '''		
		cur.execute(query)
		output = cur.fetchall()
		conn.close()
		return render_template('blogs/add.html',users=output)
	else:
		a_title = request.form['title']
		a_slug = request.form['slug']
		a_content = request.form['content']
		a_status = request.form['status']
		a_user = request.form['user']

		a_created_at = datetime.datetime.now()

		query = '''INSERT INTO `blogs`
								(`name`,
								`slug`,
								`created_at`,
								`status`,
								`user_id`,
								`content`)
					VALUES      ('%s',
								'%s',
								'%s',
								'%s',
								'%s',
								'%s'); '''	% (a_title,a_slug,a_created_at,a_status,a_user,a_content)	
		cur.execute(query)
		conn.commit()
		conn.close()
		return redirect('/blogs')

@app.route('/blogs/edit')
def edit_blog():
	return render_template('blogs/edit.html')
# Running Flask Application
if __name__ == '__main__':
	app.run(debug=True,port=9000)
	