import pytest
from game_base.tokens import Token, TokenBag
from game_base.banks import Bank
from game_base.utils import IncorrectInputError


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
        with pytest.raises(ValueError) as e:
            bank.can_remove_token(tokens_to_remove)


class TestingBankRemove3Unique:
    def test_bank_remove_token_3_unique(self) -> None:
        bank = Bank()
        tokens_to_remove = (Token.GREEN, Token.WHITE, Token.BLUE)
        bank.remove_3_unique_color_tokens(tokens_to_remove)
        expected = {Token.GREEN: 6,
                    Token.WHITE: 6,
                    Token.BLUE: 6,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert bank.token_available.tokens == expected

    def test_bank_remove_token_3_unique_error_ne_3(self) -> None:
        bank = Bank()
        tokens_to_remove = (Token.GREEN, Token.WHITE)
        with pytest.raises(IncorrectInputError) as e:
            bank.remove_3_unique_color_tokens(tokens_to_remove)

    def test_bank_remove_token_3_unique_error_not_unique(self) -> None:
        bank = Bank()
        tokens_to_remove = (Token.GREEN, Token.WHITE, Token.WHITE)
        with pytest.raises(IncorrectInputError) as e:
            bank.remove_3_unique_color_tokens(tokens_to_remove)

    def test_bank_remove_token_3_unique_error_wildcard(self) -> None:
        bank = Bank()
        tokens_to_remove = (Token.GREEN, Token.WHITE, Token.YELLOW)
        with pytest.raises(IncorrectInputError) as e:
            bank.remove_3_unique_color_tokens(tokens_to_remove)

    def test_bank_remove_token_3_unique_error_negative(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 0
        tokens_to_remove = (Token.GREEN, Token.WHITE, Token.BLUE)
        with pytest.raises(ValueError) as e:
            bank.remove_3_unique_color_tokens(tokens_to_remove)


class TestingBankRemove2Same:
    def test_bank_remove_token_2_same(self) -> None:
        bank = Bank()
        color = Token.GREEN
        bank.remove_2_same_color_tokens(color)
        expected = {Token.GREEN: 5,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 5}
        assert bank.token_available.tokens == expected

    def test_bank_remove_token_2_same_error_wildcard(self) -> None:
        bank = Bank()
        color = Token.YELLOW
        with pytest.raises(IncorrectInputError) as e:
            bank.remove_2_same_color_tokens(color)

    def test_bank_remove_token_2_same_error_can_not_remove(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 3
        color = Token.GREEN
        with pytest.raises(ValueError) as e:
            bank.remove_2_same_color_tokens(color)


class TestingBankRemoveWildcard:
    def test_bank_remove_wildcard(self) -> None:
        bank = Bank()
        bank.remove_wildcard_token()
        expected = {Token.GREEN: 7,
                    Token.WHITE: 7,
                    Token.BLUE: 7,
                    Token.BLACK: 7,
                    Token.RED: 7,
                    Token.YELLOW: 4}
        assert bank.token_available.tokens == expected

    def test_bank_remove_wildcard_error(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.YELLOW] = 0
        with pytest.raises(ValueError) as e:
            bank.remove_wildcard_token()


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
    def test_bank_str_default(self) -> None:
        bank = Bank()
        assert str(bank) == ("Available Bank tokens:\n"
                             "GREEN: 7\n"
                             "WHITE: 7\n"
                             "BLUE : 7\n"
                             "BLACK: 7\n"
                             "RED  : 7\n"
                             "YELLOW: 5")

    def test_bank_str_empty(self) -> None:
        bank = Bank()
        for color in bank.token_available.tokens:
            bank.token_available.tokens[color] = 0
        assert str(bank) == ("Available Bank tokens:\n")

    def test_bank_str_not_all(self) -> None:
        bank = Bank()
        bank.token_available.tokens[Token.GREEN] = 0
        assert str(bank) == ("Available Bank tokens:\n"
                             "WHITE: 7\n"
                             "BLUE : 7\n"
                             "BLACK: 7\n"
                             "RED  : 7\n"
                             "YELLOW: 5")

    def test_bank_str_post_remove(self) -> None:
        bank = Bank()
        tokens_to_remove = (Token.GREEN, Token.WHITE, Token.BLUE)
        bank.remove_3_unique_color_tokens(tokens_to_remove)
        assert str(bank) == ("Available Bank tokens:\n"
                             "GREEN: 6\n"
                             "WHITE: 6\n"
                             "BLUE : 6\n"
                             "BLACK: 7\n"
                             "RED  : 7\n"
                             "YELLOW: 5")
