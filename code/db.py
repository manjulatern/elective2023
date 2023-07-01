import pymysql

class DBConnection():

	def mysqlconnect(self):
		print("Connecting to database.....")
		conn = pymysql.connect(
				host='localhost',
				user='manjul',
				password='Manjul1234*',
				db='elective'
			)

		cur = conn.cursor()
		return conn, cur
