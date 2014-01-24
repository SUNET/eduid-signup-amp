from eduid_am.exceptions import UserDoesNotExist


def attribute_fetcher(db, user_id):
    attributes = {}

    user = db.registered.find_one({'_id': user_id})
    if user is None:
        raise UserDoesNotExist("No user matching _id='%s'" % user_id)

    else:
        mail = user.get('mail', None)
        if mail is not None:
            attributes['mail'] = mail

        mailAliases = user.get('mailAliases', None)
        if mailAliases is not None:
            attributes['mailAliases'] = mailAliases
        else:
            attributes['mailAliases'] = [{
                'email': mail,
                'verified': False,
            }]

        # This values must overwrite existent values
        for attr in ('givenName', 'sn', 'displayName', 'passwords',
                     'date', 'eduPersonPrincipalName'):
            value = user.get(attr, None)
            if value is not None:
                attributes[attr] = value

    return attributes
