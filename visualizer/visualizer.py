from bytecode import Bytecode, Instr

class get_local(object):
    cache = {}
    is_activate = False

    def __init__(self, varnames):
        self.varnames = [varnames] if isinstance(varnames, str) else varnames

    def __call__(self, func):
        if not type(self).is_activate:
            return func

        for varname in self.varnames:
            type(self).cache[func.__qualname__+'.'+varname] = []
        c = Bytecode.from_code(func.__code__)
        extra_code = [
                         Instr('STORE_FAST', '_res'),
                         *sum([[Instr('LOAD_FAST', varname), Instr('STORE_FAST', f'_value_{varname}')] for varname in self.varnames], []),
                         Instr('LOAD_FAST', '_res'),
                         *[Instr('LOAD_FAST', f'_value_{varname}') for varname in self.varnames],
                         Instr('BUILD_TUPLE', 1+len(self.varnames)),
                         Instr('STORE_FAST', '_result_tuple'),
                         Instr('LOAD_FAST', '_result_tuple'),
                     ]
        c[-1:-1] = extra_code
        func.__code__ = c.to_code()

        def wrapper(*args, **kwargs):
            res_values = func(*args, **kwargs)
            res, values = res_values[0], res_values[1:]
            for i,varname in enumerate(self.varnames):
                type(self).cache[func.__qualname__+'_'+varname].append(values[i].detach().cpu())
            return res
        return wrapper

    @classmethod
    def clear(cls):
        for key in cls.cache.keys():
            cls.cache[key] = []

    @classmethod
    def activate(cls, activate=True):
        cls.is_activate = activate
