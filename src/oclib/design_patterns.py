from typing import Any, Callable


class Factory:
    def __init__(self, _cls: Callable, *args, **kwargs):
        self.__cls = _cls
        self.__args = args
        self.__kwargs = kwargs

    def create(self) -> Any:
        return self.__cls(*self.__args, **self.__kwargs)

