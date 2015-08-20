import pymongo.errors
from eduid_userdb.exceptions import UserDoesNotExist


import logging
logger = logging.getLogger(__name__)


def attribute_fetcher(db, user_id):
    """
    Read a user from the Signup private userdb and return an update
    dict to let the Attribute Manager update the use in the central
    eduid user database.

    :param db: User database (application specific)
    :param user_id: Unique identifier
    :type db: SignupUserDB
    :type user_id: ObjectId

    :return: update dict
    :rtype: dict
    """
    user = db.get_user_by_id(user_id)
    if user is None:
        raise UserDoesNotExist("No user matching _id='%s'" % user_id)

    user_dict = user.to_dict(old_userdb_format=True)

    attributes, signup_finished, = _attribute_transform(user_dict, user_id)

    if signup_finished:
        try:
            db.remove_user_by_id(user_id)
        except pymongo.errors.OperationFailure:
            # eduid_am might not have write permission to the signup application's
            # collection. Just ignore cleanup if that is the case, and let that be
            # handled by some other process (cron job maybe).
            pass

    return attributes


def _attribute_transform(user_dict, user_id):
    """
    Idempotent function transforming attributes from Signup userdb to eduid-userdb format.

    :param user_dict: Data from Signup userdb
    :rtype: dict, bool
    """
    attributes = {}

    import pprint
    logger.debug("Processing user {!r}:\n{!s}".format(user_id, pprint.pformat(user_dict)))

    if 'mail' in user_dict:
        attributes['mail'] = user_dict['mail']
    if 'mailAliases' in user_dict:
        attributes['mailAliases'] = user_dict['mailAliases']

    # This values must overwrite existent values
    signup_finished = False
    for attr in ('givenName', 'sn', 'displayName', 'passwords',
                 'date', 'eduPersonPrincipalName', 'subject'):  # XXX `date' is unused
        value = user_dict.get(attr, None)
        if value is not None:
            attributes[attr] = value
            if attr == 'passwords':
                signup_finished = True

    return attributes, signup_finished
