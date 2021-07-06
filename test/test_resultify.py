# pyright: reportWildcardImportFromLibrary=false

import pytest

from resultify import Err, Ok, UnwrapError, resultify


class TestOk:
    def test_indicators(self):
        ok = Ok()
        assert ok.is_ok() is True
        assert ok.is_err() is False

    def test_default_constructor(self):
        ok = Ok()
        assert ok.ok() is True

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
        err = Err()
        assert err.is_ok() is False
        assert err.is_err() is True

    def test_default_contructor(self):
        err = Err()
        assert err.err() is True

    def test_parameterized_contructor(self):
        value = "value"
        err = Err(value)
        assert err.err() == value

    def test_err_getter_raises(self):
        err = Err()
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
        assert Ok(1) == Ok(1)
        assert Err(1) == Err(1)
        assert Ok(1) != Err(1)
        assert Ok(1) != Ok(2)
        assert Err(1) != Err(2)
        assert not (Ok(1) != Ok(1))
        assert Ok(1) != "abc"
        assert Ok("0") != Ok(0)

    def test_hash(self):
        assert len({Ok(1), Err("2"), Ok(1), Err("2")}) == 2
        assert len({Ok(1), Ok(2)}) == 2
        assert len({Ok("a"), Err("a")}) == 2

    def test_repr(self):
        assert Ok(u"£10") == eval(repr(Ok(u"£10")))
        assert Ok("£10") == eval(repr(Ok("£10")))

    def test_isinstance_result_type(self):
        o = Ok("yay")
        n = Err("nay")
        assert isinstance(o, (Ok, Err))
        assert isinstance(n, (Ok, Err))
