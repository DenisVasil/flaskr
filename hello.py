from flask import Flask, render_template

# create a flask intance

app = Flask(__name__)

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