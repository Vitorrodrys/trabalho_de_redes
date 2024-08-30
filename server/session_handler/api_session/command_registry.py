from inspect import signature
from functools import wraps
from typing import Callable, Optional


class CommandRegistry:
    def __init__(self):
        self.command_map: dict[str, Callable] = {}

    def add(self, command_name: str) -> Callable:
        """
        Provides a decorator to register a function with a command name.
        """

        def decorator(func: Callable):
            if command_name in self.command_map:
                raise ValueError(f"Command '{command_name}' is already registered.")

            @wraps(func)
            def wrapper(*args, **kwargs):
                sig = signature(func)
                bound_values = sig.bind_partial(*args, **kwargs).arguments

                for name, value in bound_values.items():
                    if name in sig.parameters:
                        param = sig.parameters[name]
                        if param.annotation != param.empty and value is not None:
                            try:
                                bound_values[name] = param.annotation(value)
                            except (ValueError, TypeError) as e:
                                raise TypeError(
                                    f"Failed to convert parameter '{name}' to {param.annotation}: {value}"
                                ) from e

                return func(*bound_values.values())

            self.command_map[command_name] = wrapper
            return wrapper

        return decorator

    def get_command(self, command_name: str) -> Optional[Callable]:
        """
        Return the specified command function mapped to the command name.
        """
        return self.command_map.get(command_name, None)
