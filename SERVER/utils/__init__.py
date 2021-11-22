import sys


def print_to_console(s):
    print(s)
    sys.stdout.flush()


def to_json(var):
    res = None

    if hasattr(var, "to_json"):
        res = var.to_json()

    elif type(var) is dict:
        res = {}
        for k, v in var.items():
            res[k] = to_json(v)

    elif type(var) is list:
        res = []
        for v in var:
            res.append(to_json(v))

    else:
        res = var
    
    return res

