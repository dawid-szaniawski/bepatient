from bepatient.waiter_src import comparators


def test_is_equal():
    assert comparators.is_equal(1, 1)
    assert not comparators.is_equal(1, 2)
    assert comparators.is_equal("abc", "abc")
    assert not comparators.is_equal("abc", "def")
    assert not comparators.is_equal([1, 2, 3], [1, 2])


def test_is_not_equal():
    assert not comparators.is_not_equal(1, 1)
    assert comparators.is_not_equal(1, 2)
    assert not comparators.is_not_equal("abc", "abc")
    assert comparators.is_not_equal("abc", "def")
    assert comparators.is_not_equal([1, 2, 3], [1, 2])


def test_is_greater_than():
    assert comparators.is_greater_than(2, 1)
    assert not comparators.is_greater_than(1, 2)
    assert comparators.is_greater_than(3.5, 2)
    assert not comparators.is_greater_than(2, 3.5)


def test_is_lesser_than():
    assert comparators.is_lesser_than(1, 2)
    assert not comparators.is_lesser_than(2, 1)
    assert comparators.is_lesser_than(2, 3.5)
    assert not comparators.is_lesser_than(3.5, 2)


def test_is_greater_than_or_equal():
    assert comparators.is_greater_than_or_equal(2, 1)
    assert comparators.is_greater_than_or_equal(2, 2)
    assert not comparators.is_greater_than_or_equal(1, 2)


def test_is_lesser_than_or_equal():
    assert comparators.is_lesser_than_or_equal(1, 2)
    assert comparators.is_lesser_than_or_equal(2, 2)
    assert not comparators.is_lesser_than_or_equal(2, 1)


def test_contain():
    assert comparators.contain([1, 2, 3], 1)
    assert not comparators.contain([1, 2, 3], 4)
    assert comparators.contain("abc", "a")
    assert not comparators.contain("abc", "d")


def test_not_contain():
    assert comparators.not_contain([1, 2, 3], 4)
    assert not comparators.not_contain([1, 2, 3], 1)
    assert comparators.not_contain("abc", "d")
    assert not comparators.not_contain("abc", "a")


def test_contain_all():
    assert comparators.contain_all([1, 2, 3], [1, 2])
    assert comparators.contain_all("abc", ["a", "b"])
    assert not comparators.contain_all([1, 2, 3], [1, 4])


def test_contain_any():
    assert comparators.contain_any([1, 2, 3], [1, 4])
    assert comparators.contain_any("abc", ["a", "d"])
    assert not comparators.contain_any([1, 2, 3], [4, 5])


def test_have_len_equal():
    assert comparators.have_len_equal([1, 2, 3], 3)
    assert comparators.have_len_equal("abc", 3)
    assert not comparators.have_len_equal([1, 2, 3], 2)


def test_have_len_greater():
    assert comparators.have_len_greater([1, 2, 3], 2)
    assert not comparators.have_len_greater("abc", 4)


def test_have_len_lesser():
    assert comparators.have_len_lesser("abc", 4)
    assert not comparators.have_len_lesser([1, 2, 3], 2)
