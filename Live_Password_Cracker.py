import hashlib

# Pretend database with user information (replace with your actual database)
database = {
    'user1': '5f4dcc3b5aa765d61d8327deb882cf99',  # 'password' hashed with MD5
    'user2': '098f6bcd4621d373cade4e832627b4f6',  # 'test' hashed with MD5
    # Add more users as needed
}

def hash_password(password):
    # Hash the password using a secure algorithm (e.g., bcrypt)
    return hashlib.md5(password.encode()).hexdigest()

def check_password(username, password):
    if username in database:
        hashed_password = database[username]
        entered_password_hash = hash_password(password)

        # Compare the entered password hash with the stored hash
        if entered_password_hash == hashed_password:
            print(f"Password for user '{username}' is correct.")
        else:
            print(f"Password for user '{username}' is incorrect.")
    else:
        print(f"User '{username}' not found in the database.")

if __name__ == "__main__":
    # Get user input
    username_input = input("Enter username: ")
    password_input = input("Enter password: ")

    # Check the password
    check_password(username_input, password_input)
