"""Define what the app displays."""
from flask import render_template, request, flash, redirect, session
from .forms import SignupForm, LoginForm, EditProfileForm, SearchForm, PostForm
from app import app, db, models, bcrypt, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Book, Post, ReadingList, Following, Liked
from sqlalchemy import and_, or_
import datetime
import json
app.app_context().push()


"""
columnName.like() learned from:
https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_filter_operators.htm

Password hashing learned from:
https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/

flask-login learned from documentation: https://flask-login.readthedocs.io/
"""


@login_manager.user_loader
def load_user(user_id):
    """Reload user from user id using flask-login."""
    return models.User.query.get(user_id)


# set login_manager variables
login_manager.login_view = "/login"
login_manager.login_message_category = "alert-info"


def format_title(search):
    """Format a search to follow standard book title format."""
    lowercase = ["a", "an", "the", "but", "for", "or", "nor", "of", "at", "on",
                 "yet", "in", "and"]
    words = search.split(" ")
    words[0] = words[0].lower().capitalize()
    words[len(words)-1] = words[len(words)-1].lower().capitalize()
    for i in range(1, len(words)-1):
        words[i] = words[i].lower()
        if words[i] not in lowercase:
            words[i] = words[i].capitalize()
    return words


@app.route('/')
def index():
    """Display main feed? Change based on if user is logged in or not."""
    # If not logged in, query most recent 10 posts
    liked = []
    read = db.session.query(Book, Post, User)\
                     .join(Post, Book.id == Post.book_id)\
                     .join(User, User.id == Post.user_id)\
                     .order_by(Post.date.desc()).limit(10).all()

    if current_user.is_authenticated:
        # Posts that user has liked
        liked = models.Post.query\
                           .join(Liked,
                                 and_(Liked.post_user_id == Post.user_id,
                                      Liked.post_book_id == Post.book_id))\
                           .filter(Liked.user_id == current_user.id).all()
        # Query books that user has read
        read = db.session.query(Book, Post, User)\
                         .join(Post, Book.id == Post.book_id)\
                         .join(User, User.id == Post.user_id)\
                         .filter(Post.user_id == current_user.id)
        # Query books that people who user is following have read
        followers = models.User.query\
                               .join(Following,
                                     Following.following_id == User.id)\
                               .filter(Following.follower_id ==
                                       current_user.id)\
                               .all()
        for follower in followers:
            follower_read = db.session.query(Book, Post, User)\
                                      .join(Post, Book.id == Post.book_id)\
                                      .join(User, User.id == Post.user_id)\
                                      .filter(Post.user_id == follower.id)
            read = read.union(follower_read)
        read = read.order_by(Post.date.desc()).all()

    return render_template('feed.html', title='BookLog', liked=liked,
                           read=read)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Display and process sign up form."""
    # Redirect if user is logged in
    if current_user.is_authenticated:
        flash('Can not access sign up page when logged in.', 'alert-danger')
        return redirect('/')

    form = SignupForm()
    if form.validate_on_submit():
        # Assign date as current date
        date = datetime.datetime.now().date()
        # Encrypt password using bcrypt
        password = bcrypt.generate_password_hash(request.form['password'])\
                         .decode('utf-8')

        # Check that entered passwords match
        match = True
        if not request.form['password'] == request.form['confirm_password']:
            flash('Unsuccessful. Passwords do not match.', 'alert-danger')
            match = False

        # Check that username is unique
        unique = True
        for user in models.User.query.all():
            if (user.username == request.form['username']):
                flash('Unsuccessful. Username already taken.', 'alert-danger')
                unique = False
                break

        # Insert new user into database
        if unique and match:
            insert = models.User(first_name=request.form['first_name'],
                                 last_name=request.form['last_name'],
                                 username=request.form['username'],
                                 password=password,
                                 date_joined=date)
            db.session.add(insert)
            db.session.commit()
            flash('Sign up successful!', 'alert-success')
            return redirect('/')

    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Display and process log in form."""
    # Redirect if user is logged in
    if current_user.is_authenticated:
        flash('Can not access login page when logged in.', 'alert-danger')
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        # Check that user exists
        user = models.User.query.filter_by(username=request.form['username'])\
                                .first()
        if user is None:
            flash('Username not found.', 'alert-danger')
        # Verify password
        elif bcrypt.check_password_hash(user.password,
                                        request.form['password']):
            login_user(user, remember=form.remember.data)
            flash(f'Log in successful. Welcome {user.first_name}!',
                  'alert-success')
            return redirect('/')
        else:
            flash('Password is incorrect.', 'alert-danger')

    return render_template('login.html', title='Log In', form=form)


@app.route("/logout")
@login_required
def logout():
    """Log user out."""
    logout_user()
    flash('Logged out successfully.', 'alert-success')
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Display a user's profile."""
    # Set correct user id
    if 'view' in request.form:
        id = request.form['view']
    elif current_user.is_authenticated:
        id = current_user.id
    else:
        flash('Error accessing profile page. Redirected to main page.',
              'alert-danger')
        return redirect('/')

    # Set page title
    user = models.User.query.get(id)
    title = "@" + user.username + "'s Profile"
    liked = []
    if current_user.is_authenticated:
        # Retrieve current user's (viewer) likes
        liked = models.Post.query.join(Liked,
                                       and_(Liked.post_user_id == Post.user_id,
                                            Liked.post_book_id == Post.book_id)
                                       )\
                                .filter(Liked.user_id == current_user.id).all()
        if user.id == current_user.id:
            title = "Your Profile"

    # Retrieve user's posts
    posts = db.session.query(Book, Post, User)\
                      .join(Post, Book.id == Post.book_id)\
                      .join(User, User.id == Post.user_id)\
                      .filter(Post.user_id == id)\
                      .order_by(Post.date.desc()).all()

    # Retrieve who user is following
    followed_users = models.User.query.join(Following,
                                            Following.following_id == User.id)\
                                      .filter(Following.follower_id == id)\
                                      .all()

    # Retrieve who user is being followed by
    followed_by = models.User.query.join(Following,
                                         Following.follower_id == User.id)\
                                   .filter(Following.following_id == id).all()

    return render_template('profile.html', user=user, title=title, liked=liked,
                           posts=posts, followed_users=followed_users,
                           followed_by=followed_by)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Display and process form for editing profile details."""

    form = EditProfileForm()
    if form.validate_on_submit():

        # Check that entered passwords match
        match = True
        if not request.form['password'] == request.form['confirm_password']:
            flash('Unsuccessful. Passwords do not match.', 'alert-danger')
            match = False

        # Flag if submitted bio matches stored bio
        bio_same = False
        if current_user.bio is None and request.form['bio'] == "":
            bio_same = True
        elif current_user.bio == request.form['bio']:
            bio_same = True

        unique = True
        for user in models.User.query.all():
            if (user.username == request.form['username']
                    and user.id != current_user.id):
                flash('Unsuccessful. Username already taken.', 'alert-danger')
                unique = False
                break

        # Check that changes were made and username is unique
        if (request.form['first_name'] == current_user.first_name
                and request.form['last_name'] == current_user.last_name
                and request.form['username'] == current_user.username
                and bio_same):
            if (bcrypt.check_password_hash(current_user.password,
                                           request.form['password']) or
                    request.form['password'] == ""):
                flash('No changes detected. Profile not updated.',
                      'alert-info')
                return redirect('/profile')

        # Insert into database
        if unique and match:
            current_user.first_name = request.form['first_name']
            current_user.last_name = request.form['last_name']
            current_user.username = request.form['username']
            if request.form['password'] != "":
                current_user.password = bcrypt.generate_password_hash(
                    request.form['password']).decode('utf-8')
            if request.form['bio'] != "":
                current_user.bio = request.form['bio']
            else:
                current_user.bio = None
            db.session.commit()
            flash('Profile update successfully.', 'alert-success')
            return redirect('/profile')

    # Query user
    user = models.User.query.get(current_user.id)

    # Pre-populate form using query
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.username.data = user.username
    form.bio.data = user.bio

    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/delete_profile')
@login_required
def delete_profile():
    """Delete user's profile."""
    delete = models.User.query.get(current_user.id)
    username = delete.username
    db.session.delete(delete)
    db.session.commit()

    flash('User profile @'+ username + ' deleted successfully.',
          'alert-success')
    return redirect('/')


@app.route('/books', methods=['GET', 'POST'])
def books():
    """Search for a book."""
    # Initialize variables to pass to html page
    added_books = []
    read_books = []
    results = models.Book.query.filter_by(title="")
    msg = None
    if current_user.is_authenticated:
        added_books = models.Book.query.join(ReadingList,
                                             ReadingList.book_id == Book.id)\
                                       .filter(current_user.id
                                               == ReadingList.user_id)

        read_books = models.Book.query.join(Post, Post.book_id == Book.id)\
                                      .filter(current_user.id == Post.user_id)

    form = SearchForm()
    if form.validate_on_submit():
        words = format_title(request.form['search'])
        # Query by exact title
        results = models.Book.query.filter_by(title=" ".join(words))

        # Query by if author contains exact search term when longer than 2
        if len(request.form['search']) > 2:
            authors = models.Book.query.filter(
                      Book.author.like("%"+request.form['search']+"%"))
            results = results.union(authors).group_by(Book.id)

        # Query by if title or author contains a significant search term
        for i in range(len(words)):
            if len(words[i]) > 3:
                title = models.Book.query.filter(
                        Book.title.like("%"+words[i]+"%"))
                author = models.Book.query.filter(
                         Book.author.like("%"+words[i]+"%"))
                results = results.union(title).union(author).group_by(Book.id)

        # Create display message for search results
        msg = (str(results.count()) + " results found for '"
               + request.form['search'] + "'")
        if results.count() == 1:
            msg = msg.replace('results', 'result', 1)

    return render_template('books.html', title='Book Search', form=form,
                           added_books=added_books, read_books=read_books,
                           results=results, msg=msg)


@app.route('/book', methods=['GET', 'POST'])
def book():
    """Display a book's information and its user reviews."""
    # Retrieve book id, redirect if not set
    book_id = session.pop("book_id", None)
    if book_id is None:
        flash("Can't access page from there. Redirected to main page.",
              "alert-danger")
        return redirect("/")

    # Retrieve likes
    liked = []
    if current_user.is_authenticated:
        liked = models.Post.query.join(Liked,
                                       and_(Liked.post_user_id == Post.user_id,
                                            Liked.post_book_id == Post.book_id)
                                       )\
                                 .filter(Liked.user_id == current_user.id)\
                                 .all()

    book = models.Book.query.get(book_id)

    added_books = []
    read_books = []
    # Retrieve logged in user's reading list and finished books
    if current_user.is_authenticated:
        added_books = models.Book.query.join(ReadingList,
                                             ReadingList.book_id == Book.id)\
                                       .filter(current_user.id
                                               == ReadingList.user_id)

        read_books = models.Book.query.join(Post, Post.book_id == Book.id)\
                                      .filter(current_user.id == Post.user_id)

    # Query book's posts that have a rating or review
    posts = db.session.query(Book, Post, User)\
                      .join(Post, Book.id == Post.book_id)\
                      .join(User, User.id == Post.user_id)\
                      .filter(Post.book_id == book_id)\
                      .filter(or_(and_(Post.review is not None,
                                       Post.review != ""),
                                  and_(Post.rating is not None,
                                       Post.rating != "")
                                  )).order_by(Post.date.desc()).all()
    # Calculate average rating
    total = 0.0
    count = 0.0
    for i in range(len(posts)):
        if posts[i][1].rating is not None and posts[i][1].rating != "":
            total += posts[i][1].rating
            count += 1
    if count != 0:
        average = total / count
    else:
        average = -1

    return render_template("book.html", title=book.title, liked=liked,
                           book=book, posts=posts, added_books=added_books,
                           read_books=read_books, average=average)


@app.route('/users', methods=['GET', 'POST'])
def users():
    """Search for another user's profile."""
    # Initialize data to pass to html page
    followed_users = []
    results = models.User.query.filter_by(username="")
    msg = None

    if current_user.is_authenticated:
        following_list = models.Following.query.filter_by(
            follower_id=current_user.id)
        for user in following_list:
            followed_users.append(user.following_id)

    form = SearchForm()
    if form.validate_on_submit():

        # Strip '@' if it's the first character of search
        if request.form['search'][0] == '@':
            search = request.form['search'][1:]
        else:
            search = request.form['search']

        # Query by exact result (mainly to re-initialize results)
        results = models.User.query.filter_by(username=search)

        words = search.split(" ")
        for i in range(len(words)):

            if words[i] == "":
                break

            # Query by username
            words[i] = words[i].lower()
            unames = models.User.query.filter(User.username
                                              .like("%"+words[i]+"%"))
            usernames = models.User.query.filter_by(username=words[i])
            results = results.union(unames).union(usernames).group_by(User.id)

            # Query by if first or last names contain an exact search term
            words[i] = words[i].capitalize()
            if len(words[i]) > 1:
                fnames = models.User.query.filter(User.first_name
                                                  .like("%"+words[i]+"%"))
                lnames = models.User.query.filter(User.last_name
                                                  .like("%"+words[i]+"%"))
                results = results.union(fnames).union(lnames).group_by(User.id)

        # Create display message for search results
        msg = (str(results.count()) + " results found for '"
               + request.form['search'] + "'")
        if results.count() == 1:
            msg = msg.replace('results', 'result', 1)

    return render_template('users.html', title='User Search', form=form,
                           followed_users=followed_users, results=results,
                           msg=msg)


@app.route('/edit_following', methods=['GET', 'POST'])
@login_required
def edit_following():
    """Follow/unfollow other users."""
    # Parse the JSON data included in the request
    data = json.loads(request.data)
    user_id = int(data.get('id')[-1])

    # Check is button is clicked on user's own profile
    own_profile = False
    if data.get('other') is None:
        own_profile = True

    action = data.get('action')

    # Follow or unfollow user
    if action == "follow":
        insert = models.Following(follower_id=current_user.id,
                                  following_id=user_id)
        db.session.add(insert)
    else:
        delete = models.Following.query.get((current_user.id, user_id))
        db.session.delete(delete)

    db.session.commit()
    user = models.User.query.get(user_id)
    username = user.username

    return json.dumps({'status': 'OK', 'id': str(user_id),
                       'own_profile': own_profile, 'username': username})


@app.route('/edit_reading_list', methods=['GET', 'POST'])
@login_required
def edit_reading_list():
    """Add book to user's reading list."""
    data = json.loads(request.data)
    book_id = int(data.get('id'))
    action = data.get('action')

    # Add or remove book to user's reading list
    if action == "add":
        insert = models.ReadingList(user_id=current_user.id, book_id=book_id)
        db.session.add(insert)
    else:
        delete = models.ReadingList.query.get((current_user.id, book_id))
        db.session.delete(delete)

    db.session.commit()
    book = models.Book.query.get(book_id)
    title = book.title

    return json.dumps({'status': 'OK', 'id': str(book_id), 'title': title})


@app.route('/reading_list')
@login_required
def reading_list():
    """Display user's reading list."""
    # Query reading list
    reading_list = models.Book.query\
                              .join(ReadingList)\
                              .filter(ReadingList.book_id == Book.id,
                                      ReadingList.user_id == current_user.id)

    # Query read books
    read_books = models.Book.query\
                            .join(Post, Post.book_id == Book.id)\
                            .filter(current_user.id == Post.user_id)

    return render_template('/reading_list.html', title='Reading List',
                           reading_list=reading_list, read_books=read_books)


@app.route('/other_profile')
def other_profile():
    """Display another user's profile."""
    # Retrieve user
    user = models.User.query.get(id)

    # Retrieve who user is following
    followed_users = models.User.query\
                                .join(Following,
                                      Following.following_id == User.id)\
                                .filter(Following.follower_id ==
                                        current_user.id)\
                                .all()

    # Retrieve who user is being followed by
    followed_by = models.User.query\
                             .join(Following,
                                   Following.follower_id == User.id)\
                             .filter(Following.following_id ==
                                     current_user.id)\
                             .all()

    return render_template('profile.html', title=user.username+"'s Profile",
                           followed_users=followed_users,
                           followed_by=followed_by)


@app.route('/post_book', methods=['GET', 'POST'])
@login_required
def post_book():
    """Mark book as read and create post."""
    data = json.loads(request.data)
    book_id = int(data.get('id')[5:])
    date = datetime.datetime.now()

    # Mark book as read
    insert = models.Post(user_id=current_user.id, book_id=book_id, date=date,
                         likes=0)
    db.session.add(insert)
    db.session.commit()

    book = models.Book.query.get(book_id)
    title = book.title

    return json.dumps({'status': 'OK', 'id': str(book_id), 'title': title})


@app.route('/delete_book', methods=['GET', 'POST'])
@login_required
def delete_book():
    """Unmark book as read and delete post."""
    data = json.loads(request.data)
    book_id = int(data.get('id'))

    # Delete book from Post
    delete = models.Post.query.get([current_user.id, book_id])

    # Delete any likes associated with the post
    delete_likes = models.Liked.query\
                               .filter(and_(Liked.post_user_id ==
                                            delete.user_id,
                                            Liked.post_book_id ==
                                            delete.book_id)
                                       )\
                               .all()
    if len(delete_likes) > 0:
        for like in delete_likes:
            db.session.delete(like)

    db.session.delete(delete)
    db.session.commit()

    book = models.Book.query.get(book_id)

    alert = ("Successfully removed '"
             + book.title
             + "' from finished books and deleted post."
             + " Click 'OK' to redirect to main page.")
    return json.dumps({'status': 'OK', 'alert': alert})


@app.route('/like_post', methods=['GET', 'POST'])
@login_required
def like_post():
    """Like/unlike post."""
    data = json.loads(request.data)
    ids = data.get('id').split("-")
    post_user_id = int(ids[0])
    post_book_id = int(ids[1])
    post = models.Post.query.get([post_user_id, post_book_id])

    if data.get('action') == "like":
        # Add to user's liked posts and increment likes
        insert = models.Liked(user_id=current_user.id,
                              post_user_id=post_user_id,
                              post_book_id=post_book_id)
        post.likes += 1
        db.session.add(insert)
    else:
        # Remove from user's liked posts and decrement likes
        delete = models.Liked.query.get([current_user.id,
                                         post_user_id,
                                         post_book_id])
        post.likes -= 1
        db.session.delete(delete)

    db.session.commit()

    return json.dumps({'status': 'OK', 'id': data.get('id'),
                       'action': data.get('action')})


@app.route('/pass_book_id', methods=['GET', 'POST'])
def pass_book_id():
    """Pass book id to edit_post or book."""
    retrieve = request.form.get('book-id', None)

    # Redirect if not a valid request
    if retrieve is None:
        flash("Can't access page from there. Redirected to main page.",
              "alert-danger")
        return redirect("/")

    # Split retrieved id
    info = retrieve.split("-")
    session['book_id'] = int(info[1])

    # Redirect to correct page
    if info[0] == "e":
        return redirect('/edit_post')
    else:
        return redirect('/book')


@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    """Edit a post."""
    # Retrieve book id, redirect if not set
    book_id = session.pop("book_id", None)
    if book_id is None:
        flash("Can't access page from there. Redirected to main page.",
              "alert-danger")
        return redirect("/")

    # Set book id again, so that page does not redirect on form submission
    session['book_id'] = book_id

    post = models.Post.query.get([current_user.id, book_id])
    book = models.Book.query.get(book_id)

    # Update post
    form = PostForm()
    if form.validate_on_submit():
        post.rating = request.form['rating']

        post.review = request.form['review']

        db.session.commit()
        session.pop("book_id", None)
        flash("Successfully updated post!", "alert-success")
        return redirect('/')

    # Pre-populate form
    form.rating.data = post.rating
    form.review.data = post.review

    return render_template('/edit_post.html',
                           title="Edit Post for '" + book.title + "'",
                           form=form, book_id=book.id)
