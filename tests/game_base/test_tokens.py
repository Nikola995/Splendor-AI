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
        token_bag = TokenBag()
        amounts = {Token.GREEN: 2}
        token_bag.add(amounts)
        expected = {Token.GREEN: 2,
                    Token.WHITE: 0,
                    Token.BLUE: 0,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 0}
        assert token_bag.tokens == expected

    def test_token_bag_default_add_multiple(self) -> None:
        token_bag = TokenBag()
        amounts = {Token.GREEN: 2,
                   Token.RED: 3}
        token_bag.add(amounts)
        expected = {Token.GREEN: 2,
                    Token.WHITE: 0,
                    Token.BLUE: 0,
                    Token.BLACK: 0,
                    Token.RED: 3,
                    Token.YELLOW: 0}
        assert token_bag.tokens == expected

    def test_token_bag_default_add_all(self) -> None:
        token_bag = TokenBag()
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 3}
        token_bag.add(amounts)
        expected = {Token.GREEN: 1,
                    Token.WHITE: 2,
                    Token.BLUE: 3,
                    Token.BLACK: 1,
                    Token.RED: 2,
                    Token.YELLOW: 3}
        assert token_bag.tokens == expected

    def test_token_bag_bank_4_init_add_single(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 2}
        token_bag.add(amounts)
        expected = {Token.GREEN: 9,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_bank_4_init_add_multiple(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 2,
                   Token.RED: 3}
        token_bag.add(amounts)
        expected = {Token.GREEN: 9,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 10,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_bank_4_init_add_all(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 3}
        token_bag.add(amounts)
        expected = {Token.GREEN: 8,
                    Token.WHITE: 9,
                    Token.BLUE: 10,
                    Token.BLACK: 8,
                    Token.RED: 9,
                    Token.YELLOW: 8}
        assert token_bag.tokens == expected

    def test_token_bag_add_expected_errors_single(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: -1}
        with pytest.raises(ValueError) as e:
            token_bag.add(amounts)

    def test_token_bag_add_expected_errors_multiple(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: -1}
        with pytest.raises(ValueError) as e:
            token_bag.add(amounts)

    def test_token_bag_bank_4_init_add_0(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        # Adding 0 shouldn't happen,
        # but at the same time shouldn't raise an error
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 0}
        token_bag.add(amounts)
        expected = {Token.GREEN: 8,
                    Token.WHITE: 9,
                    Token.BLUE: 10,
                    Token.BLACK: 8,
                    Token.RED: 9,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected


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

    def test_token_bag_default_remove_all(self) -> None:
        token_bag = TokenBag()
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 3}
        with pytest.raises(ValueError) as e:
            token_bag.remove(amounts)

    def test_token_bag_bank_4_init_remove_single(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 2}
        token_bag.remove(amounts)
        expected = {Token.GREEN: 5,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_bank_4_init_remove_multiple(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 1,
                   Token.RED: 1,
                   Token.WHITE: 1}
        token_bag.remove(amounts)
        expected = {Token.GREEN: 6,
                    Token.WHITE: 6,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 6,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_bank_4_init_remove_all(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 3}
        token_bag.remove(amounts)
        expected = {Token.GREEN: 6,
                    Token.WHITE: 5,
                    Token.BLUE: 4,
                    Token.BLACK: 6,
                    Token.RED: 5,
                    Token.YELLOW: 2}
        assert token_bag.tokens == expected

    def test_token_bag_remove_expected_errors_single(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: -1}
        with pytest.raises(ValueError) as e:
            token_bag.remove(amounts)

    def test_token_bag_remove_expected_errors_multiple(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: -1}
        with pytest.raises(ValueError) as e:
            token_bag.remove(amounts)

    def test_token_bag_bank_4_init_remove_0(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        # Removing 0 shouldn't happen,
        # but at the same time shouldn't raise an error
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 0}
        token_bag.remove(amounts)
        expected = {Token.GREEN: 6,
                    Token.WHITE: 5,
                    Token.BLUE: 4,
                    Token.BLACK: 6,
                    Token.RED: 5,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected


class TestingTokenBagAddAndRemove:
    def test_token_bag_add_and_remove_same_amount(self) -> None:
        token_bag = TokenBag()
        amounts = {Token.GREEN: 1}
        token_bag.add(amounts)
        token_bag.remove(amounts)
        expected = {Token.GREEN: 0,
                    Token.WHITE: 0,
                    Token.BLUE: 0,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 0}
        assert token_bag.tokens == expected

    def test_token_bag_add_and_remove_same_color(self) -> None:
        token_bag = TokenBag()
        amounts_to_add = {Token.GREEN: 3}
        amounts_to_remove = {Token.GREEN: 1}
        token_bag.add(amounts_to_add)
        token_bag.remove(amounts_to_remove)
        expected = {Token.GREEN: 2,
                    Token.WHITE: 0,
                    Token.BLUE: 0,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 0}
        assert token_bag.tokens == expected

    def test_token_bag_add_and_remove_different_color_single(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts_to_add = {Token.GREEN: 3}
        amounts_to_remove = {Token.RED: 1}
        token_bag.add(amounts_to_add)
        token_bag.remove(amounts_to_remove)
        expected = {Token.GREEN: 10,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 6,
                    Token.YELLOW: 5}
        assert token_bag.tokens == expected

    def test_token_bag_add_and_remove_different_color_multiple(self) -> None:
        token_bag = TokenBag(standard_amount=7, wildcard_amount=5)
        amounts_to_add = {Token.GREEN: 2,
                          Token.WHITE: 3,
                          Token.YELLOW: 1}
        amounts_to_remove = {Token.WHITE: 2,
                             Token.BLUE: 2,
                             Token.BLACK: 2}
        token_bag.add(amounts_to_add)
        token_bag.remove(amounts_to_remove)
        expected = {Token.GREEN: 9,
                    Token.WHITE: 8,
                    Token.BLUE: 5,
                    Token.BLACK: 5,
                    Token.RED: 7,
                    Token.YELLOW: 6}
        assert token_bag.tokens == expected

    def test_token_bag_add_and_remove_from_other_token_bag(self) -> None:
        token_bag = TokenBag()
        token_bag_to_add = TokenBag(standard_amount=5, wildcard_amount=4)
        token_bag_to_remove = TokenBag(standard_amount=3)
        token_bag.add(token_bag_to_add.tokens)
        token_bag.remove(token_bag_to_remove.tokens)
        expected = {Token.GREEN: 2,
                    Token.WHITE: 2,
                    Token.BLUE: 2,
                    Token.BLACK: 2,
                    Token.RED: 2,
                    Token.YELLOW: 1}
        assert token_bag.tokens == expected


class TestingTokenBagStr:
    def test_token_bag_str_default(self) -> None:
        pass

    def test_token_bag_str_single(self) -> None:
        pass

    def test_token_bag_str_multiple(self) -> None:
        pass

    def test_token_bag_str_all(self) -> None:
        pass
