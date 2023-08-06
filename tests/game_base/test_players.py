from game_base.tokens import TokenBag
from game_base.players import Player


class TestingPlayer:
    def test_player_initialization_default(self) -> None:
        raise NotImplementedError()

    def test_player_can_remove_token_True(self) -> None:
        raise NotImplementedError()

    def test_player_can_remove_token_False(self) -> None:
        raise NotImplementedError()

    def test_player_remove_token(self) -> None:
        raise NotImplementedError()

    def test_player_remove_token_error_negative(self) -> None:
        raise NotImplementedError()

    def test_player_can_add_token_True(self) -> None:
        raise NotImplementedError()

    def test_player_can_add_token_False(self) -> None:
        raise NotImplementedError()

    def test_player_add_token(self) -> None:
        raise NotImplementedError()

    def test_player_add_token_error_check(self) -> None:
        raise NotImplementedError()

    def test_player_can_reserve_card_True(self) -> None:
        raise NotImplementedError()

    def test_player_can_reserve_card_False(self) -> None:
        raise NotImplementedError()

    def test_player_add_to_owned_cards(self) -> None:
        raise NotImplementedError()

    def test_player_is_eligible_for_noble(self) -> None:
        raise NotImplementedError()

    def test_player_add_noble(self) -> None:
        raise NotImplementedError()


class TestingPlayerCanPurchaseCard:
    def test_player_can_purchase_card(self) -> None:
        raise NotImplementedError()


class TestingPlayerStr:
    def test_player_str(self) -> None:
        raise NotImplementedError()
