from flask import Flask, render_template, flash, request, redirect, url_for
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
# from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
# from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

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
# Add CKEditor
ckeditor = CKEditor(app)
# Add Database.
# Old SQLite Database.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host(localhost)/db_name'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dance@localhost/our_users'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://suzscwjtajwafc:0818742a3962aad0fd6629193248186ad6358c89ab8db42fe5659a238a9ac5d6@ec2-34-197-84-74.compute-1.amazonaws.com:5432/d6l07ihopap6bn'

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database. SQLAlchemy can easily work with most Databases. We can change SQLite with
# MySQL with simple row uncommenting.
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login stuff. Needed to use "@login_required"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass staff to navbar.
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create Search function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the database.
        posts = posts.filter(Posts.content.like(
            '%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all() # Order posts!
        return render_template("search.html", form=form,
            searched=post.searched, posts=posts)

# Create admin page.
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 19:
        return render_template('admin.html')
    else:
        flash("Sorry! You must be the addmin to access this page!")
        return redirect(url_for('dashboard'))


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get the username.
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the HASH VS the password inserted with the username
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user) # this will login, crreate the sessions etc.
                flash("Login sucessful!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password - Try again!")
        else:
            flash("This user doesn't exist! Try again...")
    return render_template('login.html', form=form)


# Create Logout route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out! Thanks for stopping by...")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        
        # Grab image name.
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Save That Image
        saver = request.files['profile_pic']
        # Change it to string to add to the database.
        name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
        
            flash('User updated successfully')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            db.session.commit()
            flash('Error! There was a problem!')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('dashboard.html',
            form=form, name_to_update=name_to_update, id = id)

    return render_template('dashboard.html')


# Delete Blog Posts
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Blog post deleted.")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

        except:
            # Return error message.
            flash("There was a problem deleting the post...")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts) 

    else:
        # Return error message.
        flash("You are not authorized to delete this post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts) 

# All Posts Page
@app.route('/posts')
def posts():
    # Grab all the posts from the database.
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts) 

# Create a route to show only 1 post
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# Edit post.
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id) # Find the post.
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)

    else:
        flash("You can't edit this post!")
        post = Posts.query.get_or_404(id)
        return render_template('post.html', post=post)        


# Add post page.
@app.route('/add_post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
            content=form.content.data,
            poster_id=poster,
            slug=form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''

        # Add post form data to the database
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog post submitted successfuly!")

    # our_posts = Posts.query.order_by(Posts.author)
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

# Create a secret key for the CSRF token.
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

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
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
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
            user = Users(username=form.username.data, 
                         name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
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



# Create Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255)) # Extension of the web address
    # Foreign Key To link Users(refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# The posts form place change to be defined in the last function
# Create a table model.
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=True)

    # Do some password stuff
    password_hash = db.Column(db.String(128))

    # User can have many posts
    posts = db.relationship('Posts', backref='poster') # we can
    # access Users table data in Post table through the relationship

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# if __name__ == '__main__':
#     app.run(debug=True)
