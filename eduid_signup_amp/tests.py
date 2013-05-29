import datetime

import bson

from eduid_am.exceptions import UserDoesNotExist
from eduid_am.tests import MongoTestCase
from eduid_signup_amp import attribute_fetcher


TEST_DB_NAME = 'eduid_signup_test'


class AttributeFetcherTests(MongoTestCase):

    def test_invalid_user(self):
        self.assertRaises(UserDoesNotExist, attribute_fetcher, self.conn['test'],
                          bson.ObjectId('000000000000000000000000'))

    def test_existing_user(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
            'verified': True,
        })
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0),
            'verified': True}
        )

    def test_malicious_attributes(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
            'verified': True,
            'malicious': 'hacker',
        })
        # Malicious attributes are not returned
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0),
            'verified': True}
        )
