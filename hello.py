from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea

# # Types of forms elements
# BooleanField, DateField, DateTimeField, DecimalField, FileField, HiddenField, MultipleField
# FieldList, FloatField, FormField, IntegerField, PasswordField, RadioField, SelectField
# SelectMultipleField, SubmitField, StringField, TextAreaField

# # Validators
# DataRequired, Email, EqualTo, InputRequired, IPAddress, Length, MacAddress, NumberRange, Optional
# Regexp, URL, UUID, AnyOf, NoneOf

# https://getbootstrap.com/ # Bootstrap templates.
# {{ url_for('user', name='Sinan') }} # Jinja2 - use 'url_for' for a route that needs a variable.

#  Create a Flask instance.
app = Flask(__name__)

# Add Database.
# Old SQLite Database.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host(localhost)/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dance@localhost/our_users'

# Initialize the database. SQLAlchemy can easily work with most Databases. We can change SQLite with
# MySQL with simple row uncommenting.
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255)) # Extension of the web address

# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# All Posts Page
@app.route('/posts')
def posts():
    # Grab all the posts from the database.
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts) 

# Add post page.
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            slug=form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add post form data to the database
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog post submitted successfuly!")

    our_posts = Posts.query.order_by(Posts.author)
    # Redirect to the webpage
    return render_template("add_post.html", form=form)

# JSON thing.
@app.route('/date')
def get_current_date():
    favorite_pizza = {
    "Mary": "Peperoni",
    "Tom": "Cheese",
    "Sinan": "Chicken Corn"
    }
    return {"Date": date.today()}


# Create a table model.
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Do some password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string.
    def __repr__(self):
        return '<Name %r>'


# Create a secret key for the CSRF token.
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


# Create a form class / CSRF tokens prevents hackers.
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a form class.
class PasswordForm(FlaskForm):
    email = StringField("What's your email?", validators=[DataRequired()])
    password_hash = PasswordField("What's your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a form class.
class NamerForm(FlaskForm):
    name = StringField("What's your email?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Delete Database Record
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")

        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html',
        form=form, name=name, our_users=our_users)
    except:
        flash("There was a problem deleting the user!")
        return render_template('add_user.html',
        form=form, name=name, our_users=our_users)

# Update Database Record.
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            db.session.commit()
            flash('Error! There was a problem!')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html',
            form=form, name_to_update=name_to_update, id = id)


# Route for user data input.
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password!!!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.date_added)
    print(our_users)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Jinja tags to consider: safe, capitalize, lower, upper, title, trim, striptags
@app.route('/')
def index():
    flash("FLASH message!")  # Try a Flash message.
    first_name = "Vasilka"
    stuff = "This is <strong>bold</strong> text"
    stuff_2 = "No HTML text here"
    favorite_pizza = ['peperoni', 'mushroom', 'cheese', 41]
    return render_template('index.html',
                           first_name=first_name,
                           stuff=stuff,
                           stuff_2=stuff_2,
                           favorite_pizza=favorite_pizza)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# Create custom error pages.
# Invalid URL.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal server Error.
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# Create Password Test Page to contain the form.
@app.route('/test_pw', methods=['GET', 'POST'])  # We need to be able to post the form.
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        # Clear the form.
        form.email.data = ''
        form.password_hash.data = ''
        
        # Look up user by email address.
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # Check hashed password.
        passed = check_password_hash(pw_to_check.password_hash, password)


    return render_template('test_pw.html', email=email, 
        password=password, pw_to_check=pw_to_check, passed=passed,
        form=form)



# Create Name Page to contain the form.
@app.route('/name', methods=['GET', 'POST'])  # We need to be able to post the form.
def name():
    name = None  # Create a name variable available on the top function level.
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data  # Give the name variable another value.
        form.name.data = ''
        flash("Form submitted successfully!")
    return render_template('name.html', name=name, form=form)  # Obviously the 'name.html' page
                                            # gets re-rendered on SUBMIT.


# if __name__ == '__main__':
#     app.run(debug=True)
