import pytest
from game_base.cards import Card
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from game_base.banks import Bank
from game_base.actions import (ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from game_base.games import Game, GameState
from tests.game_base.test_cards import TestingCardManager


class TestingGameAddPlayer:
    def test_game_adding_players(self) -> None:
        # Testing both can_add_player & add_player
        raise NotImplementedError()

    def test_game_can_add_player_False_player_exists(self) -> None:
        raise NotImplementedError()

    def test_game_can_add_player_False_game_in_progress(self) -> None:
        raise NotImplementedError()

    def test_game_can_add_player_False_too_many_players(self) -> None:
        raise NotImplementedError()

    def test_game_add_player_error_player_exists(self) -> None:
        raise NotImplementedError()

    def test_game_add_player_error_game_in_progress(self) -> None:
        raise NotImplementedError()

    def test_game_add_player_error_too_many_players(self) -> None:
        raise NotImplementedError()


class TestingGameRemovePlayer:
    def test_game_removing_players(self) -> None:
        # Testing both can_remove_player & remove_player
        raise NotImplementedError()

    def test_game_can_remove_player_False_not_player_exists(self) -> None:
        raise NotImplementedError()

    def test_game_can_remove_player_False_game_in_progress(self) -> None:
        raise NotImplementedError()

    def test_game_can_remove_player_False_not_player_exists(self) -> None:
        raise NotImplementedError()

    def test_game_remove_player_error_game_in_progress(self) -> None:
        raise NotImplementedError()


class TestingGameInit:

    def test_game_initialization_2_players(self) -> None:
        raise NotImplementedError()

    def test_game_initialization_3_players(self) -> None:
        raise NotImplementedError()

    def test_game_initialization_4_players(self) -> None:
        raise NotImplementedError()

    def test_game_can_initialize_False_min_players(self) -> None:
        raise NotImplementedError()

    def test_game_can_initialize_False_game_started(self) -> None:
        raise NotImplementedError()

    def test_game_initialization_error_min_players(self) -> None:
        with pytest.raises(ValueError) as e:
            raise NotImplementedError()

    def test_game_initialization_error_game_started(self) -> None:
        with pytest.raises(ValueError) as e:
            raise NotImplementedError()


class TestingGameProperties:
    def test_game_property_num_players(self) -> None:
        raise NotImplementedError()

    def test_game_property_current_player_idx(self) -> None:
        raise NotImplementedError()

    def test_game_property_current_player(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMoveReserve3UniqueColorTokens:

    def test_game_can_make_move_3_unique_tokens_True(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_3_unique_tokens_False_player(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_3_unique_tokens_False_bank(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_3_unique_tokens(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMoveReserve2SameColorTokens:

    def test_game_can_make_move_2_same_tokens_True(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_2_same_tokens_False_player(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_2_same_tokens_False_bank(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_2_same_tokens(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMoveReserveCard:

    def test_game_can_make_move_reserve_card_True(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_reserve_card_False(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_reserve_card_False_bank(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_reserve_card(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_reserve_card_no_wildcard_bank(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_reserve_card_no_wildcard_player(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMovePurchaseCard:
    def test_game_can_make_move_purchase_card_True(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_purchase_card_False_all(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_just_bonuses(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_just_wildcard(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_just_tokens(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_bonuses_and_wildcard(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_bonuses_and_tokens(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_wildcard_and_tokens_choose_wildcard(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_wildcard_and_tokens_choose_token(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_all(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_all_from_reserved(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_eligible_for_noble(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMoveEndTurn:
    def test_game_end_player_turn_default(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_multiple_players(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_another_turn(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_final_turn(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_final_turn_winner(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_final_turn_multiple_eligible_winner(self) -> None:
        raise NotImplementedError()
