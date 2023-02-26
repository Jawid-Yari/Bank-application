import unittest
from app import app, db,session
from model import Customer


class TestAuthentication(unittest.TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config["SERVER_NAME"] = "stefan.se"
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        app.config['LOGIN_DISABLED'] = True
        app.config['SECURITY_FRESHNESS_GRACE_PERIOD'] = 123454
        return app

    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        global init
        if not init:
            db.init_app(app)
            db.create_all()
            self.customer = Customer(
                GivenName='John',
                Surname='Doe',
                Streetaddress='123 Main St',
                City='Anytown',
                Zipcode='12345',
                Country='USA',
                CountryCode='US',
                Birthday='1990-01-01',
                NationalId='1234567890',
                TelephoneCountryCode=1,
                Telephone='555-555-5555',
                EmailAddress='johndoe@example.com'
            )
            db.session.add(self.customer)
            db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_national_id_with_valid_customer(self):
        test_client = app.test_client()
        with test_client:
            response = test_client.post('/authentication', data={
                'nationalId': self.customer.NationalId,
                'transaction_type': 'deposit'
            })
            #self.assert_redirects(response, '/deposit')
            self.assertEqual(session['customer_id'], self.customer.Id)

    def test_get_national_id_with_invalid_customer(self):
        test_client = app.test_client()
        with test_client:
            response = test_client.post('/authentication', data={
                'nationalId': 'invalid_id',
                'transaction_type': 'deposit'
            })
            #self.assert_redirects(response, '/authentication')
            self.assertNotIn('customer_id', session)


if __name__ == "__main__":
    unittest.main()