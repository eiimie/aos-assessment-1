import os
import hashlib
import time

SUB_DIR = "submissions"
SUB_LOG = "submission_log.txt"
LOGIN_LOG = "login_log.txt"

ALLOWED_EXT = {".pdf", ".docx"}
MAX_SIZE = 5 * 1024 * 1024  # 5mb

failed_logins = {}
locked_accounts = {}

def hash_file(path):
    # generate sha256 hash for file comparison
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def write_log(file, message):
    # central logging helper
    with open(file, "a") as f:
        f.write(message + "\n")

def valid_extension(path):
    # check allowed file types
    return os.path.splitext(path)[1].lower() in ALLOWED_EXT

def valid_size(path):
    # ensure file is within size limit
    return os.path.getsize(path) <= MAX_SIZE

def ensure_dir():
    # create submission dir if missing
    if not os.path.isdir(SUB_DIR):
        os.makedirs(SUB_DIR)

def find_duplicate(name, file_hash):
    # check existing submissions for identical name + content
    if not os.path.isdir(SUB_DIR):
        return False

    for entry in os.listdir(SUB_DIR):
        if "__" not in entry:
            continue

        _, existing_name = entry.split("__", 1)
        if existing_name != name:
            continue

        existing_path = os.path.join(SUB_DIR, entry)
        if hash_file(existing_path) == file_hash:
            return True

    return False

def submit():
    sid = input("id: ").strip()
    path = input("file: ").strip()

    if not os.path.isfile(path):
        print("file not found")
        return

    if not valid_extension(path):
        print("invalid type")
        return

    if not valid_size(path):
        print("file too large")
        return

    name = os.path.basename(path)
    file_hash = hash_file(path)

    if find_duplicate(name, file_hash):
        print("duplicate submission rejected")
        return

    ensure_dir()

    dest_name = f"{sid}__{name}"
    dest_path = os.path.join(SUB_DIR, dest_name)

    with open(path, "rb") as src, open(dest_path, "wb") as dst:
        for chunk in iter(lambda: src.read(4096), b""):
            dst.write(chunk)

    timestamp = int(time.time())
    write_log(SUB_LOG, f"{sid},{name},{file_hash},{timestamp}")

    print("submission stored")

def list_submissions():
    # display stored files
    if not os.path.isdir(SUB_DIR):
        print("no submissions yet")
        return

    for f in sorted(os.listdir(SUB_DIR)):
        print(f)

def handle_login():
    user = input("user: ").strip()
    now = time.time()

    if user in locked_accounts:
        print("account locked")
        return

    success = input("password correct? (y/n): ").lower() == "y"

    write_log(LOGIN_LOG, f"{user},{int(now)},{'ok' if success else 'fail'}")

    if success:
        failed_logins[user] = []
        print("login successful")
        return

    attempts = failed_logins.setdefault(user, [])
    attempts.append(now)

    # only keep attempts in last 60 seconds
    attempts[:] = [t for t in attempts if now - t <= 60]

    if len(attempts) >= 3:
        locked_accounts[user] = True
        print("account locked")
    elif len(attempts) > 1:
        print("suspicious activity")
    else:
        print("login failed")

def confirm_exit():
    # simple exit confirmation
    return input("confirm exit (y/n): ").lower() == "y"

def menu():
    while True:
        print("\n1 submit assignment")
        print("2 check duplicate")
        print("3 list submissions")
        print("4 login attempt")
        print("5 exit")

        choice = input("> ").strip()

        if choice == "1":
            submit()
        elif choice == "2":
            path = input("file path: ")
            if os.path.isfile(path):
                name = os.path.basename(path)
                h = hash_file(path)
                print("duplicate" if find_duplicate(name, h) else "not duplicate")
            else:
                print("file not found")
        elif choice == "3":
            list_submissions()
        elif choice == "4":
            handle_login()
        elif choice == "5":
            if confirm_exit():
                break
        else:
            print("invalid option")

menu()
