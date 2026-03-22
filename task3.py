import os

MAX_SIZE = 5000000  # 5mb
ALLOWED = [".pdf", ".docx"]

def submit():
    sid = input("id: ")
    path = input("file: ")

    if not os.path.isfile(path):
        print("not found")
        return

    size = os.path.getsize(path)
    if size > MAX_SIZE:
        print("too big")

    name = os.path.basename(path)
    ext = name.split(".")[-1]

    if ext not in ALLOWED:   # BUG: compares "pdf" vs ".pdf"
        print("bad type")
        return

    dest = "submissions/" + sid + "__" + name

    with open(path, "rb") as f:
        data = f.read()

    with open(dest, "wb") as f:
        f.write(data)

    print("done")

submit()
