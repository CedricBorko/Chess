def read_file(path):
    print(path)
    try:
        with open(path, "r", encoding="Latin1") as file:
            return file.read()
    except FileNotFoundError:
        print("No file found at {}.".format(path))
        write_file(path)


def write_file(path, data=""):
    with open(path, "w") as file:
        file.write(data)


def append_to_file(path, data=""):
    with open(path, "a") as file:
        file.write(data)

