"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import random
from datetime import date
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    def test_read_an_account(self):
        """It should read a single Account"""
        # create 5 test accounts, select one
        account = random.choice(self._create_accounts(5))

        # test to successfully read the account
        response = self.client.get(
            BASE_URL + f"/{str(account.id)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test the data returned
        data = response.get_json()
        self.assertEqual(data["id"], account.id)
        self.assertEqual(data["name"], account.name)
        self.assertEqual(data["email"], account.email)
        self.assertEqual(data["address"], account.address)
        self.assertEqual(data["phone_number"], account.phone_number)
        self.assertEqual(str(data["date_joined"]), str(account.date_joined))

    def test_read_nonexisting_account(self):
        """It should fail to read a non-existing Account"""
        response = self.client.get(BASE_URL + "/123")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_accounts(self):
        """It should read the list of Accounts"""
        # create 5 test accountss
        account_objects = self._create_accounts(5)

        # test to successfully read the list of accounts
        response = self.client.get(
            BASE_URL
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test the data returned
        data = response.get_json()
        for account in data:
            account_id = account["id"]
            account_object = next(
                (acc for acc in account_objects if acc.id == account_id),
                None
            )
            self.assertNotEqual(account_object, None)

            # test if the attributes match
            self.assertEqual(account["id"], account_object.id)
            self.assertEqual(account["name"], account_object.name)
            self.assertEqual(account["email"], account_object.email)
            self.assertEqual(account["address"], account_object.address)
            self.assertEqual(
                account["phone_number"],
                account_object.phone_number
            )
            self.assertEqual(
                date.fromisoformat(account["date_joined"]),
                account_object.date_joined
            )

    def test_list_no_accounts(self):
        """It should read the empty list of Accounts"""
        # test to successfully read the empty list of accounts
        response = self.client.get(
            BASE_URL
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if a list is returned
        self.assertIsInstance(response.get_json(), list)

        # check if returned list is empty
        self.assertEqual(len(response.get_json()), 0)

    def test_update_account(self):
        """It should update an Account"""
        # create 5 test accounts, select one
        account = random.choice(self._create_accounts(5))

        # read the account before the update
        resp_original = self.client.get(
            BASE_URL + f"/{str(account.id)}"
        )
        self.assertEqual(resp_original.status_code, status.HTTP_200_OK)
        data_original = resp_original.get_json()

        # change the da, a in thsomeccoun and do the update
        data_changed = data_original.copy()
        data_changed["name"] = "Test Candidate"
        data_changed["email"] = "tester@mailtest.org"

        resp_returned = self.client.put(
            BASE_URL + f"/{str(data_changed['id'])}",
            json=data_changed,
            content_type="application/json"
        )
        self.assertEqual(resp_returned.status_code, status.HTTP_200_OK)
        data_returned = resp_returned.get_json()

        # compare the returned and the changed data
        self.assertEqual(data_returned["name"], data_changed["name"])
        self.assertEqual(data_returned["email"], data_changed["email"])
        self.assertEqual(data_returned["address"], data_changed["address"])
        self.assertEqual(
            data_returned["phone_number"],
            data_changed["phone_number"]
        )
        self.assertEqual(
            date.fromisoformat(data_returned["date_joined"]),
            date.fromisoformat(data_changed["date_joined"])
        )

        # compare the returned and the original data,
        # these should be different:
        self.assertNotEqual(data_returned["name"], data_original["name"])
        self.assertNotEqual(data_returned["email"], data_original["email"])
        
        # these should be the same:
        self.assertEqual(data_returned["address"], data_original["address"])
        self.assertEqual(
            data_returned["phone_number"],
            data_original["phone_number"]
        )
        self.assertEqual(
            date.fromisoformat(data_returned["date_joined"]),
            date.fromisoformat(data_original["date_joined"])
        )

    def test_update_nonexisting_account(self):
        """It should fail to update a non-existing Account"""
        test_account = AccountFactory()
        response = self.client.put(
            BASE_URL + "/123",
            json=test_account.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
