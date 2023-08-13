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
    # FIXME: Update all tests to new version of purchase card
    def test_action_purchase_card_can_perform_False_all(self) -> None:
        # Check all possible scenarios when a player can't purchase a card
        bonus_color = Token.BLACK
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        tokens = {Token.GREEN: 2,
                  Token.BLUE: 2}
        collaterals = {Token.BLUE: 1,
                       Token.RED: 1}
        expected_cost = (TokenBag().add(bonuses).add(tokens).add(collaterals)
                         .add({Token.WHITE: 1}))
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        player = Player('test_player')
        bank = Bank()
        # Player has nothing
        assert not action.can_perform(player, bank)
        # Add the bonuses
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        # Player has just bonuses from owned cards
        assert not action.can_perform(player, bank)
        # Add the wildcard amounts
        bank.remove_token({Token.YELLOW: sum(collaterals.values())})
        player.add_token({Token.YELLOW: sum(collaterals.values())})
        # Player has bonuses from owned cards & wildcard collaterals
        assert not action.can_perform(player, bank)
        # Add the token amounts
        bank.remove_token(tokens)
        player.add_token(tokens)
        # Player has complete purchasing power
        assert not action.can_perform(player, bank)
        # Check that the complete purchasing power is not enough
        assert (expected_cost.tokens[Token.WHITE] >
                bonuses.get(Token.WHITE, 0) +
                tokens.get(Token.WHITE, 0) +
                collaterals.get(Token.WHITE, 0))

    def test_action_purchase_card_just_bonus(self) -> None:
        player = Player('test_player')
        bank = Bank()
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        bonus_card_prestige_points = 2
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, bonus_color=color,
                            prestige_points=bonus_card_prestige_points,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_bank = Bank()
        assert bank == expected_bank
        assert player.token_reserved == TokenBag()
        assert card_to_buy in player.cards_owned
        for color in bonuses:
            assert player.bonus_owned.tokens[color] == bonuses[color]
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert (player.prestige_points ==
                (bonus_card_prestige_points * sum(bonuses.values())
                 + card_prestige_points))

    def test_action_purchase_card_just_token(self) -> None:
        player = Player('test_player')
        bank = Bank()
        token_cost = {Token.GREEN: 1,
                      Token.BLUE: 2}
        token_extra = {Token.GREEN: 1,
                       Token.RED: 2}
        player.add_token(token_cost)
        player.add_token(token_extra)
        bank.remove_token(token_cost)
        bank.remove_token(token_extra)
        expected_cost = TokenBag().add(token_cost)
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_extra = TokenBag().add(token_extra)
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_action_purchase_card_just_wildcard(self) -> None:
        player = Player('test_player')
        bank = Bank()
        token_cost = {Token.BLUE: 1,
                      Token.RED: 1}
        expected_cost = TokenBag().add(token_cost)
        extra_wildcard = 1
        player.add_token({Token.YELLOW: (sum(token_cost.values()) +
                                         extra_wildcard)})
        bank.remove_token({Token.YELLOW: (sum(token_cost.values()))})
        bank.remove_token({Token.YELLOW: extra_wildcard})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_extra = (TokenBag()
                          .add({Token.YELLOW: extra_wildcard}))
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_action_purchase_card_no_bonus(self) -> None:
        player = Player('test_player')
        bank = Bank()
        # Add the regular tokens
        token_cost = {Token.GREEN: 2,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        player.add_token(token_cost)
        player.add_token(token_extra)
        bank.remove_token(token_cost)
        bank.remove_token(token_extra)
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 1
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        bank.remove_token({Token.YELLOW: sum(wildcard_cost.values())})
        bank.remove_token({Token.YELLOW: extra_wildcard})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = TokenBag().add(wildcard_cost).add(token_cost)
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_extra = (TokenBag()
                          .add({Token.YELLOW: extra_wildcard})
                          .add(token_extra))
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_action_purchase_card_no_token(self) -> None:
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        bonus_cost = {Token.GREEN: 3,
                      Token.BLUE: 2}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        bonus_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        for color in player.bonus_owned.tokens:
            assert (player.bonus_owned.tokens[color] ==
                    bonus_cost.get(color, 0) + bonus_extra.get(color, 0))
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 1
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        bank.remove_token({Token.YELLOW: (sum(wildcard_cost.values()))})
        bank.remove_token({Token.YELLOW: extra_wildcard})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = TokenBag().add(wildcard_cost).add(bonus_cost)
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_extra = (TokenBag()
                          .add({Token.YELLOW: extra_wildcard}))
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_action_purchase_card_no_wildcard(self) -> None:
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        bonus_cost = {Token.GREEN: 3,
                      Token.BLUE: 2}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        bonus_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        for color in player.bonus_owned.tokens:
            assert (player.bonus_owned.tokens[color] ==
                    bonus_cost.get(color, 0) + bonus_extra.get(color, 0))
        # Add the regular tokens
        token_cost = {Token.RED: 2,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        player.add_token(token_cost)
        player.add_token(token_extra)
        bank.remove_token(token_cost)
        bank.remove_token(token_extra)
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = TokenBag().add(token_cost).add(bonus_cost)
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_extra = TokenBag().add(token_extra)
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_action_purchase_card_all(self) -> None:
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        bonus_cost = {Token.GREEN: 3,
                      Token.BLUE: 2}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        bonus_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        for color in player.bonus_owned.tokens:
            assert (player.bonus_owned.tokens[color] ==
                    bonus_cost.get(color, 0) + bonus_extra.get(color, 0))
        # Add the regular tokens
        token_cost = {Token.RED: 2,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        player.add_token(token_cost)
        player.add_token(token_extra)
        bank.remove_token(token_cost)
        bank.remove_token(token_extra)
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 1
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        bank.remove_token({Token.YELLOW: (sum(wildcard_cost.values()))})
        bank.remove_token({Token.YELLOW: extra_wildcard})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = (TokenBag().add(wildcard_cost)
                         .add(bonus_cost).add(token_cost))
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        expected_extra = (TokenBag()
                          .add({Token.YELLOW: extra_wildcard})
                          .add(token_extra))
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_action_purchase_card_all_from_reserved(self) -> None:
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        bonus_cost = {Token.GREEN: 3,
                      Token.BLUE: 2}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        bonus_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        for color in player.bonus_owned.tokens:
            assert (player.bonus_owned.tokens[color] ==
                    bonus_cost.get(color, 0) + bonus_extra.get(color, 0))
        # Add the regular tokens
        token_cost = {Token.RED: 2,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        player.add_token(token_cost)
        player.add_token(token_extra)
        bank.remove_token(token_cost)
        bank.remove_token(token_extra)
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 1
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        bank.remove_token({Token.YELLOW: (sum(wildcard_cost.values()))})
        bank.remove_token({Token.YELLOW: extra_wildcard})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = (TokenBag().add(wildcard_cost)
                         .add(bonus_cost).add(token_cost))
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        action = PurchaseCard(card_to_buy)
        # Reserve the card before purchase
        player.add_to_reserved_cards(card_to_buy)
        assert player.num_reserved_cards == 1
        assert card_to_buy in player.cards_reserved
        action.perform(player, bank)
        expected_extra = (TokenBag()
                          .add({Token.YELLOW: extra_wildcard})
                          .add(token_extra))
        expected_bank = Bank()
        expected_bank.remove_token(expected_extra.tokens)
        assert bank == expected_bank
        assert player.token_reserved == expected_extra
        assert card_to_buy in player.cards_owned
        assert player.num_reserved_cards == 0
        assert card_to_buy not in player.cards_reserved
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points
