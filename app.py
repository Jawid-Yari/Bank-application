from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_security import roles_accepted, auth_required, logout_user
import os
from model import db, seedData, Customer, Account, Transaction

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hej123@localhost/starbank'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'Kp10kHudawanDa594-2ToBiaEnji-9OnAchoRaNaraFt')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
db.app = app
db.init_app(app)
migrate = Migrate(app,db)






# @app.route("/")
# def login():
#     return render_template(
#         "login.html",
#         redirect = "/customers"
#     )

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


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
@auth_required()
@roles_accepted("Admin", "Cashier")
def customers():
    accounts = Account.query.all()
    sortColumn=request.args.get('sortColumn', 'id')
    sortOrder=request.args.get('sortOrder', 'asc')
    list_of_customers=Customer.query
    q = request.args.get('q', '')
    page =int(request.args.get('page', 1))

    list_of_customers = Customer.query
    list_of_customers= list_of_customers.filter(
         Customer.GivenName.like('%' + q + '%') |
                                Customer.City.like('%' + q + '%')|
                                                Customer.Surname.like('%' + q + '%')|
                                                                    Customer.Id.like('%' + q + '%')|
                                                                                        Customer.Country.like('%' + q + '%')|
                                                                                                            Customer.City.like('%' + q + '%')
                                                                                                                        

    )
    if sortColumn=='id':
        if sortOrder =='asc':
            list_of_customers=list_of_customers.order_by(Customer.Id.asc())
        else:
            list_of_customers=list_of_customers.order_by(Customer.Id.desc())

    if sortColumn=='name':
        if sortOrder=='asc':
            list_of_customers=list_of_customers.order_by(Customer.Surname.asc())
        else:
            list_of_customers=list_of_customers.order_by(Customer.Surname.desc())
        
    if sortColumn=='givenName':
        if sortOrder=='asc':
            list_of_customers=list_of_customers.order_by(Customer.GivenName.asc())
        else:
            list_of_customers=list_of_customers.order_by(Customer.GivenName.desc())

    if sortColumn=='country':
        if sortOrder=='asc':
            list_of_customers=list_of_customers.order_by(Customer.Country.asc())
        else:
            list_of_customers=list_of_customers.order_by(Customer.Country.desc())

    if sortColumn=='city':
        if sortOrder=='asc':
            list_of_customers=list_of_customers.order_by(Customer.City.asc())
        else:
            list_of_customers=list_of_customers.order_by(Customer.City.desc())
        
    paginationObject=list_of_customers.paginate(page = page,per_page=50, error_out = False)

    return render_template("customers.html",
                            list_of_customers=paginationObject,
                            activePage="customers_page",
                            pages = paginationObject.pages,
                            page =page,
                            sortColumn=sortColumn,
                            sortOrder = sortOrder,
                            has_prev=paginationObject.has_prev,
                            has_next=paginationObject.has_next,
                            redirect="/customres",
                            q=q
                            )


@app.route("/customer/<int:customer_id>")
def customer(customer_id):
    customer = db.session.query(Customer).filter(Customer.Id == customer_id).first()
    accounts = db.session.query(Account).filter(Account.CustomerId == customer_id).all()
    total_balance = sum([account.Balance for account in accounts])
    return render_template("customer_profile.html",
                           customer = customer,
                           accounts = accounts,
                           total_balance = total_balance,
                           redirect = "/customer",
                           activePage = 'profile'
                            )

@app.route("/transaction/<int:account_id>")
def transactions(account_id):
    transactions = db.session.query(Transaction).filter(Transaction.AccountId == account_id).all()
    account = db.session.query(Account).filter(Account.Id == account_id).first()
    return render_template("transactions.html",
                           transactions= transactions,
                           account = account,
                           redirect="/transaction",
                           activePage = 'transaction'

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
        seedData(app,db)
        app.run(debug=True)
        

