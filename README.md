# Resultify

This is an opinionated, simplified fork of [dbrgn/result](https://github.com/dbrgn/result).

Result is a simple, type annotated Result type for Python 3.6+ inspired by [Rust](https://doc.rust-lang.org/std/result/).

The idea is that a result value can be either `Ok(value)` or `Err(error)`, with a way to differentiate between the two. `Ok` and `Err` are both classes wrapping an arbitrary value. `Result[T, E]` is a generic type alias for `typing.Union[Ok[T], Err[E]]`.

Requires Python 3.8 or higher!

NB: If you are using a Python version lower than 3.10, you will have to install `typing_extensions`!


### Caveats

Not all [methods](https://doc.rust-lang.org/std/result/enum.Result.html) have been implemented, only the ones that make sense in the Python context. For example, the `map` methods have been omitted, because they don't quite make sense without Rust's pattern matching.

Since Rust's Optional type does not meaningfully translate to Python in a way type checkers are able to understand, `ok()` corresponds to `unwrap()` and `err()` corresponds to `unwrap_err()`. On the other side, you don't have to return semantically unclear tuples anymore.

By using `.is_ok()` and `is_err()` to check for `Ok` or `Err` you get type safe access to the contained value. All of this in a package allowing easier handling of values that can be OK or not, without resorting to custom exceptions.


### API

Creating an instance:

```py
>>> from resultify import Ok, Err
>>> ok = Ok('yay')
>>> res2 = Err('nay')
```

Type safe checking whether a result is `Ok` or `Err`.

```py
>>> res = Ok('yay')
>>> res.is_ok()
True
>>> res.is_err()
False
```

Unwrap a `Result`, or raise if trying to extract a result from an error from a result or vice-versa:

```py
>>> ok = Ok('yay')
>>> err = Err('nay')
>>> ok.ok()
'yay'
>>> ok.err()
resultify.UnwrapError: Cannot unwrap error from Ok: Ok('yay')
>>> err.err()
'nay'
>>> err.ok()
resultify.UnwrapError: Cannot unwrap value from Err: Err('nay')
```

For your convenience, and to appease the type checkers, simply creating an `Ok` result without value is the same as using `True`:

```py
>>> ok = Ok()
>>> ok.ok()
True
```

To easily convert a function to return `Result`, you can use `resultify()`:

```py
>>> from resultify import resultify
>>> @resultify()
... def a():
...     return "value"
...
>>> a()
Ok('value')
```

You can similarly auto-capture exceptions using `resultify(...)`. Please note that you can provide multiple exceptions, or none if you don't want to catch the exception! This is primarily useful when modeling code paths with a single good branch and multiple early `raise`s, where one does not have to concern oneself with annoying `try ... catch ...` statements.

```py
>>> @resultify(TypeError)
... def foo():
...     raise TypeError()
...
>>> foo()
Err(TypeError())
```


You can `retry` a function that returns a `Result` type with a constant backoff.

```py
>>> from resultify import resultify, retry
... @retry(retries=2, delay=2, initial_delay=1):
... @resultify(Exception)
... def foo():
...     # do something that needs retrying here
```

This example waits 1 second before executing the initial call, then attempts the initial call, then executes two retries, spaces out two seconds from the previous call. If any execution was a success, the `Ok` value will be returned. If the retries were exhausted and no `Ok` was returned, we return the `Err` value.

For those running Python 3.10, you can make use of Python's **structural pattern** matching like this:

```py
>>> from resultify import Ok, Err
>>> ok = Ok("ok!")
>>> match ok:
...     case Ok(foo): print(f"Yay {foo}")
...     case Err(foo): print(f"Nay {foo}")
...
Yay ok!
>>> no = Err("nope!")
>>> match no:
...     case Ok(foo): print(f"Yay {foo}")
...     case Err(foo): print(f"Nay {foo}")
...
Nay nope!
```


Since documentation always lies, please refer to the unit tests for examples of usage.


### License

MIT License

