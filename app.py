from mailbox import Message
from flask import Flask, jsonify, render_template, request, redirect, session, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_security import roles_accepted, auth_required, logout_user, SQLAlchemyUserDatastore, Security
import os
from model import db, seedData, Customer, Account, Transaction, fsqla
from deposit_forms import deposit_form
from withdrawal_form import withdrawal_form
from authenticcation_form import authentication_form
from new_customer import create_new_customer
from get_profile_form import get_customer_profile
from datetime import datetime
from transfer_form import transfer_form
import requests
import time
from flask_mail import Mail
from forgot_password import ForgotPasswordForm,ResetPasswordForm
from flask_security import hash_password


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://nordiscbank:Hejsan123@nordicbank.mysql.database.azure.com/bank'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hej123@localhost/starbank'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'Kp10kHudawanDa594-2ToBiaEnji-9OnAchoRaNaraFt')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'jawidyari123@gmail.com' # replace with your email address
app.config['MAIL_PASSWORD'] = 'Hejsan123#' # replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'jawidyari123@gmail.com' # replace with your email address
mail = Mail(app)
db.app = app
db.init_app(app)
migrate = Migrate(app,db)


fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):

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


@app.route("/get_customer_profile", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin", "Cashier")
def customer_profile():
    form = get_customer_profile()
    if form.validate_on_submit():
        customer = db.session.query(Customer).filter(Customer.Id == form.customer_id.data).first()
        accounts = db.session.query(Account).filter(Account.CustomerId == form.customer_id.data).all()
        total_balance = sum([account.Balance for account in accounts])
        return render_template("customer_profile.html",
                            customer = customer,
                            accounts = accounts,
                            total_balance = total_balance,
                            redirect = "/customer",
                            activePage = 'profile'
                                )
    return render_template('search_profile.html', form = form)


@app.route("/account-history/<int:account_id>")
@auth_required()
@roles_accepted("Admin", "Cashier")
def transactions(account_id):
    page =int(request.args.get('page', 1))
    transactions_query = db.session.query(Transaction).filter(Transaction.AccountId == account_id)
    account = db.session.query(Account).filter(Account.Id == account_id).first()
    paginationObject=transactions_query.paginate(page = page, error_out = False)
    return render_template("account-history.html",
                           transactions= paginationObject,
                           account = account,
                           redirect="/account-history",
                           activePage = 'account-history'

                            )

@app.route('/account-history/<int:account_id>/transactions', methods=['GET'])
def more_transactions(account_id):
    offset = request.args.get('offset', type=int)
    limit = request.args.get('limit', type=int)
    transactions = db.session.query(Transaction)\
        .filter(Transaction.AccountId == account_id)\
        .limit(limit).offset(offset).all()
    return jsonify(transactions=[t.to_dict() for t in transactions])


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
            form.amount.errors = form.amount.errors + ('Belopp too large or below 0',)
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
            form.amount.errors = form.amount.errors + ('OBS! not enough balance in your account or you try to transfer below 0',)
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


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = user_datastore.find_user(email)
        if user:
            token = user_datastore.generate_reset_password_token(user)
            reset_link = url_for('reset_password', token=token, _external=True)
            msg = Message(subject=app.config['SECURITY_EMAIL_SUBJECT_PASSWORD_RESET'],
                          recipients=[user.email])
            msg.body = render_template('security/reset_password_instructions.txt',
                                        reset_link=reset_link, user=user)
            mail.send(msg)
            return redirect(url_for('security.login'))
    return render_template('security/forgot_password.html', form=form)



@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = user_datastore.get_user_from_reset_password_token(token)
    if not user:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('security.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user_datastore.reset_password_token_used(user)
        user_datastore.update_user(user, password= hash_password(form.password.data))
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('security.login'))
    return render_template('security/reset_password.html', form=form)



@app.route("/createCustomer", methods= ['GET', 'POST'])
@auth_required()
@roles_accepted("Admin", "Cashier")
def create_customer():
    form = create_new_customer()
    if form.validate_on_submit():
        customer = Customer()
        customer.GivenName = form.GivenName.data
        customer.Surname = form.Surname.data
        customer.City = form.City.data
        customer.Country = form.Country.data
        customer.NationalId = form.NationalId.data
        customer.Birthday = form.Birthday.data
        customer.Streetaddress = form.Streetaddress.data
        customer.CountryCode= form.CountryCode.data
        customer.Zipcode= form.Zipcode.data
        customer.EmailAddress = form.EmailAddress.data
        customer.TelephoneCountryCode = form.TelephoneCountryCode.data
        customer.Telephone= form.Telephone.data
        db.session.add(customer)
        db.session.commit()
        return redirect('/createCustomer')
    return render_template('new_customer.html', form = form)



if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seedData(app,db)
        app.run(debug=True)
        

