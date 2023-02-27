import unittest
from flask import Flask, render_template, request, url_for, redirect
from app import app, User,Role
from model import db, Customer, Account
from flask_security import Security,SQLAlchemyUserDatastore, hash_password
from sqlalchemy import create_engine
from datetime import datetime, date


def set_current_user(app, ds, email):
    """Set up so that when request is received,
    the token will cause 'user' to be made the current_user
    """

    def token_cb(request):
        if request.headers.get("Authentication-Token") == "token":
            return ds.find_user(email=email)
        return app.security.login_manager.anonymous_user()

    app.security.login_manager.request_loader(token_cb)


init = False

class FormsTestCases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(FormsTestCases, self).__init__(*args, **kwargs)
    def tearDown(self):
        self.ctx.pop()
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        app.config["SERVER_NAME"] = "stefan.se"
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['SECURITY_FRESHNESS_GRACE_PERIOD'] = 123454
        global init
        if not init:
            db.init_app(app)
            db.create_all()
            init = True
            user_datastore = SQLAlchemyUserDatastore(db, User, Role)
            app.security = Security(app, user_datastore,register_blueprint=False)
            app.security.init_app(app, user_datastore,register_blueprint=False)
            app.security.datastore.db.create_all()




   


    def test_when_authorizing_customer_using_national_ID_in_case_customer_does_not_exist_tell_custome_does_not_exist(self):
        app.security.datastore.create_role(name="Admin")
        app.security.datastore.create_user(email="unittest@me.com", password=hash_password("password"), roles=["Admin"])
        app.security.datastore.commit()

        set_current_user(app, app.security.datastore, "unittest@me.com")

        account = Account()
        account.Id = 1
        account.AccountType = 'checking'
        account.Created = datetime(2022, 2, 28, 12, 30, 0)
        account.Balance = 100
        account.CustomerId = 1
        customer = Customer()
        customer.GivenName = "Stefan"
        customer.Surname = "Holmberg"
        customer.Streetaddress = "Karlavägen12"
        customer.City = "Stockholm"
        customer.Zipcode = 73335
        customer.Country = "Sweden"
        customer.CountryCode = "+46"
        customer.Birthday = date(1990, 2, 28)
        customer.NationalId ='1234567890'
        customer.TelephoneCountryCode=1
        customer.Telephone='555-555-5555'
        customer.EmailAddress='unittest@gmail.com'
        db.session.add(account)
        db.session.add(customer)
        db.session.commit()

        test_client = app.test_client()
        with test_client:
            url = '/authentication' 
            response = test_client.post(url, data={"nationalId":'1234567892', 
                                                    "transaction_type":'Withdraw',},
                                                    headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
                                        )
            

            s = response.data.decode("utf-8") 
            ok = 'Customer does not exist' in s
            self.assertTrue(ok)



    def test_when_withdraw_negative_should_show_error(self):
        test_client = app.test_client()
        with test_client:
            url = '/withdraw' 
            response = test_client.post(url, data={"account_number":"1", 
                                                    "amount":-1000},
                                                    headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
                                        )
            s = response.data.decode("utf-8") 
            ok = 'Belopp too large' in s
            self.assertTrue(ok)



    def test_when_withdraw_more_than_account_balance_should_show_error(self):
        test_client = app.test_client()
        with test_client:
            url = '/withdraw' 
            response = test_client.post(url, data={"account_number":"1", 
                                                    "amount":1000},
                                                    headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
                                        )
            s = response.data.decode("utf-8") 
            ok = 'Belopp too large' in s
            self.assertTrue(ok)


    def test_when_transfer_more_than_account_balance_should_show_error(self):
        test_client = app.test_client()
        with test_client:
            url = '/transfer' 
            response = test_client.post(url, data={"source_account_number":"1",
                                                   "destination_account_number":"2", 
                                                    "amount":-1000},
                                                    headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
                                        )
            s = response.data.decode("utf-8") 
            ok = 'Not enough balance in your account!' in s
            self.assertTrue(ok)



    def test_when_deposit_less_than_0_or_more_than_50000_at_a_time_should_show_error(self):
        test_client = app.test_client()
        with test_client:
            url = '/deposit' 
            response = test_client.post(url, data={"account_number":"1", 
                                                    "amount":-1},
                                                    headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
                                        )
            s = response.data.decode("utf-8") 
            ok = 'You cant deposit less than 0' in s
            self.assertTrue(ok)


    def test_when_deposit_more_than_50000_at_a_time_should_show_error(self):
        test_client = app.test_client()
        with test_client:
            url = '/deposit' 
            response = test_client.post(url, data={"account_number":"1", 
                                                    "amount":60000},
                                                    headers={app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
                                        )
            s = response.data.decode("utf-8") 
            ok = 'You cant deposit less than 0' in s
            self.assertTrue(ok)






if __name__ == "__main__":
    unittest.main()