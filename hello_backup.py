from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# create a flask intance

app = Flask(__name__)

# connet to a database

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:denis@localhost/ourusers'

# Create a secrt key

app.config['SECRET_KEY'] = "my super secret key"

#initialize a database

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Create a blog post model

class Posts(db.Model):
	id = db.Column( db.Integer, primary_key = True )
	title = db.Column( db.String(255) )
	content = db.Column( db.Text )
	author = db.Column( db.String(255) )
	date_posted = db.Column( db.DateTime, default=datetime.utcnow )
	slug = db.Column( db.String(255) )


#Create a Posts form
class PostForm(FlaskForm):
	title = StringField("Title", validators = [DataRequired()])
	content = StringField("Content", validators = [DataRequired()], widget = TextArea())
	author = StringField("Author", validators = [DataRequired()])
	slug = StringField("Slug", validators = [DataRequired()])
	submit = SubmitField("Submit", validators = [DataRequired()])

# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Username", validators = [DataRequired()])
	password = PasswordField("Password", validators = [DataRequired()])
	submit = SubmitField("Submit", validators = [DataRequired()])

# Login initiation

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))
# Create Login Page
@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username = form.username.data).first()
		if user:
			#Check the hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login successful!")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password! Try again.")
		else:
			flash("That user does not exist. Try again!")

	return render_template('login.html', form = form)

# Crete Logout page
@app.route('/logoout', methods = ['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You have been logged out.")
	return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favourite_color = request.form['favourite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash('User udated successfully!')
			return render_template('dashboard.html',
				form = form,
				name_to_update = name_to_update)
		except:
			flash('Error! Try again.')
			return render_template('dashboard.html',
				form = form,
				name_to_update = name_to_update)
	else:
		return render_template('dashboard.html',
				form = form,
				name_to_update = name_to_update,  id = id)
	return render_template('dashboard.html')

#Deleteing posts
@app.route('/posts/delete/<int:id>')
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)

	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		flash("Blog post was deleted")
		# Take all posts from the db
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template('posts.html', posts = posts)
	except:
		#Error message
		flash("There was a roblem deleteing ost. Try again!")
		# Take all posts from the db
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template('posts.html', posts = posts)

# Blog post page
@app.route("/posts")
def posts():
	#Get posts from the db
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template('posts.html', posts = posts)

# Adding view of individual post
@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post = post)

#Editing Posts
@app.route('/posts/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		#Update db
		db.session.add(post)
		db.session.commit()
		flash("Post has been updated!")
		return redirect(url_for('post', id = post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content
	return render_template('edit_post.html', form = form)



# Add post page
@app.route('/add-post', methods = ['GET', 'POST'])		
#@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title = form.title.data, content = form.content.data, author = form.author.data, slug = form.slug.data)
		#Clear the form
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''
		#Add post data to db
		db.session.add(post)
		db.session.commit()
		#Return a message
		flash("Blog Post Submittd Successfully!")
	#Redirect to the webpage
	return render_template('add_post.html', form = form)
#Create a database model

class Users(db.Model, UserMixin):
	id = db.Column( db.Integer, primary_key = True)
	username = db.Column( db.String(20), nullable = False, unique = True)
	name = db.Column( db.String(200), nullable = False)
	email = db.Column( db.String(120), nullable = False, unique = True)
	favourite_color = db.Column( db.String(120))
	date_added = db.Column( db.DateTime, default=datetime.utcnow)
	# Create password hashing
	password_hash = db.Column(db.String(128))
	
	@property
	def password(self):
		raise AttributeError("Password is not a readable attribute!")

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)


	# Ceate a string
	def __repr__(self):
		return '<Name %r>' % self.name

# Delete route
@app.route("/delete/<int:id>")
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User deleted successfully!")

		our_users = Users.query.order_by(Users.date_added)
		return render_template('add_user.html',
			form = form,
			name = name,
			our_users = our_users)


	except:
		flash("Ther was a problem. Try again!")
		return render_template('add_user.html',
			form = form,
			name = name,
			our_users = our_users)

#	def __init__(self, arg):
#		super(Users, self).__init__()
#		self.arg = arg

# Database form
class UserForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired()])
	username = StringField("Username", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired()])
	favourite_color = StringField("Favourite Color")
	password_hash = PasswordField("Password", validators = [DataRequired(), EqualTo('password_hash2', message = 'Passwords must match!')])
	password_hash2 = PasswordField("Confirm Password", validators = [DataRequired()])
	submit = SubmitField("Submit")


# Update database record

@app.route("/update/<int:id>", methods = ['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favourite_color = request.form['favourite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash('User udated successfully!')
			return render_template('update.html',
				form = form,
				name_to_update = name_to_update)
		except:
			flash('Error! Try again.')
			return render_template('update.html',
				form = form,
				name_to_update = name_to_update)
	else:
		return render_template('update.html',
				form = form,
				name_to_update = name_to_update,  id = id)

# Password form
class PasswordForm(FlaskForm):
	email = StringField("What`s your email?", validators = [DataRequired()])
	password_hash = PasswordField("What`s your password?", validators = [DataRequired()])
	submit = SubmitField("Submit")
# Create a form class

class NamerForm(FlaskForm):
	name = StringField("What`s your name?", validators = [DataRequired()])
	submit = SubmitField("Submit")



# create a route decoraotr

@app.route("/")
def index():
	first_name = "Denis"
	stuff = "This is bold text"
	favourit_pizza = ["Mushroom", "Cheese", "Peeroni", 42]
	return render_template("index.html",
		first_name = first_name,
		stuff = stuff,
		favourit_pizza = favourit_pizza)
#def index():
# 	return "<h1>Hello World!</h1>"

@app.route('/user/add', methods = ['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email = form.email.data).first()
		if user is None:
			# Hash the password
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(username = form.username.data, name=form.name.data, email=form.email.data, favourite_color = form.favourite_color.data, password_hash = hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.favourite_color.data = ''
		form.password_hash = ''

		flash("User added successfully!")

	our_users = Users.query.order_by(Users.date_added)
	return render_template('add_user.html',
		form = form,
		name = name,
		our_users = our_users)

@app.route("/user/<name>")
def user(name):
	return render_template("user.html", user_name = name)
	#return f"<h1>Hello, {name}"

# create custom error pages
# Invalid URL

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def internal_seerver_error(e):
	return render_template("500.html"), 500

# Create a password test page
@app.route('/test_pw', methods = ['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()
	#Valodate Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear form
		form.email.data = ''
		form.password_hash.data = ''
		flash("Form submitted successfully!")
		#Look up user by email
		pw_to_check = Users.query.filter_by(email = email).first()

		#Check hashed password
		passed = check_password_hash(pw_to_check.password_hash, password)
	return render_template("test_pw.html",
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)

# Create a name form page
@app.route('/name', methods = ['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	#Valodate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form submitted successfully!")

	return render_template("name.html",
		name = name,
		form = form)

# Returning JSON
@app.route('/date')
def get_current_date():
	return {'Date' : date.today()}