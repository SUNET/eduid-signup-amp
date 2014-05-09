import datetime

import bson

from eduid_am.exceptions import UserDoesNotExist
from eduid_am.tests import MongoTestCase
from eduid_signup_amp import attribute_fetcher


TEST_DB_NAME = 'eduid_signup_test'


class AttributeFetcherTests(MongoTestCase):

    def test_invalid_user(self):
        self.assertRaises(UserDoesNotExist, attribute_fetcher,
                          self.conn['test'],
                          bson.ObjectId('000000000000000000000000'))

    def test_existing_user(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'verified': True,
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
        })
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {
                'mail': 'john@example.com',
                'mailAliases': [{
                    'email': 'john@example.com',
                    'verified': True,
                }],
                'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0)
            }
        )

    def test_user_without_aliases(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
        })
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {
                'mail': 'john@example.com',
                'mailAliases': [{
                    'email': 'john@example.com',
                    'verified': False,
                }],
                'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0)
            }
        )

    def test_malicious_attributes(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'verified': True,
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
            'malicious': 'hacker',
        })
        # Malicious attributes are not returned
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {
                'mail': 'john@example.com',
                'mailAliases': [{
                    'email': 'john@example.com',
                    'verified': True,
                }],
                'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0)
            }
        )

    def test_fillup_attributes(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'displayName': 'John',
            'verified': True,
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
        })
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {
                'mail': 'john@example.com',
                'mailAliases': [{
                    'email': 'john@example.com',
                    'verified': True,
                }],
                'displayName': 'John',
                'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0),
            }
        )

    def test_user_finished_and_removed(self):
        user_id = self.conn['test'].registered.insert({
            'email': 'john@example.com',
            'verified': True,
            'date': datetime.datetime(2013, 4, 1, 10, 10, 20),
            'passwords': [{
                'id': '123',
                'salt': '456',
            }]
        })
        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id),
            {
                'mail': 'john@example.com',
                'mailAliases': [{
                    'email': 'john@example.com',
                    'verified': True,
                }],
                'date': datetime.datetime(2013, 4, 1, 10, 10, 20, 0),
                'passwords': [{
                    'id': u'123',
                    'salt': u'456',
                }]
            }
        )
        self.assertRaises(UserDoesNotExist, attribute_fetcher, self.conn['test'], user_id)
