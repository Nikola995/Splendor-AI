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
    def test_reserve_card_can_perform_True(self) -> None:
        cards = TestingCardManager.card_list_for_testing(num_cards=3)
        player = Player('player_1')
        bank = Bank()
        for card in cards:
            action = ReserveCard(card)
            assert action.can_perform(player, bank)
            action.perform(player, bank)

    def test_reserve_card_can_perform_False(self) -> None:
        cards = TestingCardManager.card_list_for_testing(num_cards=4)
        player = Player('player_1')
        bank = Bank()
        for card in cards[:3]:
            action = ReserveCard(card)
            assert action.can_perform(player, bank)
            action.perform(player, bank)
        action = ReserveCard(cards[-1])
        assert not action.can_perform(player, bank)

    def test_reserve_card_perform(self) -> None:
        cards = TestingCardManager.card_list_for_testing(num_cards=3)
        player = Player('player_1')
        bank = Bank()
        for card_idx, card in enumerate(cards):
            action = ReserveCard(card)
            action.perform(player, bank)
            assert player.num_reserved_cards == card_idx + 1
            assert player.token_reserved.tokens[Token.YELLOW] == card_idx + 1
            assert (bank.token_available.tokens[Token.YELLOW] ==
                    bank.initial_wildcard_token_amount - (card_idx + 1))

    def test_reserve_card_perform_no_wildcard_bank(self) -> None:
        cards = TestingCardManager.card_list_for_testing(num_cards=3)
        player = Player('player_1')
        bank = Bank()
        bank.initial_wildcard_token_amount = 2
        bank.token_available.tokens[Token.YELLOW] = 2
        for card_idx, card in enumerate(cards[:2]):
            action = ReserveCard(card)
            action.perform(player, bank)
            assert player.num_reserved_cards == card_idx + 1
            assert player.token_reserved.tokens[Token.YELLOW] == card_idx + 1
            assert (bank.token_available.tokens[Token.YELLOW] ==
                    bank.initial_wildcard_token_amount - (card_idx + 1))
        action = ReserveCard(cards[-1])
        action.perform(player, bank)
        assert player.num_reserved_cards == 3
        assert (player.token_reserved.tokens[Token.YELLOW] ==
                bank.initial_wildcard_token_amount)
        assert bank.token_available.tokens[Token.YELLOW] == 0

    def test_reserve_card_perform_no_wildcard_player(self) -> None:
        cards = TestingCardManager.card_list_for_testing(num_cards=3)
        player = Player('player_1')
        bank = Bank()
        for color in [Token.BLUE, Token.BLACK, Token.RED, Token.WHITE]:
            player.token_reserved.tokens[color] = 2
        for card_idx, card in enumerate(cards[:2]):
            action = ReserveCard(card)
            action.perform(player, bank)
            assert player.num_reserved_cards == card_idx + 1
            assert player.token_reserved.tokens[Token.YELLOW] == card_idx + 1
            assert (bank.token_available.tokens[Token.YELLOW] ==
                    bank.initial_wildcard_token_amount - (card_idx + 1))
        action = ReserveCard(cards[-1])
        action.perform(player, bank)
        assert player.num_reserved_cards == 3
        assert player.token_reserved.tokens[Token.YELLOW] == 2
        assert (bank.token_available.tokens[Token.YELLOW] ==
                bank.initial_wildcard_token_amount - 2)


class TestingPurchaseCard:
    def test_purchase_card(self) -> None:
        raise NotImplementedError
