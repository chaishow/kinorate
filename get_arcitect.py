import os

def generate_tree(directory, prefix=""):
    entries = sorted(os.listdir(directory))
    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = (index == len(entries) - 1)
        connector = "|" if not is_last else " "
        prefix_connector = "|----" if not is_last else " \____"
        print(f"{prefix}{prefix_connector}{entry}")
        if os.path.isdir(path):
            new_prefix = f"{prefix}{connector}    "
            generate_tree(path, new_prefix)

if __name__ == "__main__":
    print("ROOT")
    generate_tree(os.getcwd())