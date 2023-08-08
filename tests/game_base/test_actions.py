import pytest
from game_base.cards import Card
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from game_base.banks import Bank
from game_base.actions import (ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from tests.game_base.test_cards import TestingCardManager


class TestingReserve2SameColorTokens:
    def test_reserve_2_same_tokens_init_error_wildcard(self) -> None:
        color = Token.YELLOW
        with pytest.raises(ValueError) as e:
            action = Reserve2SameColorTokens(color)

    def test_reserve_2_same_tokens_can_perform_True(self) -> None:
        player_1 = Player('player_1')
        bank = Bank()
        color_1 = Token.GREEN
        action_1 = Reserve2SameColorTokens(color_1)
        assert action_1.can_perform(player_1, bank)

    def test_reserve_2_same_tokens_can_perform_False_bank(self) -> None:
        player_1 = Player('player_1')
        bank = Bank()
        color_1 = Token.GREEN
        action_1 = Reserve2SameColorTokens(color_1)
        bank.token_available.tokens[color_1] = 3
        assert not action_1.can_perform(player_1, bank)

    def test_reserve_2_same_tokens_can_perform_False_player(self) -> None:
        player_1 = Player('player_1')
        bank = Bank()
        color_1 = Token.GREEN
        action_1 = Reserve2SameColorTokens(color_1)
        for color in [Token.BLUE, Token.BLACK, Token.RED]:
            player_1.token_reserved.tokens[color] = 3
        assert not action_1.can_perform(player_1, bank)

    def test_reserve_2_same_tokens(self) -> None:
        player_1 = Player('player_1')
        player_2 = Player('player_2')
        bank = Bank(num_players=2)
        color_1 = Token.GREEN
        action_1 = Reserve2SameColorTokens(color_1)
        action_1.perform(player_1, bank)
        assert player_1.token_reserved == TokenBag().add({color_1: 2})
        assert bank.token_available == TokenBag(4, 5).remove({color_1: 2})
        color_2 = Token.RED
        action_2 = Reserve2SameColorTokens(color_2)
        action_2.perform(player_2, bank)
        assert player_2.token_reserved == TokenBag().add({color_2: 2})
        assert bank.token_available == TokenBag(4, 5).remove({color_1: 2,
                                                              color_2: 2})


class TestingReserve3UniqueColorTokens:
    def test_reserve_3_unique_tokens_init_error_ne_3(self) -> None:
        colors = (Token.GREEN, Token.WHITE)
        with pytest.raises(ValueError) as e:
            action = Reserve3UniqueColorTokens(colors)

    def test_reserve_3_unique_tokens_init_error_not_unique(self) -> None:
        colors = (Token.GREEN, Token.WHITE, Token.WHITE)
        with pytest.raises(ValueError) as e:
            action = Reserve3UniqueColorTokens(colors)

    def test_reserve_3_unique_tokens_init_error_wildcard(self) -> None:
        colors = (Token.GREEN, Token.WHITE, Token.YELLOW)
        with pytest.raises(ValueError) as e:
            action = Reserve3UniqueColorTokens(colors)

    def test_reserve_3_unique_tokens_can_perform_True(self) -> None:
        player_1 = Player('player_1')
        bank = Bank()
        colors = (Token.GREEN, Token.WHITE, Token.BLUE)
        action_1 = Reserve3UniqueColorTokens(colors)
        assert action_1.can_perform(player_1, bank)

    def test_reserve_3_unique_tokens_can_perform_False_bank(self) -> None:
        player_1 = Player('player_1')
        bank = Bank()
        colors = (Token.GREEN, Token.WHITE, Token.BLUE)
        action_1 = Reserve3UniqueColorTokens(colors)
        bank.token_available.tokens[colors[0]] = 0
        assert not action_1.can_perform(player_1, bank)

    def test_reserve_3_unique_tokens_can_perform_False_player(self) -> None:
        player_1 = Player('player_1')
        bank = Bank()
        colors = (Token.GREEN, Token.WHITE, Token.BLUE)
        action_1 = Reserve3UniqueColorTokens(colors)
        for color in [Token.BLUE, Token.BLACK, Token.RED, Token.WHITE]:
            player_1.token_reserved.tokens[color] = 2
        assert not action_1.can_perform(player_1, bank)

    def test_reserve_3_unique_tokens(self) -> None:
        player_1 = Player('player_1')
        player_2 = Player('player_2')
        bank = Bank(num_players=2)
        colors_1 = (Token.GREEN, Token.WHITE, Token.RED)
        action_1 = Reserve3UniqueColorTokens(colors_1)
        action_1.perform(player_1, bank)
        token_amounts_1 = dict.fromkeys(colors_1, 1)
        assert player_1.token_reserved == TokenBag().add(token_amounts_1)
        assert bank.token_available == TokenBag(4, 5).remove(token_amounts_1)
        colors_2 = (Token.BLACK, Token.BLUE, Token.RED)
        action_2 = Reserve3UniqueColorTokens(colors_2)
        action_2.perform(player_2, bank)
        token_amounts_2 = dict.fromkeys(colors_2, 1)
        assert player_2.token_reserved == TokenBag().add(token_amounts_2)
        assert bank.token_available == (TokenBag(4, 5)
                                        .remove(token_amounts_1)
                                        .remove(token_amounts_2))


class TestingReserveCard:
    def test_reserve_card(self) -> None:
        raise NotImplementedError


class TestingPurchaseCard:
    def test_purchase_card(self) -> None:
        raise NotImplementedError
