from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_security import roles_accepted, auth_required, logout_user
import os
from model import db, seedData, Customer, Account, Transaction
from deposit_forms import deposit_form
from withdrawal_form import withdrawal_form
from authenticcation_form import authentication_form

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hej123@localhost/starbank'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'Kp10kHudawanDa594-2ToBiaEnji-9OnAchoRaNaraFt')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
db.app = app
db.init_app(app)
migrate = Migrate(app,db)





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
    if sortColumn=='phone':
        if sortOrder=='asc':
            list_of_customers = list_of_customers.order_by(Customer.Telephone.asc())
        else:
            list_of_customers= list_of_customers.order_by(Customer.Telephone.desc())
        
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
@auth_required()
@roles_accepted("Admin", "Cashier")
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

@app.route("/account-history/<int:account_id>")
@auth_required()
@roles_accepted("Admin", "Cashier")
def transactions(account_id):
    transactions = db.session.query(Transaction).filter(Transaction.AccountId == account_id).all()
    account = db.session.query(Account).filter(Account.Id == account_id).first()
    return render_template("account-history.html",
                           transactions= transactions,
                           account = account,
                           redirect="/account-history",
                           activePage = 'account-history'

                            )




@app.route("/authentication",  methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin", "Cashier")
def get_nationl_id():
    form = authentication_form()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(NationalId=form.nationalId.data).first()
        if customer:
            session['customer_id']= customer.Id
            if form.transaction_type.data == "deposit":
                return redirect("/deposit")
            elif form.transaction_type.data == "withdraw":
                return redirect("/withdraw")
            elif form.transaction_type.data == "transfer":
                return redirect("/transfer")
            else:
                flash('Invalid choice', 'danger')
                return redirect('/authentication')
        else:
            flash('Customer not found', 'error')
            return redirect('/authentication')
            
    return render_template("authentication.html",
                            form = form
                            
                        )


@app.route("/deposit",  methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin", "Cashier")
def deposit():
    form = deposit_form()
    customer_id = session.get('customer_id')
    if customer_id:
        accounts = db.session.query(Account).filter(Account.CustomerId == customer_id).all()
        #for a in accounts:
            #form.account_number.choices.append(a.Id)
        form.account_number.choices = [(account.Id) for account in accounts]
    if form.validate_on_submit():
        account = Account.query.filter_by(Id=form.account_number.data).first()
        if not account:
           flash('Account does not exist', 'danger')
           return redirect(url_for('deposit'))
        if form.amount.data > 5000:
            flash('Deposit amount should not be greater than 5000', 'danger')
            return redirect(url_for('deposit'))
        account.Balance += form.amount.data
        db.session.commit()
        flash('Deposit Successful', 'success')
        return redirect("/deposit")
        
    return render_template('deposit.html',
                             form=form
                            )



@app.route("/withdraw", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin", "Cashier")
def withdraw():
    form = withdrawal_form()
    customer_id = session.get('customer_id')
    if customer_id:
        accounts= db.session.query(Account).filter(Account.CustomerId == customer_id).all()
        form.account_number.choices = [(account.Id) for account in accounts]
    if form.validate_on_submit():
        account = Account.query.filter_by(Id = form.account_number.data).first()
        if not account:    
            flash('Account does not exist', 'danger')
            return redirect('/withdraw')
        if account.Balance < form.amount.data:
            flash('Too low balance', 'error')
            return redirect('/withdraw')
        account.Balance -= form.amount.data
        db.session.commit()
        flash('Withdrawal Succesful', 'success')
        return redirect('/withdraw')

    return render_template('withdrawal.html',
                            form = form
                            )




@app.route("/category/<id>")
def category(id):
    products = Product.query.all()
    return render_template("category.html", products=products
                            
            )

@app.route("/tables")
def tables():
    return render_template("tables.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seedData(app,db)
        app.run(debug=True)
        

