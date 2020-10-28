def do_nothing(*args, **kwargs):
    return None


def find_params(*names, namespace=""):
    """ find var names in os.environ, then hiddensettings.
        var `name` is looked for as environ.PSPACE_{NAMESPACE}_NAME and
        hiddensettings.{NAMESPACE}_NAME.
    """
    import os
    _fix = (namespace + '_') if namespace else ''
    def to_env(name): return f"PSPACE_{_fix}{name}".upper()
    def to_param(name): return f"{_fix}{name}".upper()
    for name in names:
        _var = to_env(name)
        if _var in os.environ:
            yield os.environ[_var]
        else:
            import flaskr.nocommit.hiddensettings as hs
            yield getattr(hs, to_param(name))


def find_params_dict(*names, namespace=""):
    return {k: v for k, v in zip(names, find_params(*names, namespace=namespace))}
