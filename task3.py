import os, time

users = {
    "admin": "1234",
    "student": "pass"
}

fails = {}

def login():
    u = input("user: ")
    p = input("pass: ")

    if u not in fails:
        fails[u] = 0

    if fails[u] > 3:
        print("locked")
        return False

    if u in users and users[u] == p:
        print("ok")
        fails[u] = 0
        return True
    else:
        print("bad login")
        fails[u] += 1
        return False


def log(msg):
    f = open("log.txt", "a")
    f.write(str(time.time()) + " " + msg + "\n")
    f.close()


def submit():
    path = input("file: ")

    if not os.path.exists(path):
        log("fail missing file")
        return

    name = os.path.basename(path)

    with open(path, "rb") as f:
        data = f.read()

    with open("submissions/" + name, "wb") as f:
        f.write(data)

    log("submitted " + name)


if login():
    submit()
