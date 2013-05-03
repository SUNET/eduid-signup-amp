import datetime
import unittest

import bson
import pymongo

from eduid_am.exceptions import UserDoesNotExist
from eduid_signup_amp import attribute_fetcher


TEST_DB_NAME = 'eduid_signup_test'


class AttributeFetcherTests(unittest.TestCase):

    def setUp(self):
        self.connection = pymongo.Connection()
        self.db = self.connection[TEST_DB_NAME]

    def tearDown(self):
        self.db.drop_collection('registered')

    def test_invalid_user(self):
        self.assertRaises(UserDoesNotExist, attribute_fetcher, self.db,
                          bson.ObjectId('000000000000000000000000'))

    def test_existing_user(self):
        user_id = self.db.registered.insert({
            'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
            'verified': True,
        })
        self.assertEqual(
            attribute_fetcher(self.db, user_id),
            {'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0),
            'verified': True}
        )

    def test_malicious_attributes(self):
        user_id = self.db.registered.insert({
            'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
            'verified': True,
            'malicious': 'hacker',
        })
        # Malicious attributes are not returned
        self.assertEqual(
            attribute_fetcher(self.db, user_id),
            {'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0),
            'verified': True}
        )
