import os, hashlib

SUB_DIR = "submissions"
LOG = "log.txt"

def hash_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def log(msg):
    with open(LOG, "a") as f:
        f.write(msg + "\n")

def submit():
    sid = input("id: ")
    path = input("file: ")

    if not os.path.isfile(path):
        print("not found")
        return

    name = os.path.basename(path)
    h = hash_file(path)

    for f in os.listdir(SUB_DIR):
        if f.endswith(name):
            print("duplicate name")

    dest = f"{sid}__{name}"

    with open(path, "rb") as s, open(os.path.join(SUB_DIR, dest), "wb") as d:
        d.write(s.read())

    log(f"{sid} {name} {h}")
    print("ok")

def menu():
    while True:
        print("1 submit")
        print("2 exit")

        c = input("> ")
        if c == "1":
            submit()
        else:
            break

menu()
