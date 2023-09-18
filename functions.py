DEBUG = True

def debug(var, var_name="var"):
    if DEBUG:
        print(f"{var_name}: {var}")

def log(statement: str):
    if DEBUG:
        print(statement)