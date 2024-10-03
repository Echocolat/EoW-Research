import os

def search(version, string):

    for subdir, dirs, files in os.walk(version):
        for file in files:
            with open(os.path.join(subdir, file), 'r', errors = "ignore") as file_:
                if string in file_.read():
                    print(os.path.join(subdir, file))

search("101", "MapAbyss")