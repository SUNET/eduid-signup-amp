import pymongo.errors
from eduid_userdb.exceptions import UserDoesNotExist
from eduid_userdb.signup import SignupUserDB

import logging
logger = logging.getLogger(__name__)


class SignupAMPContext(object):
    """
    Private data for this AM plugin.
    """

    def __init__(self, db_uri):
        self.signup_userdb = SignupUserDB(db_uri)


def plugin_init(am_conf):
    """
    Create a private context for this plugin.

    Whatever is returned by this function will get passed to attribute_fetcher() as
    the `context' argument.

    @param db_uri: Database URI from the Attribute Manager.
    @am_conf: Attribute Manager configuration data.

    @type db_uri: str or unicode
    @type am_conf: dict
    """
    return SignupAMPContext(am_conf['MONGO_URI'])


def attribute_fetcher(context, user_id):
    """
    Read a user from the Signup private userdb and return an update
    dict to let the Attribute Manager update the use in the central
    eduid user database.

    :param context: Plugin context, see plugin_init above.
    :param user_id: Unique identifier

    :type context: SignupAMPContext
    :type user_id: ObjectId

    :return: update dict
    :rtype: dict
    """
    user = context.signup_userdb.get_user_by_id(user_id)
    if user is None:
        raise UserDoesNotExist("No user matching _id='%s'" % user_id)

    user_dict = user.to_dict(old_userdb_format=True)

    attributes, signup_finished, = _attribute_transform(user_dict, user_id)

    if signup_finished:
        try:
            context.signup_userdb.remove_user_by_id(user_id)
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
                 'date', 'eduPersonPrincipalName', 'subject', 'tou'):  # XXX `date' is unused
        value = user_dict.get(attr, None)
        if value is not None:
            attributes[attr] = value
            if attr == 'passwords':
                signup_finished = True

    return attributes, signup_finished
