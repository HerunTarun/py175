from bcrypt import checkpw

def find_logged_in_user(users_data):
    for user in users_data:
        for username in user:
            if user[username]['logged in'] == True:
                return username
    return None

def toggle_user_login_status(username, users_data):
    for user in users_data:
        if username in user:
            current_status = user[username]['logged in']
            user[username]['logged in'] = not current_status
            return None

def verify_user(username, users_data):
    return [user for user in users_data if username in user.keys()]

def verify_user_password(username, password, users_data):
    user_data = verify_user(username, users_data)
    for user in user_data:
        hashed_password = user[username]['password']
        print(f"Checking hashed pw: {hashed_password}")
        hashed_in_bytes = hashed_password.encode('utf-8')
        password_in_bytes = password.encode('utf-8')
        return checkpw(password_in_bytes, hashed_in_bytes)
    return False
