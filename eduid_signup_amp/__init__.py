from eduid_am.exceptions import UserDoesNotExist


def attribute_fetcher(db, user_id):
    attributes = {}

    user = db.registered.find_one({'_id': user_id})
    if user is None:
        raise UserDoesNotExist("No user matching _id='%s'" % user_id)

    email = user.get('email', None)
    if email is not None:
        attributes['mail'] = email

        attributes['mailAliases'] = [{
            'email': email,
            'verified': user.get('verified', False),
        }]

    # This values must overwrite existent values
    signup_finished = False
    for attr in ('givenName', 'sn', 'displayName', 'passwords',
                 'date', 'eduPersonPrincipalName'):
        value = user.get(attr, None)
        if value is not None:
            attributes[attr] = value
            if attr == 'passwords':
                signup_finished = True

    if signup_finished:
        db.registered.remove(spec_or_id=user_id)

    return attributes
