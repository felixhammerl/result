from time import sleep
from functools import wraps

try:
    from typing import Any, Generic, ParamSpec, TypeVar, Union, Type, Callable
except ImportError:
    from typing_extensions import (
        Any,
        Generic,
        ParamSpec,
        TypeVar,
        Union,
        Type,
        Callable,
    )

T = TypeVar("T", bound=Any)  # Success type
E = TypeVar("E", bound=Exception)  # Error type
P = ParamSpec("P")


class Ok(Generic[T]):
    """
    A value that indicates success and which stores arbitrary data for the return value.
    """

    __match_args__ = ("_value",)

    def __init__(self, value: T = True) -> None:
        self._value = value

    def __repr__(self) -> str:
        return "Ok({})".format(repr(self._value))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ok) and self._value == other._value

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((True, self._value))

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def ok(self) -> T:
        """
        Return the value.
        """
        return self._value

    def err(self):
        """
        Throws UnwrapError
        """
        raise UnwrapError(message=f"Cannot unwrap error from Ok: {self}")


class Err(Generic[E]):
    """
    A value that signifies failure and which stores arbitrary data for the error.
    """

    __match_args__ = ("_value",)

    def __init__(self, value: E = True) -> None:
        self._value = value

    def __repr__(self) -> str:
        return "Err({})".format(repr(self._value))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Err) and self._value == other._value

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((False, self._value))

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def ok(self):
        """
        Throws UnwrapError
        """
        raise UnwrapError(message=f"Cannot unwrap value from Err: {self}")

    def err(self) -> E:
        """
        Return the error.
        """
        return self._value


"""
A simple `Result` type inspired by Rust. Not all functions have been implemented.
Since Rust"s Optional type does not meaningfully translate to Python, ok() corresponds to unwrap() and err() corresponds to unwrap_err().
"""
Result = Union[Ok[T], Err[E]]


class UnwrapError(Exception):
    """
    Exception thrown upon invoking `.ok()` on instance of `Error` and `.err()` on instance of `Ok`
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


def resultify(
    *errors: Type[E],
) -> Callable[[Callable[P, T]], Callable[P, Result[T, E]]]:
    def decorator(function: Callable[P, T]) -> Callable[P, Result[T, E]]:
        @wraps(function)
        def inner(*args, **kwargs):
            try:
                return Ok(function(*args, **kwargs))
            except errors as e:
                return Err(e)

        return inner

    return decorator


def retry(retries: int = 0, delay: int = 0, initial_delay: int = 0):
    def decorator(
        function: Callable[..., Union[Ok[T], Err[E]]]
    ) -> Callable[..., Union[Ok[T], Err[E]]]:
        @wraps(function)
        def func_with_retries(*args, **kwargs) -> Union[Ok[T], Err[E]]:
            sleep(initial_delay)
            _retries = retries
            res: Union[Ok[T], Err[E]] = function(*args, **kwargs)
            while _retries >= 1:
                if res.is_ok():
                    break
                sleep(delay)
                _retries -= 1
                res = function(*args, **kwargs)
            return res

        return func_with_retries

    return decorator
