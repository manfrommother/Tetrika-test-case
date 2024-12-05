from functools import wraps

def strict(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        #получаем аннотации типов
        annotations = {k: v for k, v in func.__annotations__.items() if k != 'return'}

        if len(args) != len(annotations):
            raise TypeError(f'Ожидалось {len(annotations)} аргументов, аргументов получено {len(args)}')
        
        for arg_value, (arg_name, expected_type) in zip(args, annotations.items()):
            if not isinstance(arg_value, expected_type):
                raise TypeError(
                    f'Аргумент "{arg_name}" должен быть {expected_type.__name__},'
                    f'но он {type(arg_value).__name__}'
                )
        return func(*args, *kwargs)
    
    return wrapper