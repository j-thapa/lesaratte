import os,requests,random

#class of Books to store object with attributes from data of googlebooks API and provided csv file

class Book:
    def __init__(self,title,author,category,image,year,isbn):

        self.title=title
        self.author=author
        self.image=image
        self.year=year
        self.isbn=isbn
        self.category=category


# all necessary libraries
from flask import Flask, session, render_template ,request,flash ,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"),pool_size=20, max_overflow=0)
db = scoped_session(sessionmaker(bind=engine))

# default value of the logged session
logged=None








#root route
@app.route("/")
def index():

     return render_template("index.html")


#route for sign up page

@app.route("/signedup", methods=["POST","GET"])
def signedup():

    if request.method == "POST":


        userid = request.form.get("userid")
        password = request.form.get("password")
        email = request.form.get("email")
        length2=len(userid)
        length1=len(password)
        if length1 > 6 and length2 > 6 :



            if db.execute("SELECT * FROM users WHERE  email= :email" , { "email":email}).rowcount == 0:
                if db.execute("SELECT * FROM users WHERE  userid= :name" , { "name":userid}).rowcount == 0:


                    db.execute("INSERT INTO users (userid, password, email) VALUES (:name, :password ,:email)",
                              {"name": userid, "password": password , "email": email})
                    db.commit()
                    flash("Your account is created . Please log in ", 1)
                else:


                    flash("user id is not available ")
            else:

                flash(" email is already on use")
        else:
            flash("userid and password should be at least six characters")




    return render_template("signup.html")





#route for log in page

@app.route("/signedin",methods=["POST","GET"])
def signedin():
    if request.method == "POST":

        user = request.form.get("user")
        passw = request.form.get("pass")



        if db.execute("SELECT * FROM users WHERE userid = :name and password= :passw", {"name": user, "passw":passw}).rowcount == 0:



            flash("Incorrect email or password")
            return home()
        else:
            session['user']=user
            global logged
            logged=session['user']
            return home()
    else:
         return render_template("index.html")

#rout for signing out
@app.route("/signout",methods=["POST","GET"])
def signout():
    logged=None
    return render_template('index.html')


#route for home page
@app.route("/home",methods=["POST","GET"])
def home():

    if logged is None:

        return render_template("index.html")
    else:
        #create a grid of six book object randomly for display in home page
        books_list=[]




        for i in range(6):





            num=random.randrange(000, 999)
            term = f"%{num}%"
            dis = db.execute("SELECT * FROM books WHERE isbn LIKE :term ;", {"term": term}).fetchone()
            title=dis.title
            isbn=dis.isbn
            author=dis.author
            year=dis.year

            try:

                res = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{dis.isbn}")
                google=res.json()

                categories=google['items'][0]['volumeInfo']['categories'][0]
                category=categories
                image=google['items'][0]['volumeInfo']['imageLinks']['thumbnail']
                image=image
                book1=Book(title,author,category,image,year,isbn)

                books_list.append(book1)

            except:
                description="Not Available"
                categories="Not Available"
                category=categories
                image="https://perfectlytolerable.files.wordpress.com/2019/03/blank-book-cover-e1551822897834.jpg"
                book1=image
                book1=Book(title,author,category,image,year,isbn)
                books_list.append(book1)



        return render_template("home.html", dis=books_list)


#route for search bar ; can search books usinh ISBN, date , title and author from database
@app.route("/search",methods=["POST","GET"])
def search():

    if logged is None:

        return render_template("index.html")
    else:
        result=request.form.get("result")
        term = f"%{result}%".upper()

        books = db.execute("SELECT * FROM books WHERE isbn LIKE :term OR UPPER(title) LIKE :term OR UPPER(author) LIKE :term LIMIT 40;", {"term": term}).fetchall()
        return render_template('search_results.html', books=books)

#route for book details , display details of book from data obtained in database , goodread API and googlebooks API

@app.route("/search/<string:book_isbn>",methods=["GET", "POST"])
def book(book_isbn):
    if logged is None:

        return render_template("index.html")
    else:


        if request.method == "POST":
            userid=logged
            isbn=book_isbn
            comments = request.form.get("comments")
            rating = request.form.get("inlineRadioOptions")
            previous_review = db.execute("SELECT * FROM reviews WHERE isbn = :id AND userid= :userid ", {"id": book_isbn, "userid":logged}).fetchone()
            if previous_review is None:

                db.execute("INSERT INTO reviews (userid, isbn, comments, rating) VALUES (:userid, :isbn, :comments ,:rating)",
                      {"userid": userid, "isbn": isbn, "comments":comments, "rating":rating})
                db.commit()
            else:
                flash(' error already commented')


        book = db.execute("SELECT * FROM books WHERE isbn = :id", {"id": book_isbn}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1uUqGfvQqH8149G1Up3g", "isbns": book_isbn })
        goodrd=res.json()
        goodrating=goodrd['books'][0]['average_rating']
        goodcount=goodrd['books'][0]['work_ratings_count']

        try:

            res = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{book_isbn}")
            google=res.json()
            description=google['items'][0]['volumeInfo']['description']
            categories=google['items'][0]['volumeInfo']['categories'][0]
            image=google['items'][0]['volumeInfo']['imageLinks']['thumbnail']

        except:
            description="Not Available"
            categories="Not Available"
            image="https://perfectlytolerable.files.wordpress.com/2019/03/blank-book-cover-e1551822897834.jpg"




        review=db.execute("SELECT * FROM reviews WHERE isbn = :id", {"id": book_isbn}).fetchall()
        if book is None:
            return ("No such book.")
        else:





            return render_template("bookdetails.html", book=book, reviews=review ,goodrating=goodrating,goodcount=goodcount, description=description,
            categories=categories,images=image )

#route to search books using their author or year provided in search list

@app.route("/searchnext/<string:book_a>",methods=["GET", "POST"])
def book_search(book_a):
    if logged is None:

        return render_template("index.html")
    else:
        books = db.execute("SELECT * FROM books WHERE author=:book_ OR year=:book_  LIMIT 40;", {"book_": book_a}).fetchall()
        return render_template('search_results.html', books=books)

# route to display logged in user profile Details

@app.route("/profile", methods=["POST","GET"])
def profile():
    if logged is None:

        return render_template("index.html")
    else:

        review=db.execute("SELECT * FROM reviews WHERE userid= :userid  ORDER BY review_id DESC LIMIT 2 ; ", {"userid":logged}).fetchall()
        user=db.execute("SELECT * FROM users WHERE userid= :userid ;", {"userid":logged}).fetchone()


    return render_template('profile.html',review=review , user=user)

#route to dispaly info about the website


@app.route("/about", methods=["POST","GET"])
def about():
    if logged is None:


        return render_template("index.html")
    else:
        return render_template("about.html")

#route for api which send json of book details and review details from database matching to the requested isbn number


@app.route("/api/<string:book_isbn>")
def book_api(book_isbn):
    book_isbn=book_isbn

    book = db.execute("SELECT * FROM books WHERE isbn = :id", {"id": book_isbn}).fetchone()

    if book is None:
        return("404 : Error the book is not in the database")
    else:

        read=db.execute("select * from reviews where isbn = :book_isbn;",{"book_isbn":book_isbn}).fetchall()
        rateint=[]

        for r in read:

            rate=r.rating.split()
            l=len(rate)
            rateint.append(l)


        ratingsum=sum(rateint)
        number_rating=len(rateint)
        try:




            avg_rating=ratingsum/number_rating

            return jsonify({
                "title": book.title,
                "author":book.author,
                "year": book.year,
                "isbn": book.isbn,
                "review_count":number_rating,
                "average_score": avg_rating

            })

        except:

            avg_rating=0
            return jsonify({
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "isbn": book.isbn,
                "review_count": number_rating,
                "average_score": avg_rating

            })
