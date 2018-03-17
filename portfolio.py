from flask import Flask, redirect, request, url_for, render_template, session
import sqlite3

app = Flask(__name__,static_url_path="",static_folder='static');
DATABASE = 'myDB'
db = sqlite3.connect(DATABASE)

#function to insert into guestbook
def _insert(name,email,message):
    params= {'name':name,'email':email,'message':message}
    cur = db.cursor()
    cur.execute("INSERT INTO Guestbook(name,email,message) VALUES(:name,:email,:message)",params)
    db.commit()
    cur.close()

#function to insert comments
def _insert1(comment,photoId,uid):
    params = {'comment':comment,'photoId':photoId,'uid':uid}
    cur = db.cursor()
    cur.execute("INSERT INTO Comment(comment,photoId,uid) VALUES(:comment,:photoId,:uid)",params)
    db.commit()
    cur.close()

#function to insert user data during registration
def _insert2(username,email,password):
    params = {'username':username,'email':email,'password':password}
    cur = db.cursor()
    cur.execute("INSERT INTO User(username,email,password) VALUES(:username,:email,:password)",params)
    print("the query worked!")
    db.commit()
    cur.close()

#app route for the homepage
@app.route('/')
def homepage():
    if session.get('UserName'):
        return render_template('index.html',username=session['UserName'],uid = session['uid'])
    else:
        return render_template('index.html',uid=0)

#app route for the list of pictures
@app.route('/list')
def list():
    pid = request.args.get("id")
    query1 = "SELECT * FROM Photo WHERE categoryId = " + str(pid)
    cur = db.execute(query1)
    rv1 = cur.fetchall()
    query2 = "SELECT * FROM Category WHERE categoryId =" + str(pid)
    cur = db.execute(query2);
    rv2 = cur.fetchall()
    cur.close()
    if session.get('UserName'):
        return render_template('list.html',entries=rv1,name=rv2[0],username=session['UserName'],uid=session['uid'])
    else:
        return render_template('list.html',entries=rv1,name=rv2[0],uid=0)

#app route for the about page
@app.route('/about')
def about():
    if session.get('UserName'):
        return render_template('about.html',username=session['UserName'],uid = session['uid'])
    else:
        return render_template('about.html',uid=0)

#app route for the guestbook
@app.route('/guestbook')
def gbook():
    query = "SELECT * FROM Guestbook"
    cur = db.execute(query)
    rv = cur.fetchall()
    cur.close()
    if session.get('UserName'):
        return render_template('guestbook.html',rv=rv,username=session['UserName'],uid=session['uid'])
    else:
        return render_template('guestbook.html',rv=rv,uid=0)

#app route to add message in the guestbook
@app.route('/add', methods=['POST'])
def add():
    _insert(request.form['name'],request.form['email'],request.form['message'])
    return redirect(url_for('gbook'))

#app route for the Search
@app.route('/search',methods={'POST','GET'})
def search():
    if request.method == 'POST':
        search = request.form['search']
        query = "SELECT * FROM Photo WHERE (photoName LIKE \'%"+ search + "%\') OR (photoDesc LIKE \'%" + search + "%\')"
        print(query)
        cur = db.execute(query)
        rv = cur.fetchall()
        cur.close()
        if session.get('UserName'):
            return render_template('search.html',rv=rv,username=session['UserName'],uid=session['uid'])
        else:
            return render_template('search.html',uid=0,rv=rv)
    else:
        if session.get('UserName'):
            return render_template('search.html',username=session['UserName'],uid=session['uid'])
        else:
            return render_template('search.html',uid=0)

#app route for the single product page
@app.route('/product',methods={'POST','GET'})
def product():
    pid = request.args.get("pid")
    cid = request.args.get("id")
    if request.method == 'POST':
        _insert1(request.form['comment'],pid,session['uid'])
        return redirect(request.url)
    else:
        query1 = "SELECT * FROM Photo WHERE photoId =" + str(pid)
        cur = db.execute(query1)
        rv1 = cur.fetchall()
        query2 = "SELECT * FROM Category WHERE categoryId =" + str(cid)
        cur = db.execute(query2)
        rv2 = cur.fetchall()
        query3 = "SELECT username,comment,photoId FROM Comment INNER JOIN User ON User.uid = Comment.uid WHERE photoId =" + str(pid)
        cur = db.execute(query3)
        rv3 = cur.fetchall()
        cur.close()
        if session.get("UserName"):
            return render_template('product.html',photos = rv1[0] ,name = rv2[0], comments = rv3,username = session['UserName'],uid=session['uid'])
        else:
            return render_template('product.html',photos = rv1[0] ,name = rv2[0], comments = rv3,uid=0)

#app route for the login page
@app.route('/login',methods={'GET','POST'})
def login():
    if request.method == 'POST':
        query = "SELECT * FROM User WHERE username = \'" + request.form['UserName'] + "\'"
        query = query + " AND password= \'" + request.form['Password'] + "\'"
        cur = db.execute(query)
        rv = cur.fetchall()
        cur.close()
        if len(rv)==1:
            session['UserName'] = request.form['UserName']
            session['uid'] = rv[0][0]
            return redirect(url_for('homepage'))
        else:
            return render_template('signin.html')
    else:
        return render_template('signin.html')

#app route for adding a user
@app.route('/addUser',methods={'POST'})
def adduser():
    _insert2(request.form['Username'],request.form['Email'],request.form['Password'])
    return redirect(url_for('login'))

#app route for the register page
@app.route('/register')
def register():
    return render_template('register.html')

#app route for the logout
@app.route('/logout')
def logout():
    session.pop('UserName',None)
    return redirect(url_for('homepage'))

#secret key for the session
app.secret_key = "secret_key7712"
