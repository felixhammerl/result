# pyright: reportWildcardImportFromLibrary=false

import pytest

from resultify import Err, Ok, UnwrapError, resultify, retry


class TestOk:
    def test_indicators(self):
        ok = Ok()
        assert ok.is_ok() is True
        assert ok.is_err() is False

    def test_default_constructor(self):
        ok = Ok()
        assert ok.ok() is None

    def test_parameterized_constructor(self):
        value = "value"
        ok = Ok(value)
        assert ok.is_ok() is True
        assert ok.ok() == value

    def test_getter_raises(self):
        ok = Ok()
        with pytest.raises(UnwrapError):
            ok.err()


class TestErr:
    def test_indicators(self):
        err = Err(ValueError())
        assert err.is_ok() is False
        assert err.is_err() is True

    def test_parameterized_contructor(self):
        value = ValueError()
        err = Err(value)
        assert err.err() == value

    def test_err_getter_raises(self):
        value = ValueError()
        err = Err(value)
        with pytest.raises(UnwrapError):
            err.ok()


class TestResultify:
    def test_should_resultify_to_ok(self):
        val = "asd"

        @resultify()
        def foo():
            return val

        x = foo()
        assert isinstance(x, Ok)
        assert x.ok() == val

    def test_should_not_catch_exception_when_none_provided(self):
        val = TypeError()

        @resultify()
        def foo():
            raise val

        with pytest.raises(TypeError):
            foo()

    def test_should_resultify_to_err(self):
        val = TypeError()

        @resultify(TypeError)
        def foo():
            raise val

        x = foo()
        assert isinstance(x, Err)
        assert x.err() == val

    def test_should_resultify_to_err_with_multiple_exceptions(self):
        class MyException(Exception):
            pass

        class MyOtherException(Exception):
            pass

        @resultify(MyException, MyOtherException)
        def foo(a: bool):
            if a:
                raise MyException()
            else:
                raise MyOtherException()

        assert isinstance(foo(True).err(), MyException)
        assert isinstance(foo(False).err(), MyOtherException)


class TestDunderMethods:
    def test_eq(self):
        value = ValueError()
        other_value = ValueError()
        assert Ok(1) == Ok(1)
        assert Err(value) == Err(value)
        assert Ok(1) != Err(value)
        assert Ok(1) != Ok(2)
        assert Err(value) != Err(other_value)
        assert not (Ok(1) != Ok(1))
        assert Ok(1) != "abc"
        assert Ok("0") != Ok(0)

    def test_hash(self):
        value = ValueError()
        assert len({Ok(1), Err(value), Ok(1), Err(value)}) == 2
        assert len({Ok(1), Ok(2)}) == 2
        assert len({Ok("a"), Err(value)}) == 2

    def test_repr(self):
        assert Ok("£10") == eval(repr(Ok("£10")))
        assert Ok("£10") == eval(repr(Ok("£10")))

    def test_isinstance_result_type(self):
        value = ValueError()
        o = Ok("yay")
        n = Err(value)
        assert isinstance(o, (Ok, Err))
        assert isinstance(n, (Ok, Err))


class TestRetry:
    def test_retry_fail(self):
        class Config:
            value = "asdfasdfasdf"
            counter = 0
            failing_tries = 999
            retries = 2

        config = Config()

        @retry(retries=config.retries)
        @resultify(Exception)
        def foo():
            config.counter += 1
            if config.counter <= config.failing_tries:
                raise TypeError()
            else:
                return config.value

        x = foo()
        assert isinstance(x, Err)
        assert config.counter == 3

    def test_retry_ok(self):
        class Config:
            value = "asdfasdfasdf"
            counter = 0
            failing_tries = 2
            retries = 2

        config = Config()

        @retry(retries=config.retries)
        @resultify(Exception)
        def foo():
            config.counter += 1
            if config.counter <= config.failing_tries:
                raise TypeError()
            else:
                return config.value

        x = foo()
        assert isinstance(x, Ok)
        assert x.ok() == config.value
        assert config.counter == 3
