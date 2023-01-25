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
            list_of_customers=Customer.query.order_by(Customer.Id.asc())
        else:
            list_of_customers=Customer.query.order_by(Customer.Id.desc())

    if sortColumn=='name':
        if sortOrder=='asc':
            list_of_customers=Customer.query.order_by(Customer.Surname.asc())
        else:
            list_of_customers=Customer.query.order_by(Customer.Surname.desc())
        
    if sortColumn=='givenName':
        if sortOrder=='asc':
            list_of_customers=Customer.query.order_by(Customer.GivenName.asc())
        else:
            list_of_customers=Customer.query.order_by(Customer.GivenName.desc())

    if sortColumn=='country':
        if sortOrder=='asc':
            list_of_customers=Customer.query.order_by(Customer.Country.asc())
        else:
            list_of_customers=Customer.query.order_by(Customer.Country.desc())

    if sortColumn=='city':
        if sortOrder=='asc':
            list_of_customers=Customer.query.order_by(Customer.City.asc())
        else:
            list_of_customers=Customer.query.order_by(Customer.City.desc())
        
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
        

