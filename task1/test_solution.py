import pytest
from solution import strict

def test_valid_types():
    @strict
    def func(a: int, b: str, c: float, d: bool) -> int:
        return a
    
    assert func(1, "test", 1.0, True) == 1

def test_invalid_int():
    @strict
    def func(a: int) -> int:
        return a
    
    with pytest.raises(TypeError):
        func(1.5)

def test_invalid_float():
    @strict
    def func(a: float) -> float:
        return a
    
    with pytest.raises(TypeError):
        func("1.5")

def test_invalid_str():
    @strict
    def func(a: str) -> str:
        return a
    
    with pytest.raises(TypeError):
        func(123)

def test_invalid_bool():
    @strict
    def func(a: bool) -> bool:
        return a
    
    with pytest.raises(TypeError):
        func(1)

def test_multiple_arguments():
    @strict
    def func(a: int, b: str) -> tuple:
        return a, b
    
    with pytest.raises(TypeError):
        func(1, 2)

def test_wrong_number_of_arguments():
    @strict
    def func(a: int, b: int) -> int:
        return a + b
    
    with pytest.raises(TypeError):
        func(1)

def test_provided_example():
    @strict
    def sum_two(a: int, b: int) -> int:
        return a + b
    
    assert sum_two(1, 2) == 3
    with pytest.raises(TypeError):
        sum_two(1, 2.4)