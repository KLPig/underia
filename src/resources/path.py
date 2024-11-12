import os

print("Discovering path...")
print("Containing: ", os.listdir())

def get_path(filename=None):
    print("Current path: ", os.getcwd())
    try:
        pt = os.MEIPASS
        print("Path selected: MEIPASS: ", pt, "as pyinstaller")
    except AttributeError:
        pt = os.path.abspath(".")
        print("Path selected: Current directory: ", pt)
    pt = ''
    if filename:
        return os.path.join(pt, filename)
    else:
        return pt
