import pytest
from game_base.tokens import Token, TokenBag


class TestingTokenBagInit:
    def test_token_bag_initialization_default(self) -> None:
        token_bag = TokenBag()
        expected = {Token.GREEN: 0,
                    Token.WHITE: 0,
                    Token.BLUE: 0,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 0}
        assert token_bag.tokens == expected

    def test_token_bag_initialization_just_standard_amount(self) -> None:
        token_bag = TokenBag(standard_amount=5)
        expected = {Token.GREEN: 5,
                    Token.WHITE: 5,
                    Token.BLUE: 5,
                    Token.BLACK: 5,
                    Token.RED: 5,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_initialization_just_wildcard_amount(self) -> None:
        token_bag = TokenBag(wildcard_amount=5)
        expected = {Token.GREEN: 0,
                    Token.WHITE: 0,
                    Token.BLUE: 0,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_initialization_different_values(self) -> None:
        token_bag = TokenBag(standard_amount=5, wildcard_amount=3)
        expected = {Token.GREEN: 5,
                    Token.WHITE: 5,
                    Token.BLUE: 5,
                    Token.BLACK: 5,
                    Token.RED: 5,
                    Token.YELLOW: 3}
        assert token_bag.tokens == expected

    def test_token_bag_initialization_same_values(self) -> None:
        token_bag = TokenBag(standard_amount=5, wildcard_amount=5)
        expected = {Token.GREEN: 5,
                    Token.WHITE: 5,
                    Token.BLUE: 5,
                    Token.BLACK: 5,
                    Token.RED: 5,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_initialization_negative_value_1(self) -> None:
        with pytest.raises(ValueError) as e:
            token_bag = TokenBag(standard_amount=-5,
                                 wildcard_amount=5)

    def test_token_bag_initialization_negative_value_2(self) -> None:
        with pytest.raises(ValueError) as e:
            token_bag = TokenBag(standard_amount=5,
                                 wildcard_amount=-5)

    def test_token_bag_initialization_negative_value_3(self) -> None:
        with pytest.raises(ValueError) as e:
            token_bag = TokenBag(standard_amount=-5,
                                 wildcard_amount=-5)


class TestingTokenBagAdd:
    def test_token_bag_default_add_single(self) -> None:
        token_bag = TokenBag(standard_amount=0)
        amounts = {Token.GREEN: 2}
        token_bag.add(amounts)
        assert token_bag.tokens[Token.GREEN] == 2

    def test_token_bag_default_add_multiple(self) -> None:
        token_bag = TokenBag(standard_amount=0)
        amounts = {Token.GREEN: 2, Token.RED: 3}
        token_bag.add(amounts)
        assert token_bag.tokens[Token.GREEN] == 2
        assert token_bag.tokens[Token.RED] == 3

    def test_token_bag_default_add_all(self) -> None:
        token_bag = TokenBag(standard_amount=0)
        amounts = {Token.GREEN: 1,
                         Token.WHITE: 2,
                         Token.BLUE: 3,
                         Token.BLACK: 1,
                         Token.RED: 2,
                         Token.YELLOW: 3}
        token_bag.add(amounts)
        assert token_bag.tokens[Token.GREEN] == 1
        assert token_bag.tokens[Token.WHITE] == 2
        assert token_bag.tokens[Token.BLUE] == 3
        assert token_bag.tokens[Token.BLACK] == 1
        assert token_bag.tokens[Token.RED] == 2
        assert token_bag.tokens[Token.YELLOW] == 3


class TestingTokenBagRemove:
    def test_token_bag_default_remove_single(self) -> None:
        token_bag = TokenBag()
        amounts = {Token.GREEN: 1}
        with pytest.raises(ValueError) as e:
            token_bag.remove(amounts)

    def test_token_bag_default_remove_multiple(self) -> None:
        token_bag = TokenBag()
        amounts = {Token.GREEN: 2, Token.RED: 3}
        with pytest.raises(ValueError) as e:
            token_bag.remove(amounts)