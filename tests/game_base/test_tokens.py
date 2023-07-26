import pytest
from game_base.tokens import Token, TokenBag


def test_token_bag_initialization_default() -> None:
    token_bag = TokenBag()
    expected = {Token.GREEN: 0,
                Token.WHITE: 0,
                Token.BLUE: 0,
                Token.BLACK: 0,
                Token.RED: 0,
                Token.YELLOW: 0}
    assert token_bag.tokens == expected


def test_token_bag_initialization_just_standard_amount() -> None:
    token_bag = TokenBag(standard_amount=5)
    expected = {Token.GREEN: 5,
                Token.WHITE: 5,
                Token.BLUE: 5,
                Token.BLACK: 5,
                Token.RED: 5,
                Token.YELLOW: 5}
    assert token_bag.tokens == expected


def test_token_bag_initialization_just_wildcard_amount() -> None:
    token_bag = TokenBag(wildcard_amount=5)
    expected = {Token.GREEN: 0,
                Token.WHITE: 0,
                Token.BLUE: 0,
                Token.BLACK: 0,
                Token.RED: 0,
                Token.YELLOW: 5}
    assert token_bag.tokens == expected


def test_token_bag_initialization_different_values() -> None:
    token_bag = TokenBag(standard_amount=5, wildcard_amount=3)
    expected = {Token.GREEN: 5,
                Token.WHITE: 5,
                Token.BLUE: 5,
                Token.BLACK: 5,
                Token.RED: 5,
                Token.YELLOW: 3}
    assert token_bag.tokens == expected


def test_token_bag_initialization_same_values() -> None:
    token_bag = TokenBag(standard_amount=5, wildcard_amount=5)
    expected = {Token.GREEN: 5,
                Token.WHITE: 5,
                Token.BLUE: 5,
                Token.BLACK: 5,
                Token.RED: 5,
                Token.YELLOW: 5}
    assert token_bag.tokens == expected


def test_token_bag_initialization_negative_value_1() -> None:
    with pytest.raises(ValueError) as e:
        token_bag = TokenBag(standard_amount=-5,
                             wildcard_amount=5)


def test_token_bag_initialization_negative_value_2() -> None:
    with pytest.raises(ValueError) as e:
        token_bag = TokenBag(standard_amount=5,
                             wildcard_amount=-5)


def test_token_bag_initialization_negative_value_3() -> None:
    with pytest.raises(ValueError) as e:
        token_bag = TokenBag(standard_amount=-5,
                             wildcard_amount=-5)
