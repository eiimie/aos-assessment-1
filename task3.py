import os
import hashlib
import time

SUB_DIR = "submissions"
SUB_LOG = "submission_log.txt"
LOGIN_LOG = "login_log.txt"

ALLOWED_EXT = [".pdf", ".docx"]
MAX_SIZE = 5 * 1024 * 1024  # 5mb

failed_logins = {}
locked_accounts = {}

# basic hash function for duplicate detection
def hash_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

# append message to a log file
def log(file, msg):
    with open(file, "a") as f:
        f.write(msg + "\n")

# validate file type and size
def validate_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXT:
        print("invalid file type")
        return False

    size = os.path.getsize(path)
    if size > MAX_SIZE:
        print("file too large")
        return False

    return True

# check for duplicate filename and content
def is_duplicate(name, h):
    if not os.path.isdir(SUB_DIR):
        return False

    for f in os.listdir(SUB_DIR):
        if "__" not in f:
            continue

        _, existing_name = f.split("__", 1)
        if existing_name == name:
            existing_path = os.path.join(SUB_DIR, f)
            if hash_file(existing_path) == h:
                return True

    return False

# submit assignment
def submit():
    sid = input("id: ")
    path = input("file: ")

    if not os.path.isfile(path):
        print("not found")
        return

    if not validate_file(path):
        return

    name = os.path.basename(path)
    h = hash_file(path)

    if is_duplicate(name, h):
        print("duplicate submission")
        return

    if not os.path.isdir(SUB_DIR):
        os.makedirs(SUB_DIR)

    dest = f"{sid}__{name}"
    dest_path = os.path.join(SUB_DIR, dest)

    with open(path, "rb") as s, open(dest_path, "wb") as d:
        d.write(s.read())

    log(SUB_LOG, f"{sid} {name} {h} {int(time.time())}")
    print("submitted")

# list all submissions
def list_submissions():
    if not os.path.isdir(SUB_DIR):
        print("no submissions")
        return

    for f in os.listdir(SUB_DIR):
        print(f)

# simulate login attempt
def login():
    user = input("user: ")
    now = time.time()

    # check if account is locked
    if user in locked_accounts:
        print("account locked")
        return

    success = input("password correct? (y/n): ") == "y"

    # log attempt
    log(LOGIN_LOG, f"{user} {int(now)} {'success' if success else 'fail'}")

    if success:
        failed_logins[user] = []
        print("login ok")
        return

    # track failed attempts
    failed_logins.setdefault(user, []).append(now)

    # keep only recent attempts (last 60s)
    failed_logins[user] = [t for t in failed_logins[user] if now - t <= 60]

    if len(failed_logins[user]) >= 3:
        locked_accounts[user] = True
        print("account locked due to failures")
    elif len(failed_logins[user]) > 1:
        print("suspicious activity detected")
    else:
        print("login failed")

# confirm exit
def confirm_exit():
    c = input("exit? (y/n): ")
    return c.lower() == "y"

# menu system
def menu():
    while True:
        print("\n1 submit")
        print("2 check duplicates (manual)")
        print("3 list submissions")
        print("4 login attempt")
        print("5 exit")

        c = input("> ")

        if c == "1":
            submit()
        elif c == "2":
            name = input("filename: ")
            path = input("path: ")
            if os.path.isfile(path):
                h = hash_file(path)
                print("duplicate" if is_duplicate(name, h) else "not duplicate")
        elif c == "3":
            list_submissions()
        elif c == "4":
            login()
        elif c == "5":
            if confirm_exit():
                break
        else:
            print("invalid")

menu()
