from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData, Customer, Account

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hej123@localhost/StarBank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
 
 

# @app.route("/")
# def startpage():
#     trendingCategories = Category.query.all()
#     return render_template("index.html", trendingCategories=trendingCategories)

#-------------------------
#from chatgdp
# @app.route('/')
# def home():
#     # kod för att hämta statistik om antalet kunder, antalet konton och summan av saldot på konton
#     return render_template('home.html', customers=customers, accounts=accounts, total_balance=total_balance)

# @app.route('/customer/<int:customer_id>')
# def customer_view(customer_id):
#     customer = db.session.query(Customer).filter(Customer.id == customer_id).first()
#     accounts = db.session.query(Account).filter(Account.customer_id == customer_id).all()
#     total_balance = sum([account.balance for account in accounts])
#     return render_template('customer.html', customer=customer, accounts=accounts, total_balance=total_balance)

# @app.route('/account/<int:account_number>')
# def account_view(account_number):
#     account = db.session.query(Account).filter(Account.number == account_number).first()
#     transactions = db.session.query(Transaction).filter(Transaction.account_number == account_number).all()
#     return render_template('account.html', account=account, transactions=transactions)


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
    accounts = Account.query.all()
    # for a in accounts:
    #     if 
    # balance = Account.query.filter_by(CustomerId=customers.Id)
    # current_balance =0
    
    
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
                            redirect= "/customres",
                            q=q
                            )

# @app.route('/customer/<int:customer_id>')
# def customer_view(customer_id):
#     customer = db.session.query(Customer).filter(Customer.id == customer_id).first()
#     accounts = db.session.query(Account).filter(Account.customer_id == customer_id).all()
#     total_balance = sum([account.balance for account in accounts])
#     return render_template('customer.html', customer=customer, accounts=accounts, total_balance=total_balance)


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
        

