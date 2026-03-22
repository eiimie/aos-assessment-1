import os

SUBMISSIONS = "submissions"

def submit():
    student = input("student id: ")
    path = input("file path: ")

    if not os.path.exists(path):
        print("file not found")
        return

    name = os.path.basename(path)

    dest = SUBMISSIONS + "/" + student + "_" + name

    f = open(path, "rb")
    data = f.read()
    f.close()

    f2 = open(dest, "wb")
    f2.write(data)
    f2.close()

    print("submitted")

def list_files():
    files = os.listdir(SUBMISSIONS)
    for f in files:
        print(f)

while True:
    print("1 submit")
    print("2 list")
    print("3 exit")

    c = input("> ")

    if c == "1":
        submit()
    elif c == "2":
        list_files()
    elif c == "3":
        break
