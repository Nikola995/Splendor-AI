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
    def test_bank_can_remove_token_3_unique(self) -> None:
        assert False

    def test_bank_can_remove_token_2_same(self) -> None:
        assert False

    def test_bank_can_remove_token_error(self) -> None:
        assert False


class TestingBankRemove3Unique:
    def test_bank_remove_token_3_unique(self) -> None:
        assert False

    def test_bank_remove_token_3_unique_error_not_3(self) -> None:
        assert False

    def test_bank_remove_token_3_unique_error_not_unique(self) -> None:
        assert False

    def test_bank_remove_token_3_unique_error_wildcard(self) -> None:
        assert False

    def test_bank_remove_token_3_unique_error_negative(self) -> None:
        assert False


class TestingBankRemove2Same:
    def test_bank_remove_token_2_same(self) -> None:
        assert False

    def test_bank_remove_token_2_same_error_wildcard(self) -> None:
        assert False

    def test_bank_remove_token_2_same_error_can_not_remove(self) -> None:
        assert False


class TestingBankRemoveWildcard:
    def test_bank_remove_wildcard(self) -> None:
        assert False

    def test_bank_remove_wildcard_error(self) -> None:
        assert False


class TestingBankAddToken:
    def test_bank_add_token_single(self) -> None:
        assert False

    def test_bank_add_token_multiple(self) -> None:
        assert False

    def test_bank_add_token_all(self) -> None:
        assert False


class TestingBankStr:
    def test_bank_str_default(self) -> None:
        assert False

    def test_bank_str_empty(self) -> None:
        assert False

    def test_bank_str_not_all(self) -> None:
        assert False

    def test_bank_str_remove(self) -> None:
        assert False
