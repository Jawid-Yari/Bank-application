from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData, Customer, Account

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hej123@localhost/BankData'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
 
 

# @app.route("/")
# def startpage():
#     trendingCategories = Category.query.all()
#     return render_template("index.html", trendingCategories=trendingCategories)

@app.route("/")
def home():
    account = Account.query.filter(Account.Balance)
    balance = 0
    for a in account:
        balance +=a.Balance

    return render_template("home.html",
                            number_of_accounts= Account.query.count(),
                            number_of_customers = Customer.query.count(),
                            total_balance = balance,
                            redirect="/",
                            activePage = "home_page"
                            )
    



@app.route("/customers")
def customers():
    customers = Customer.query.all()
    accounts = Account.query.all()
    # for a in accounts:
    #     if 
    # balance = Account.query.filter_by(CustomerId=customers.Id)
    # current_balance =0

    return render_template("customers.html",
                            customers = customers,
                            redirect= "customres",
                            activePage="customers_page"
                            )

@app.route("/customer/<id>")
def customer(id):
    customer = Customer.query.filter_by(Id = id).first()
    return render_template("customer.html"
                            )


@app.route("/category/<id>")
def category(id):
    products = Product.query.all()
    return render_template("category.html", products=products
                            
            )

@app.route("/tables")
def tables():
    return render_template("tables.html")

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seedData(db)
        app.run(debug=True)
        

