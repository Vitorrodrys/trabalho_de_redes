from inspect import signature
from functools import wraps
from typing import Callable

class CommandRegistry:
    def __init__(self):
        self.command_map:dict[str, Callable] = {}

    def add(self, command_name)->Callable:
        """
        Provides a decorator to register a function with a command name.
        """
        def decorator(func:Callable):
            # Registry the function with the command name
            self.command_map[command_name] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                sig = signature(func)
                bound_values = sig.bind_partial(*args, **kwargs).arguments

                for name, value in bound_values.items():
                    if name in sig.parameters:
                        param = sig.parameters[name]
                        if param.annotation != param.empty:
                            try:
                                bound_values[name] = param.annotation(value)
                            except ValueError as e:
                                raise TypeError(f"Failed to convert parameter '{name}' to {param.annotation}") from e

                return func(*bound_values.values())

            return wrapper

        return decorator

    def get_command(self, command_name:str)->Callable:
        """
        Return the specified command function mapped to the command name.
        """
        return self.command_map.get(command_name, None)
