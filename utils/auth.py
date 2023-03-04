import users

def user_is_authorized():
    authorized = False
    user_id = users.user_id()
    if not user_id:
        return authorized
    if users.is_user():
        authorized = True
    return authorized