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
            'mail': 'john@example.com',
            'mailAliases': [{
                'email': 'john@example.com',
                'verified': True,
            }],
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
            'mail': 'john@example.com',
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
            'mail': 'john@example.com',
            'mailAliases': [{
                'email': 'john@example.com',
                'verified': True,
            }],
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
            'mail': 'john@example.com',
            'displayName': 'John',
            'mailAliases': [{
                'email': 'john@example.com',
                'verified': True,
            }],
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

        self.conn['test'].registered.update({
            'mail': 'john@example.com',
        }, {
            '$set': {
                'displayName': 'John2',
            }
        })

        self.assertEqual(
            attribute_fetcher(self.conn['test'], user_id)['displayName'],
            'John2',
        )

    def test_append_attributes(self):
        user_id = self.conn['test'].registered.insert({
            'mail': 'john@example.com',
            'mailAliases': [{
                'email': 'john@example.com',
                'verified': True,
            }],
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

        # Don't repeat the password
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

        # Adding a new password
        self.conn['test'].registered.update({
            'mail': 'john@example.com',
        }, {
            '$push': {
                'passwords': {
                    'id': '123a',
                    'salt': '456',
                }
            }
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
                }, {
                    'id': u'123a',
                    'salt': u'456',
                }]
            }
        )
