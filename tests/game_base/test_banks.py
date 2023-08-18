import pytest
from game_base.tokens import Token, TokenBag
from game_base.banks import Bank


class TestingBankInit:
    def test_bank_initialization_default(self) -> None:
        bank = Bank()
        expected = TokenBag(standard_amount=7, wildcard_amount=5)
        assert bank.token_available == expected

    def test_bank_initialization_3_players(self) -> None:
        bank = Bank(num_players=3)
        expected = TokenBag(standard_amount=5, wildcard_amount=5)
        assert bank.token_available == expected

    def test_bank_initialization_2_players(self) -> None:
        bank = Bank(num_players=2)
        expected = TokenBag(standard_amount=4, wildcard_amount=5)
        assert bank.token_available == expected

    def test_bank_initialization_error(self) -> None:
        with pytest.raises(ValueError) as e:
            bank = Bank(1)


class TestingBankCanRemoveToken:
    def test_bank_can_remove_token_3_unique_true(self) -> None:
        bank = Bank()
        tokens_to_remove = {Token.GREEN: 1,
                            Token.WHITE: 1,
                            Token.BLUE: 1}
        assert bank.can_remove_token(tokens_to_remove)

    def test_bank_can_remove_token_3_unique_false(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 0
        tokens_to_remove = {Token.GREEN: 1,
                            Token.WHITE: 1,
                            Token.BLUE: 1}
        assert not bank.can_remove_token(tokens_to_remove)

    def test_bank_can_remove_token_2_same_true_gt_4(self) -> None:
        bank = Bank()
        tokens_to_remove = {Token.GREEN: 2}
        assert bank.can_remove_token(tokens_to_remove)

    def test_bank_can_remove_token_2_same_true_eq_4(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 4
        tokens_to_remove = {Token.GREEN: 2}
        assert bank.can_remove_token(tokens_to_remove)

    def test_bank_can_remove_token_2_same_true_lt_4(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 3
        tokens_to_remove = {Token.GREEN: 2}
        assert not bank.can_remove_token(tokens_to_remove)

    def test_bank_can_remove_token_error(self) -> None:
        bank = Bank()
        tokens_to_remove = {Token.GREEN: 1,
                            Token.WHITE: 1,
                            Token.BLUE: 3}
        with pytest.raises(NotImplementedError) as e:
            bank.can_remove_token(tokens_to_remove)


class TestingBankRemoveToken:
    def test_bank_remove_token_1_single(self) -> None:
        bank = Bank()
        color = Token.YELLOW
        tokens_to_remove = {color: 1}
        bank.remove_token(tokens_to_remove)
        expected = {Token.GREEN: 7,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 4}
        assert bank.token_available.tokens == expected

    def test_bank_remove_token_1_single_error(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.YELLOW] = 0
        color = Token.YELLOW
        tokens_to_remove = {color: 1}
        with pytest.raises(ValueError) as e:
            bank.remove_token(tokens_to_remove)

    def test_bank_remove_token_1_multiple(self) -> None:
        bank = Bank()
        colors = (Token.GREEN, Token.WHITE, Token.BLUE)
        tokens_to_remove = dict.fromkeys(colors, 1)
        bank.remove_token(tokens_to_remove)
        expected = {Token.GREEN: 6,
                    Token.WHITE: 6,
                    Token.BLUE: 6,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert bank.token_available.tokens == expected

    def test_bank_remove_token_1_multiple_error(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 0
        colors = (Token.GREEN, Token.WHITE, Token.BLUE)
        tokens_to_remove = dict.fromkeys(colors, 1)
        with pytest.raises(ValueError) as e:
            bank.remove_token(tokens_to_remove)

    def test_bank_remove_token_2(self) -> None:
        bank = Bank()
        color = Token.GREEN
        tokens_to_remove = {color: 2}
        bank.remove_token(tokens_to_remove)
        expected = {Token.GREEN: 5,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert bank.token_available.tokens == expected

    def test_bank_remove_token_2_error(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 3
        color = Token.GREEN
        tokens_to_remove = {color: 2}
        with pytest.raises(ValueError) as e:
            bank.remove_token(tokens_to_remove)


class TestingBankAddToken:
    def test_bank_add_token_single(self) -> None:
        bank = Bank()
        amounts = {Token.GREEN: 2}
        bank.add_token(amounts)
        expected = {Token.GREEN: 9,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert bank.token_available.tokens == expected

    def test_bank_add_token_multiple(self) -> None:
        bank = Bank()
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3}
        bank.add_token(amounts)
        expected = {Token.GREEN: 8,
                    Token.WHITE: 9,
                    Token.BLUE: 10,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert bank.token_available.tokens == expected

    def test_bank_add_token_all(self) -> None:
        bank = Bank()
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 3,
                   Token.BLACK: 1,
                   Token.RED: 2,
                   Token.YELLOW: 3}
        bank.add_token(amounts)
        expected = {Token.GREEN: 8,
                    Token.WHITE: 9,
                    Token.BLUE: 10,
                    Token.BLACK: 8,
                    Token.RED: 9,
                    Token.YELLOW: 8}
        assert bank.token_available.tokens == expected


class TestingBankStr:
    def test_bank_str_default_all(self) -> None:
        bank = Bank()
        assert str(bank) == ("Available Bank tokens:\n"
                             "Green: 7\n"
                             "White: 7\n"
                             "Blue : 7\n"
                             "Black: 7\n"
                             "Red  : 7\n"
                             "Yellow: 5")

    def test_bank_str_default_none(self) -> None:
        bank = Bank()
        for color in bank.token_available.tokens:
            bank.token_available.tokens[color] = 0
        assert str(bank) == ("Available Bank tokens:\n")

    def test_bank_str_any(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 0
        assert str(bank) == ("Available Bank tokens:\n"
                             "White: 7\n"
                             "Blue : 7\n"
                             "Black: 7\n"
                             "Red  : 7\n"
                             "Yellow: 5")

    def test_bank_str_post_remove(self) -> None:
        bank = Bank()
        colors = (Token.GREEN, Token.WHITE, Token.BLUE)
        tokens_to_remove = dict.fromkeys(colors, 1)
        bank.remove_token(tokens_to_remove)
        assert str(bank) == ("Available Bank tokens:\n"
                             "Green: 6\n"
                             "White: 6\n"
                             "Blue : 6\n"
                             "Black: 7\n"
                             "Red  : 7\n"
                             "Yellow: 5")
