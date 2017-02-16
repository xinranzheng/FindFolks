#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from flask.ext.hashing import Hashing
from flask_bootstrap import Bootstrap
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)
hashing = Hashing(app)
Bootstrap(app)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       db='meetup',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')


#Define route for login
@app.route('/login')
def login():
	cursor = conn.cursor()
	#eventName = request.form['events']
	query = 'SELECT * from an_event WHERE start_time between CURRENT_DATE() and DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY)'
	cursor.execute(query)
	data1 = cursor.fetchall()
	if(data1):
		render_template('login.html', eventTable=data1)
	query = 'SELECT category, group_name, group_id from a_group NATURAL JOIN about group by group_id'
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	if(data):
		render_template('login.html', groupInterestTable=data)
	if(data and data1):
		return render_template('login.html', groupInterestTable=data, eventTable=data1)


@app.route('/findGroupInterests', methods=['GET', 'POST'])	
def findGroupInterests():
	if('username' in session):
		query = 'SELECT category, group_name, group_id from a_group NATURAL JOIN about group by group_id'
		cursor = conn.cursor()
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('group.html', groupInterestTable=data)
		else:
			errorForSearchGroups = 'Cannot find information you requested.'
			return render_template('group.html', groupInterestTableError=errorForSearchGroups)
	else:	
		error = 'Invalid login or username'
		return render_template('group.html', groupInterestTableError=error)



@app.route('/viewGroups', methods=['GET', 'POST'])
def viewGroups():
	if('username' in session):
		cursor = conn.cursor()
		username = session['username']
		query = 'SELECT group_id, group_name, description from a_group'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('group.html', allGroupTable=data)
		else:
			allGroupTableError = 'There are no groups.'
			return render_template('group.html', allGroupTableError=allGroupTableError)
	else:	
		error = 'Invalid login or username'
		return render_template('group.html', allGroupTableError=error)



@app.route('/joinGroup', methods=['GET', 'POST'])
def joinGroups():
	if('username' in session):
		cursor = conn.cursor()
		username = session['username']
		groupID = request.form['groupID']
		query = 'SELECT * from belongs_to where group_id=%s and username=%s'
		cursor.execute(query, (groupID, username))
		data = cursor.fetchone()
		if(not data):
			query = 'INSERT into belongs_to (group_id, username) VALUES (%s, %s)'
			cursor.execute(query, (groupID, username))
			cursor.close()
			conn.commit()
			success = 'You have joined this group! :D'
			return render_template('group.html', success=success)
		else:
			error = 'You are already part of this group!'
			return render_template('group.html', errorJoinGroup=error)
	else:	
		error = 'Invalid login or username'
		return render_template('group.html', errorJoinGroup=error)
	
		





@app.route('/addFriend', methods=['GET', 'POST'])
def addFriend():
	if('username' in session):
		cursor = conn.cursor()
		username = session['username']
		friendname = request.form['friendname']
		query = 'SELECT * from friend where friend_of=%s and friend_to=%s'
		cursor.execute(query, (username, friendname))
		data = cursor.fetchall()
		if(data):
			cursor.close()
			error = 'You are already friends with this user'
			return render_template('home.html', errorAddFriend=error)
		else:
			query = 'INSERT into friend (friend_of, friend_to) VALUES (%s, %s)'
			cursor.execute(query, (username, friendname))
			conn.commit()
			cursor.close()
			return render_template('home.html', friendAddTable=data)	
	else:	
		error = 'Invalid login or username'
		return render_template('login.html', errorAddFriend=error)

@app.route('/rate', methods=['GET', 'POST'])
def rate():
	if('username' in session):
		cursor = conn.cursor()
		username = session['username']
		eventID = request.form['eventID']
		eventID = int(eventID)
		rating = request.form['rating']
		rating = int(rating)
		query = 'UPDATE sign_up SET rating=%s WHERE event_id=%s and username=%s'
		cursor.execute(query, (rating, eventID, username))
		conn.commit()
		cursor.close()
		success='Your rating has been added!'
		return render_template('viewEverythingEventRelated.html', successfulRating=success)
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', errorRating=error)

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/signUpForEvent', methods=['GET', 'POST'])
def signUp():
	if('username' in session):
		cursor = conn.cursor()
		username = session['username']
		eventID = request.form['eventID']
		eventID = int(eventID)
		query = 'SELECT * from sign_up where sign_up.event_id=%s and sign_up.username=%s'
		cursor.execute(query, (eventID, username))
		data = cursor.fetchall()
		if(data):
			error = 'You have already signed up! :D'
			return render_template('viewEverythingEventRelated.html', errorSignUp=error)	
		else:
			query2 = 'INSERT into sign_up (event_id, username) VALUES (%s, %s)'
			cursor.execute(query2, (eventID, username))
			conn.commit()
			cursor.close()
			success='You have signed up!'
			return render_template('viewEverythingEventRelated.html', successfulSignUp=success)	
	else:
		error = 'Invalid login or username'
		return render_template('viewEverythingEventRelated.html', errorSignUp=error)


@app.route('/createGroup', methods=['GET', 'POST'])
def createTheGroup():
	if('username' in session):
		username = session['username']
		groupname = request.form['groupname']
		description = request.form['description']
		cursor = conn.cursor()
		#query = 'INSERT into a_group (group_name, description, creator) Values (%s, %s, %s)'
		query = 'INSERT into a_group (group_name, description, creator) VALUES(%s,%s, (SELECT username from member WHERE member.username=%s))'
		cursor.execute(query, (groupname, description, username))
		#query1 ='INSERT into belongs_to (group_name, username, authorized) Values (%s, %s, %s)'
		query1='INSERT into belongs_to (group_id, username, authorized) VALUES((SELECT group_id from a_group where group_name=%s),(select username from member where member.username=%s), %s)'
		cursor.execute(query1, (groupname,username,1))
		conn.commit()
		cursor.close()
		success='Your group has been added!'
		return render_template('group.html', success=success)
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)




@app.route('/viewEverythingEventRelated')
def viewEverythingEventRelated():
	return render_template('viewEverythingEventRelated.html')


@app.route('/groups')
def groups():
	return render_template('group.html')

@app.route('/findFriend', methods=['GET', 'POST'])
def findFriend():
	if('username' in session):
		cursor = conn.cursor()
		friendname = request.form['friendname']
		query = 'SELECT firstname, lastname, username from member where username=%s'
		cursor.execute(query, friendname)
		data = cursor.fetchall()
		cursor.close()
		if(not data):
			error = 'There does not exist any records of your search'
			return render_template('home.html', errorFriend=error)
		else:
			return render_template('home.html', friendTable=data)
			#query = 'SELECT * from friend where username=%s and friend_to=%s'
			#cursor.execute(query, (username, friendname))
			#data = cursor.fetchall()
			#if(data):
				#cursor.close()
				#error = 'You are already friends with this user'
				#return render_template('home.html', errorFriend=error)
			#else:
				#query = 'INSERT into friend (friend_of, friend_to) VALUES (friendname, username)'
				#cursor.execute(query)
				#cursor.close()
				#return render_template('home.html', friendTable=data)
	else:
		error = 'Invalid login or username'
		return render_template('login.html', errorFriend=error)


@app.route('/grabEventTables', methods=['GET', 'POST'])
def grabEventTable():
	if('username' in session):
		cursor = conn.cursor()
		#eventName = request.form['events']
		query = 'SELECT * from an_event WHERE start_time between CURRENT_DATE() and DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY)'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		return render_template('login.html', eventTable=data)
	else:
		error = 'Invalid login or username'
		return render_template('login.html', error=error)


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']



	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM member WHERE username = %s and password = %s'
	tempPass = hashing.hash_value(password, salt='')
	cursor.execute(query, (username, tempPass))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['logged_in'] = True
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	firstname = request.form['firstname']
	lastname = request.form['lastname']
	email = request.form['email']
	zipcode = request.form['zipcode']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query1 = 'SELECT * FROM member WHERE username = %s and email = %s'
	#stores the results in a variable
	cursor.execute(query1, (username, email))
	data1 = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data1):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		hashedPW = hashing.hash_value(password, salt='')
		ins1 = 'INSERT INTO member VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins1, (username,hashedPW, firstname, lastname, email, zipcode))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor();
		query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
		cursor.execute(query, (username))
		data = cursor.fetchall()
		cursor.close()
		return render_template('home.html', username=username, posts=data)
	else:
		error = 'Invalid login or username'
		return render_template('login.html', error=error)	
	
@app.route('/viewRecentEvents', methods=['GET', 'POST'])
def viewRecentEvents():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor();
		query1 = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name FROM member inner JOIN sign_up on member.username=sign_up.username INNER JOIN an_event on sign_up.event_id=an_event.event_id INNER JOIN organize on organize.event_id = an_event.event_id INNER JOIN a_group on a_group.group_id=organize.group_id WHERE member.username=%s and an_event.start_time between CURRENT_DATE() and DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY)'
		cursor.execute(query1, (username))
		data = cursor.fetchall()
		cursor.close()
		return render_template('viewEverythingEventRelated.html', recentEvents=data)
	else:
		error = 'Invalid login or username'
		return render_template('login.html', error=error)	


@app.route('/makeEvent', methods=['GET', 'POST'])
def makeEvent():
	if('username' in session):
		username = session['username']
		groupname = request.form['groupname']
		title = request.form['title']
		description = request.form['description']
		starttime = request.form['starttime']
		endtime = request.form['endtime']
		location = request.form['location']
		zipcode = request.form['zipcode']
		cursor = conn.cursor()
		query='SELECT authorized from belongs_to NATURAL JOIN a_group where username=%s and group_name=%s and authorized=%s'
		cursor.execute(query, (username, groupname,1))
		data=cursor.fetchone()
		if(data):
			query3= 'INSERT into an_event (title, description, start_time, end_time, location_name, zipcode) VALUES (%s, %s, %s, %s, (SELECT location_name from location where location_name=%s and zipcode=%s), (SELECT zipcode from location where location_name=%s and zipcode=%s))'
			cursor.execute(query3, (title,description,starttime,endtime, location, zipcode, location, zipcode))
			last_event_id = conn.insert_id()
			#query5 = 'SELECT LAST_INSERT_ID()'
			#cursor.execute(query5)
			#data=cursor.fetchone()
			query4= 'INSERT into organize (event_id, group_id) VALUES (%s,(SELECT group_id from a_group NATURAL JOIN belongs_to WHERE username=%s and group_name=%s and authorized=%s))'
			cursor.execute(query4, (last_event_id, username, groupname, 1))
			query6 = 'INSERT into sign_up (event_id, username) VALUES (%s, %s)'
			cursor.execute(query6, (last_event_id, username))
			conn.commit()
			cursor.close()
			success='Your event has been created!'
			return render_template('viewEverythingEventRelated.html', successAuth=success)
		else:
			error = 'You are not authorized to do this!!'
			return render_template('viewEverythingEventRelated.html', errorNotAuth=error)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/viewAllEvents', methods=['GET', 'POST'])
def viewAllEvents():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		query1 = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name FROM an_event INNER JOIN organize on organize.event_id = an_event.event_id INNER JOIN a_group on a_group.group_id=organize.group_id WHERE an_event.start_time >= CURRENT_DATE()'
		cursor.execute(query1)
		data = cursor.fetchall()
		cursor.close()
		return render_template('viewEverythingEventRelated.html', allEventsOnwards=data)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/viewFriendEvents', methods=['GET', 'POST'])
def viewFriendEvents():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		query = 'SELECT DISTINCT an_event.event_id, an_event.title, username FROM member natural join sign_up inner join an_event on sign_up.event_id = an_event.event_id WHERE member.username in (SELECT friend_to FROM friend WHERE friend_of = %s) and an_event.start_time >= CURRENT_DATE() '
		cursor.execute(query, (username))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('home.html', friendsEvents=data)
		else:
			error='You have no friends.'
			return render_template('home.html', errorViewFriendEvent=error)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('home.html', errorViewFriendEvent=error)


@app.route('/viewAllGroupRating', methods=['GET', 'POST'])
def viewAllGroupRating():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		query = 'SELECT AVG(rating) as rating,organize.group_id from sign_up NATURAL JOIN organize NATURAL JOIN an_event WHERE group_id in (SELECT group_id from belongs_to NATURAL JOIN member WHERE member.username=%s) GROUP by organize.group_id'
		cursor.execute(query, (username))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('group.html', allGroupTableRatings=data)
		else:
			error='Your friends have not rated yet!'
			return render_template('group.html', errorAllGroupRating=error)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/pastEvents', methods=['GET', 'POST'])
def viewPastEvents():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		query1 = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name, sign_up.rating FROM an_event INNER JOIN organize on organize.event_id = an_event.event_id INNER JOIN a_group on a_group.group_id=organize.group_id INNER JOIN sign_up on an_event.event_id=sign_up.event_id WHERE an_event.end_time <= CURRENT_DATE()'
		cursor.execute(query1)
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('viewEverythingEventRelated.html', pastEventsData=data)
		else:
			errorPastEvent = 'There was a problem with this request.'
			return render_template('viewEverythingEventRelated.html', errorPastEvent=errorPastEvent)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)


		
@app.route('/post', methods=['GET', 'POST'])
def post():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		blog = request.form['blog']
		query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
		cursor.execute(query, (blog, username))
		conn.commit()
		cursor.close()
		return redirect(url_for('home'))
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/showEvents', methods=['GET', 'POST'])
def showEvents():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		eventName = request.form['events']
		query = 'SELECT * from an_event WHERE start_time between CURRENT_DATE() and DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY)'
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		return render_template('home.html', username=username, eventTable=data)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/searchGroup', methods=['GET', 'POST'])	
def searchThyGroups():
	if('username' in session):
		username = session['username']
		myvar = request.form["queryToSearch"]
		cursor = conn.cursor()
		query = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name from an_event inner join organize on an_event.event_id=organize.event_id inner join a_group on a_group.group_id=organize.group_id inner join belongs_to on a_group.group_id=belongs_to.group_id WHERE an_event.start_time >= CURRENT_DATE() and belongs_to.username =%s and a_group.group_name=%s'
		cursor.execute(query, (username, myvar))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('viewEverythingEventRelated.html', username=username, selectTableView=data)
		else:
			errorForSearchGroups = 'Cannot find information you requested.'
			return render_template('viewEverythingEventRelated.html', username=username, errorForSearchGroups=errorForSearchGroups)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)






@app.route('/viewInterestEvents', methods=['GET', 'POST'])	
def viewInterestEvents():
	if('username' in session):
		username = session['username']
		cursor = conn.cursor()
		query = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, a_group.group_name from an_event NATURAL JOIN organize INNER JOIN a_group on a_group.group_id=organize.group_id WHERE organize.group_id in (SELECT group_id from interested_in NATURAL JOIN about WHERE interested_in.username=%s)'
		cursor.execute(query, (username))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('viewEverythingEventRelated.html', eventInterestTable=data)
		else:
			errorForSearchGroups = 'Cannot find information you requested.'
			return render_template('viewEverythingEventRelated.html', errorInterestTable=errorForSearchGroups)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/searchDescription', methods=['GET', 'POST'])	
def searchDescription():
	if('username' in session):
		username = session['username']
		myvar = request.form["queryToSearch"]
		cursor = conn.cursor()
		query = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name from an_event inner join organize on an_event.event_id=organize.event_id inner join a_group on a_group.group_id=organize.group_id inner join belongs_to on a_group.group_id=belongs_to.group_id WHERE an_event.start_time >= CURRENT_DATE() and an_event.description=%s'
		cursor.execute(query, (myvar))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('viewEverythingEventRelated.html', username=username, selectTableView=data)
		else:
			errorForSearchGroups = 'Cannot find information you requested.'
			return render_template('viewEverythingEventRelated.html', username=username, errorForSearchGroups=errorForSearchGroups)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/searchEventID', methods=['GET', 'POST'])	
def searchEventID():
	if('username' in session):
		username = session['username']
		myvar = request.form["queryToSearch"]
		cursor = conn.cursor()
		query = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name from an_event inner join organize on an_event.event_id=organize.event_id inner join a_group on a_group.group_id=organize.group_id inner join belongs_to on a_group.group_id=belongs_to.group_id WHERE an_event.start_time >= CURRENT_DATE() and an_event.event_id=%s'
		cursor.execute(query, (myvar))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('viewEverythingEventRelated.html', username=username, selectTableView=data)
		else:
			errorForSearchGroups = 'Cannot find information you requested.'
			return render_template('viewEverythingEventRelated.html', username=username, errorForSearchGroups=errorForSearchGroups)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)

@app.route('/searchDate', methods=['GET', 'POST'])	
def searchDate():
	if('username' in session):
		username = session['username']
		myvar = request.form["queryToSearch"]
		cursor = conn.cursor()
		query = 'SELECT an_event.event_id, title, start_time, location_name, an_event.zipcode, an_event.description, group_name from an_event inner join organize on an_event.event_id=organize.event_id inner join a_group on a_group.group_id=organize.group_id inner join belongs_to on a_group.group_id=belongs_to.group_id WHERE an_event.start_time >= CURRENT_DATE() and an_event.start_time=%s'
		cursor.execute(query, (myvar))
		data = cursor.fetchall()
		cursor.close()
		if(data):
			return render_template('viewEverythingEventRelated.html', username=username, selectTableView=data)
		else:
			errorForSearchGroups = 'Cannot find information you requested.'
			return render_template('viewEverythingEventRelated.html', username=username, errorForSearchGroups=errorForSearchGroups)
	else:
		error = 'It seems that this is not your account. Please log in again!'
		return render_template('login.html', error=error)



@app.route('/displayLogoutMessage')
def displayLogoutMessage():
	return render_template('logoutmessage.html')

@app.route('/logout')
def logout():
	session.pop('username')
	session["__invalidate__"] = True
	session.clear()
	return redirect('/displayLogoutMessage')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5001, debug = True)
