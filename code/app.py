# import flask module
from flask import Flask, render_template,request,redirect

# For JSON Response
from flask import jsonify

import pymysql

from db import DBConnection

import datetime

import uuid

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
					u.id as user_id,
					u.first_name,
					u.last_name,
					b.content
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

@app.route('/edit-blog/<int:id>',methods=['GET'])
def edit_blog(id):
	if request.method == 'GET':
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
					u.last_name,
					b.content
				FROM   blogs b
					JOIN users u
						ON u.id = b.user_id
						WHERE b.id =  %s; ''' % (id)
		
		cur.execute(query)
		output = cur.fetchone()
		print(output)

		# SQL Query for selecting all blogs
		query1 = '''SELECT * FROM users; '''
		
		cur.execute(query1)
		output1 = cur.fetchall()

		conn.close()

		return render_template('blogs/edit.html',blog=output,users=output1)
	else:
		
		# TODO Get Input
		# TODO Update Query

		return redirect('/blogs')

@app.route('/update-blog',methods=['POST'])
def update_blog():
	a_title = request.form['title']
	a_slug = request.form['slug']
	a_content = request.form['content']
	a_status = request.form['status']
	a_user = request.form['user']
	a_blog_id = request.form["blog_id"]


	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	query = '''
			UPDATE `blogs`
				SET    `name` = '%s',
				       `slug` = '%s',
				       `status` = %s,
				       `content` = '%s',
				       `user_id` = %s
				WHERE  `id` = %s; 
	''' % (a_title,a_slug,a_status,a_content,a_user,a_blog_id)

	cur.execute(query)
	conn.commit()
	conn.close()

	return redirect('/blogs')

@app.route('/delete-blog/<int:id>',methods=['GET'])
def delete_blog(id):

	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	query = '''DELETE FROM `blogs`
				WHERE  `id` = %s; 
			''' % id

	cur.execute(query)
	conn.commit()
	conn.close()
	
	return redirect('/blogs')

##### ----- API Endpoints --------------------------

@app.route('/api/blogs')
def api_blogs():
	response = {}
	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	# SQL Query for selecting all blogs
	query = '''SELECT b.id as blog_id,
					b.name as title,
					b.slug as blog_slug,
					b.created_at,
					b.status,
					u.id as user_id,
					u.first_name,
					u.last_name,
					b.content
				FROM   blogs b
					JOIN users u
						ON u.id = b.user_id; '''
	
	cur.execute(query)
	output = cur.fetchall()
	conn.close()

	#return render_template('blogs/list.html',blogs=output)
	return jsonify(output)

@app.route('/api/blogs/create', methods=['POST'])
def api_blogs_create():
	json_data = request.get_json()

	a_title = json_data.get('title')
	a_slug = json_data.get('slug')
	a_content = json_data.get('content')
	a_status = json_data.get('status')
	a_user = json_data.get('user_id')

	a_created_at = datetime.datetime.now()

	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

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

	response = {"message": "Blog Created Succesfully","status":True}
	return jsonify(response)

@app.route('/api/blogs/update',methods=['POST'])
def api_blogs_update():
	json_data = request.get_json()

	a_blog_id = json_data.get('id')
	a_title = json_data.get('title')
	a_slug = json_data.get('slug')
	a_content = json_data.get('content')
	a_status = json_data.get('status')
	a_user = json_data.get('user_id')

	a_token = json_data.get('token')

	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	query_token = '''SELECT * FROM users WHERE token =  '%s'; ''' % (a_token)
	cur.execute(query_token)
	output_token = cur.fetchone()
	if not output_token:
		return jsonify({"message":"The provided token is invalid", "status":False})

	# Handle case when specific id is not present
	# SQL Query for selecting all blogs
	query = '''SELECT * FROM  blogs WHERE id =  %s; ''' % (a_blog_id)
	cur.execute(query)
	output = cur.fetchone()

	if not output:
		return jsonify({"message": "Blog with provided ID doesn't exist", "status": False})

	query1 = '''
			UPDATE `blogs`
				SET    `name` = '%s',
				       `slug` = '%s',
				       `status` = %s,
				       `content` = '%s',
				       `user_id` = %s
				WHERE  `id` = %s; 
	''' % (a_title,a_slug,a_status,a_content,a_user,a_blog_id)

	cur.execute(query1)
	conn.commit()
	conn.close()

	response = {"message": "Blog updated Succesfully","status": True}
	return jsonify(response)

@app.route('/api/blogs/delete',methods=['POST'])
def api_blogs_edit():
	json_data = request.get_json()
	a_blog_id = json_data.get('id')

	# Initialize DB Connection
	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	# SQL Query for selecting all blogs
	query = '''SELECT * FROM  blogs WHERE id =  %s; ''' % (a_blog_id)
	cur.execute(query)
	output = cur.fetchone()

	if not output:
		return jsonify({"message": "Blog with provided ID doesn't exist", "status": False})

	query1 = '''DELETE FROM `blogs`
				WHERE  `id` = %s; 
			''' % a_blog_id

	cur.execute(query1)
	conn.commit()
	conn.close()

	response = {"message": "Blog deleted Succesfully","status": True}
	return jsonify(response)

@app.route('/api/login',methods=['POST'])
def api_login():
	json_data = request.get_json()
	a_email = json_data.get("email")
	a_password = json_data.get("password")

	dbConn = DBConnection()
	conn,cur = dbConn.mysqlconnect()

	query = "SELECT * FROM users WHERE username='%s' and password='%s';" % (a_email,a_password)
	
	cur.execute(query)
	output = cur.fetchall()
	

	if len(output) > 0:
		token = uuid.uuid4().hex
		query1 = '''
					UPDATE `users`
						SET    `token` = '%s'
						WHERE  `username` = '%s'; 
			''' % (token,a_email)
		print(query1)
		cur.execute(query1)
		conn.commit()
		response = {"message": "Login Succesfull","status": True,"token":token}
	else:
		response = {"message": "Email/Password combination doesn't match","status": False}

	conn.close()
	return jsonify(response)

# Running Flask Application
if __name__ == '__main__':
	app.run(debug=True,port=9000)
	