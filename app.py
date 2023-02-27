from flask import Flask, render_template, request, redirect, session, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_security import roles_accepted, auth_required, logout_user, SQLAlchemyUserDatastore, Security
import os
from model import db, seedData, Customer, Account, Transaction, fsqla
from deposit_forms import deposit_form
from withdrawal_form import withdrawal_form
from authenticcation_form import authentication_form
from datetime import datetime
from transfer_form import transfer_form
import requests
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hej123@localhost/starbank'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'Kp10kHudawanDa594-2ToBiaEnji-9OnAchoRaNaraFt')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
db.app = app
db.init_app(app)
migrate = Migrate(app,db)


fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass
    # id = db.Column(db.Integer, primary_key = True)
    # name = db.Column(db.String(100), unique = True) 

class User(db.Model, fsqla.FsUserMixin):
    # id = db.Column(db.Integer, primary_key = True)
    # email = db.Column(db.String(100), unique= True)
    # password= db.Column(db.String(255))
    # active = db.Column(db.Boolean)
    pass
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

def save_transaction(type, operation, date, amount, new_balance, account_id):
    transaction = Transaction(Type=type, Operation=operation, 
                            Date= date,
                            Amount=amount, NewBalance=new_balance, 
                            AccountId=account_id)
    db.session.add(transaction)
    db.session.commit()


@app.route("/")
def home():

    account = Account.query.filter(Account.Balance)
    top_accounts = Account.query.order_by(Account.Balance.desc()).limit(10).all()
    balance = 0
    for a in account:
        balance +=a.Balance
    return render_template("home.html",
                            number_of_accounts= Account.query.count(),
                            number_of_customers = Customer.query.count(),
                            total_balance = balance,
                            redirect="/",
                            top_accounts= top_accounts,
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
    onvalidate_is_ok = True
    if request.method == 'POST':
        customer = Customer.query.filter_by(NationalId=form.nationalId.data).first()
        if not customer:
            form.nationalId.errors = form.nationalId.errors + ('Customer does not exist',)
            onvalidate_is_ok = False
    if onvalidate_is_ok and form.validate_on_submit():
        if customer:
            session['customer_id']= customer.Id
            if form.transaction_type.data == "deposit":
                return redirect("/deposit")
            elif form.transaction_type.data == "withdraw":
                return redirect("/withdraw")
            elif form.transaction_type.data == "transfer":
                return redirect("/transfer")
        else:
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
        form.account_number.choices = [(account.Id) for account in accounts]
    onvalidate_is_ok = True
    if request.method == 'POST':
        account = Account.query.filter_by(Id = form.account_number.data).first()
        if form.amount.data < 0 or form.amount.data > 50000:
            form.amount.errors = form.amount.errors + ('You cant deposit less than 0',)
            onvalidate_is_ok = False

    if onvalidate_is_ok and form.validate_on_submit():
        account = Account.query.filter_by(Id=form.account_number.data).first()
        if not account:
           flash('Account does not exist',category= 'danger')
           return redirect(url_for('deposit'))
        
        account.Balance += form.amount.data
        db.session.commit()
        save_transaction('Credit',
                    'Deposit',
                    datetime.now(),
                    form.amount.data,
                    account.Balance, 
                    account.Id )
        flash('Deposit Successful', category='success')
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
    onvalidate_is_ok = True
    if request.method == 'POST':
        account = Account.query.filter_by(Id = form.account_number.data).first()
        if account.Balance < form.amount.data or form.amount.data < 0:
            form.amount.errors = form.amount.errors + ('Belopp too large',)
            onvalidate_is_ok = False
        

    if onvalidate_is_ok and form.validate_on_submit():
        account.Balance -= form.amount.data
        db.session.commit()
        save_transaction('Credit',
                         'wthidraw',
                         datetime.now(),
                         form.amount.data,
                         account.Balance, 
                         account.Id )
        flash('Withdrawal Succesful', category='success')
        form.submit_success = True
        #return redirect('/withdraw')
    return render_template('withdrawal.html',
                            form = form
                        
                            )


@app.route("/transfer", methods= ['GET','POST'])
@auth_required()
@roles_accepted('Admin','Cashier')
def transfer():
    form = transfer_form()
    customer_id = session.get('customer_id')
    if customer_id:
        source_accounts= db.session.query(Account).filter(Account.CustomerId == customer_id).all()
        form.source_account_number.choices = [(account.Id) for account in source_accounts]
        destination_accounts = db.session.query(Account).filter(Account.CustomerId == customer_id).all()
        form.destination_account_number.choices = [(account.Id) for account in destination_accounts]

    onvalidate_is_ok = True
    if request.method == 'POST':
        source_account = Account.query.filter_by(Id = form.source_account_number.data).first() 
        if source_account.Balance < form.amount.data or form.amount.data < 0:
            form.amount.errors = form.amount.errors + ('Not enough balance in your account!',)
            onvalidate_is_ok = False


    if onvalidate_is_ok and form.validate_on_submit():
        source_account = Account.query.filter_by(Id = form.source_account_number.data).first()
        destination_account= Account.query.filter_by(Id = form.destination_account_number.data).first()
        if source_account and destination_account:
            if source_account == destination_account:
                flash('Should choese diffirent account', category='error')
            elif destination_account.Balance < form.amount.data:
                flash('Your balance is too low!', category='error')
            else:
                source_account.Balance -= form.amount.data   
                destination_account.Balance += form.amount.data
                db.session.commit()

                save_transaction('Credit',
                                'Transfer',
                                datetime.now(),
                                -(form.amount.data),
                                source_account.Balance, 
                                source_account.Id
                                )
                save_transaction('Credit',
                                    'Transfer',
                                    datetime.now(),
                                    form.amount.data,
                                    destination_account.Balance, 
                                    destination_account.Id
                                    )
                flash('Transfer Succesful', category='success')
                return redirect("/transfer")

    return render_template("transfer.html",
                            form = form
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
        

