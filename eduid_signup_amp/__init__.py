import logging

import bson


logger = logging.getLogger(__name__)


def attribute_fetcher(db, user_id):
    attributes = {}
    try:
        _id = bson.ObjectId(user_id)
    except bson.errors.InvalidId:
        logger.error('Invalid user_id: %s' % user_id)
        return attributes
    
    user = db.registered.find_one({'_id': _id})
    if user is None:
        logger.warning('The user %s does not exist in the "registered" collection'
                       % user_id)

    else:
        for attr in ('email', 'date', 'verified'):
            value = user.get(attr, None)
            if value is not None:
                attributes[attr] = value

        logger.debug('Attributes fetched for user %s: %s'
                     % (user_id, attributes))

    return attributes
