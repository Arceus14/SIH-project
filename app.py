import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    portfolio=[]
    ts_value=0
    bal = 10000

    if len(db.execute("SELECT * FROM users")) > 0:
        if len(db.execute("SELECT name FROM sqlite_master WHERE type='table'"))>1:
            if len(db.execute("SELECT * FROM ?", ("transactions_" + str(session["user_id"])))) > 0:
                portfolio = db.execute("SELECT * FROM ?",("stocks_owned_" + str(session["user_id"])))
                for each in portfolio:
                    print("printting below")
                    print(each['stock_symbol'])
                    print(each['stock_quantity'])
                    print(each['current_value'])
                    print(each['e_value'])
                    print("printting below")
                    print(each)


                    each['e_value'] = lookup(each['stock_symbol'])['price']
                    each['current_value'] = each['e_value'] * (each['stock_quantity'])
                    db.execute("UPDATE ? SET current_value=?,e_value=? WHERE stock_symbol=?",("stocks_owned_" + str(session["user_id"])),each['current_value'],each['e_value'],(each['stock_symbol']))

                portfolio = db.execute("SELECT * FROM ?",("stocks_owned_" + str(session["user_id"])))

                ts_value = db.execute("SELECT SUM(current_value) AS ts_value FROM ?",("stocks_owned_" + str(session["user_id"])))[0]['ts_value']
                bal = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
                ts_value += bal
                return render_template("index.html",id=session["user_id"],portfolio=portfolio,ts_value=ts_value,bal=bal)

    return render_template("index.html",id=session["user_id"],portfolio=[],bal=bal,ts_value=ts_value)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quantity = request.form.get("shares")
        s_quantity = quantity
        try:
            int(quantity)
        except ValueError:
            return apology("Enter a natural number")

        quantity = int(quantity)
        if not symbol:
            return apology("Enter Stock Symbol")

        if not lookup(symbol):
            return apology("Enter Valid Stock Symbol")

        if not quantity:
            return apology("Enter Number of stocks to purchase")
        if  ( quantity < 0 ) or (str(s_quantity) != str(quantity)):
            return apology("Enter a natural number!!! HATT")

        bal = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
        print("PRINT BELOW")

        price = (lookup(symbol)['price']) * quantity
        print(price)
        print(quantity)
        print("PRINT abouve")
        if price > bal:
            return apology("Insufficient Balance, You are ? $ short",((lookup(symbol)['price']) * quantity) - bal)
        else:
            db.execute("UPDATE users SET cash=? WHERE id=?",bal-price,session["user_id"])
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()

        db.execute("INSERT INTO ? VALUES(?,?,?,?,?,?)",("transactions_" + str(session["user_id"])), symbol, quantity, "BUY",current_date,current_time,price)

        #add stock if new to portfolio else update current
        stock_check = len(db.execute("SELECT stock_symbol FROM ? WHERE stock_symbol= ?",("stocks_owned_" + str(session["user_id"])),symbol))
        if(stock_check != 1):
            #add new company stock to portfolio
            db.execute("INSERT INTO ? VALUES(?,?,?,?)",("stocks_owned_" + str(session["user_id"])), symbol,(lookup(symbol)['price']), quantity, price)
        else:
            #update: add stocks to portfolio
            print("PRINT it \n\n\n\n\n\n\n\n\n\nn\n\n")
            print(db.execute("SELECT stock_quantity FROM ? WHERE stock_symbol = ?",("stocks_owned_" + str(session["user_id"])),symbol)[0]['stock_quantity'])
            updated_quantity = quantity + db.execute("SELECT stock_quantity FROM ? WHERE stock_symbol = ?",("stocks_owned_" + str(session["user_id"])),symbol)[0]['stock_quantity']
            print("updated quantty")
            print(updated_quantity)
            updated_value = ((lookup(symbol)['price']) * updated_quantity)
            db.execute("UPDATE ? SET stock_quantity=?, current_value=?, e_value=? WHERE stock_symbol=?", ("stocks_owned_" + str(session["user_id"])), updated_quantity, updated_value,(lookup(symbol)['price']),symbol)

        return redirect("/")


    else:
        return render_template("buy.html")





@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM ?",("transactions_" + str(session["user_id"])))

    return render_template("history.html",history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method=="POST":

        if not request.form.get("symbol"):
            return apology("Enter a Stock Symbol")
        if not lookup(request.form.get("symbol")):
            return apology("Enter a Valid Stock Symbol")
        else:
            list = lookup(request.form.get("symbol"))
        print("LIST BELOW")
        print(list)
        return render_template("quoted.html",list=list)

    else:
        return render_template("quote.html",list=[])



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Enter name")
        name_check = db.execute("SELECT * FROM users WHERE username = ?",request.form.get("username"))
        if len(name_check)!=0:
            return apology("Username taken! Enter a different one")
        if not request.form.get("password"):
            return apology("Enter password")
        if not request.form.get("confirmation"):
            return apology("Enter same password")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords dont match!")



        name = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        index = len(db.execute("SELECT * FROM users ")) + 1
        session["user_id"] = index
        db.execute("INSERT INTO users(id, username, hash) VALUES (?,?,?)",index,name,password)

        db.execute("CREATE TABLE ? (stock_symbol TEXT NOT NULL, stock_quantity INTEGER, transaction_type TEXT NOT NULL,transaction_date DATE,transaction_time TEXT,transaction_value INTEGER)",("transactions_" + str(session["user_id"])))
        db.execute("CREATE TABLE ? (stock_symbol TEXT UNIQUE NOT NULL,e_value INTEGER, stock_quantity INTEGER, current_value REAL)",("stocks_owned_" + str(session["user_id"])))
        return redirect("/")

    else :
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        quantity = request.form.get("shares")
        s_quantity = quantity
        try:
            int(quantity)
        except ValueError:
            return apology("Enter a natural number")
        quantity = int(quantity)

        if not symbol:
            return apology("Enter Stock Symbol")

        if not lookup(symbol):
            return apology("Enter Valid Stock Symbol")

        if not quantity:
            return apology("Enter Number of stocks to purchase")
        if  ( quantity < 0 ) or (str(s_quantity) != str(quantity)):
            return apology("Enter a natural number!!! HATT")

        avail_quantity =  (db.execute("SELECT stock_quantity FROM ? WHERE stock_symbol= ?",("stocks_owned_" + str(session["user_id"])),symbol))[0]['stock_quantity']
        avail_quantity = int(avail_quantity)
        bal = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
        print(f"Ball \n\n\n\n\n\n\n\n{bal}")
        print("PRINT BELOW")
        price = (lookup(symbol)['price']) * quantity
        if quantity > avail_quantity:
            return apology("Insufficient Balance !!!")
        else:

            db.execute("UPDATE users SET cash=? WHERE id=?",bal+price,session["user_id"])





        now = datetime.now()
        current_date = now.date()
        current_time = now.time()

        db.execute("INSERT INTO ? VALUES(?,?,?,?,?,?)",("transactions_" + str(session["user_id"])), symbol, quantity, "SELL",current_date,current_time,price)

        #add stock if new to portfolio else update current
        stock_check = len(db.execute("SELECT stock_symbol FROM ? WHERE stock_symbol= ?",("stocks_owned_" + str(session["user_id"])),symbol))
        if(stock_check != 1):
            #add new company stock to portfolio
            db.execute("INSERT INTO ? VALUES(?,?,?)",("stocks_owned_" + str(session["user_id"])), symbol, quantity, price)
        else:
            #update: add stocks to portfolio
            updated_quantity = avail_quantity - quantity
            updated_value = bal + price
            db.execute("UPDATE ? SET stock_quantity=?, current_value=? WHERE stock_symbol=?", ("stocks_owned_" + str(session["user_id"])), updated_quantity, updated_value,symbol)

        return redirect("/")


    else:
        list = db.execute("SELECT stock_symbol FROM ?",("stocks_owned_" + str(session["user_id"])))

        return render_template("sell.html" ,list=list)



@app.route("/change", methods=["GET", "POST"])
def change():
    """Register user"""
    if request.method == "POST":
        
        if not request.form.get("password"):
            return apology("Enter password")
        if not request.form.get("confirmation"):
            return apology("Enter same password")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords dont match!")




        n_password = generate_password_hash(request.form.get("password"))
        index = session["user_id"]

        db.execute("UPDATE users SET hash=? WHERE id=?",n_password,index)

        return redirect("/")

    else :
        return render_template("change.html")
