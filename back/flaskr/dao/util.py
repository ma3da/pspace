import flaskr.config


def do_nothing(*args, **kwargs):
    return None


def find_params(*names, namespace=""):
    pfx = f"{namespace}_" if namespace else ''
    for name in names:
        yield flaskr.config.get(f"{pfx}{name}".upper(), _raise=True)


def find_params_dict(*names, namespace=""):
    return {k: v for k, v in zip(names, find_params(*names, namespace=namespace))}
