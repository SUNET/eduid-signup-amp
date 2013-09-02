from eduid_am.exceptions import UserDoesNotExist


def attribute_fetcher(db, user_id):
    attributes = {}

    user = db.registered.find_one({'_id': user_id})
    if user is None:
        raise UserDoesNotExist("No user matching _id='%s'" % user_id)

    else:
        email = user.get('email', None)
        if email:
            attributes['mail'] = email
            attributes['mailAliases'] = [{
                'email': email,
                'verified': user.get('verified', False),
            }]

        # This values must overwrite existent values
        for attr in ('givenName', 'sn', 'displayName', 'passwords',
                     'date'):
            value = user.get(attr, None)
            if value is not None:
                attributes[attr] = value

    return attributes
