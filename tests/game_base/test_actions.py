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
    def test_purchase_card_just_bonuses(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 4,
                 Token.BLUE: 2}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        for color in costs:
            for _ in range(costs[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        # Perform action
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        assert bank == Bank()

    def test_purchase_card_just_wildcard(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2}
        card_prestige_points = 1
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the wildcard amounts
        wildcard_amounts = {Token.YELLOW: 2}
        bank.remove_token(wildcard_amounts)
        player.add_token(wildcard_amounts)
        # Perform action
        action = PurchaseCard(card_to_buy, costs)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        assert player.token_reserved == TokenBag()
        assert bank == Bank()

    def test_purchase_card_just_tokens(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 1}
        card_prestige_points = 1
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the token amounts
        bank.remove_token(costs)
        player.add_token(costs)
        # Perform action
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        assert player.token_reserved == TokenBag()
        assert bank == Bank()

    def test_purchase_card_bonuses_and_wildcard(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 4,
                 Token.BLUE: 2}
        wildcard_collaterals = {Token.WHITE: 1,
                                Token.BLUE: 1}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        for color in costs:
            for _ in range(costs[color] - wildcard_collaterals.get(color, 0)):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        # Add the wildcard amounts
        wildcard_amounts = {Token.YELLOW: 2}
        bank.remove_token(wildcard_amounts)
        player.add_token(wildcard_amounts)
        # Perform action
        action = PurchaseCard(card_to_buy, wildcard_collaterals)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        assert bank == Bank()

    def test_purchase_card_bonuses_and_tokens(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 4,
                 Token.BLUE: 2}
        token_collaterals = {Token.WHITE: 1,
                             Token.BLUE: 1}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        for color in costs:
            for _ in range(costs[color] - token_collaterals.get(color, 0)):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        # Add the token amounts
        bank.remove_token(token_collaterals)
        player.add_token(token_collaterals)
        # Perform action
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        assert bank == Bank()

    def test_purchase_card_wildcard_and_tokens_choose_wildcard(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 2,
                 Token.BLUE: 2}
        wildcard_collaterals = {Token.WHITE: 1,
                                Token.BLUE: 1}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the wildcard amounts
        wildcard_amounts = {Token.YELLOW: 2}
        bank.remove_token(wildcard_amounts)
        player.add_token(wildcard_amounts)
        # Add the token amounts
        bank.remove_token(costs)
        player.add_token(costs)
        # Perform action with wildcard collaterals
        action = PurchaseCard(card_to_buy, wildcard_collaterals)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        # The player should keep the regular token amounts equal to the
        # wildcard collaterals for each color
        expected_bank = Bank()
        expected_bank.remove_token(wildcard_collaterals)
        assert bank == expected_bank
        assert player.token_reserved == TokenBag().add(wildcard_collaterals)

    def test_purchase_card_wildcard_and_tokens_choose_token(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 2,
                 Token.BLUE: 2}
        wildcard_collaterals = {Token.WHITE: 1,
                                Token.BLUE: 1}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the wildcard amounts
        wildcard_amounts = {Token.YELLOW: 2}
        bank.remove_token(wildcard_amounts)
        player.add_token(wildcard_amounts)
        # Add the token amounts
        bank.remove_token(costs)
        player.add_token(costs)
        # Perform action without wildcard collaterals
        action = PurchaseCard(card_to_buy)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        # The player should keep the wildcard amounts
        expected_bank = Bank()
        expected_bank.remove_token(wildcard_amounts)
        assert bank == expected_bank
        assert player.token_reserved == TokenBag().add(wildcard_amounts)

    def test_purchase_card_all(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 4,
                 Token.BLUE: 2}
        bonuses = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 1}
        token_collaterals = {Token.GREEN: 1,
                             Token.WHITE: 1,
                             Token.BLUE: 1}
        wildcard_collaterals = {Token.WHITE: 1}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        # Add the wildcard amounts
        wildcard_amounts = {Token.YELLOW: 2}
        bank.remove_token(wildcard_amounts)
        player.add_token(wildcard_amounts)
        # Add the token amounts
        token_amounts = {Token.GREEN: 1,
                         Token.WHITE: 2,
                         Token.BLUE: 1}
        bank.remove_token(token_amounts)
        player.add_token(token_amounts)
        # Perform action
        action = PurchaseCard(card_to_buy, wildcard_collaterals)
        action.perform(player, bank)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        # The player should have extra tokens: 1 white & 1 wildcard
        expected_bank = Bank()
        expected_bank.remove_token({Token.WHITE: 1, Token.YELLOW: 1})
        assert bank == expected_bank
        assert player.token_reserved == TokenBag().add({Token.WHITE: 1,
                                                        Token.YELLOW: 1})

    def test_purchase_card_all_from_reserved(self) -> None:
        bonus_color = Token.BLACK
        costs = {Token.GREEN: 2,
                 Token.WHITE: 4,
                 Token.BLUE: 2}
        bonuses = {Token.GREEN: 1,
                   Token.WHITE: 2,
                   Token.BLUE: 1}
        token_collaterals = {Token.GREEN: 1,
                             Token.WHITE: 1,
                             Token.BLUE: 1}
        wildcard_collaterals = {Token.WHITE: 1}
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=bonus_color, token_cost=TokenBag().add(costs))
        player = Player('test_player')
        bank = Bank()
        # Add the bonuses
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        # Add the wildcard amounts
        wildcard_amounts = {Token.YELLOW: 2}
        bank.remove_token(wildcard_amounts)
        player.add_token(wildcard_amounts)
        # Add the token amounts
        token_amounts = {Token.GREEN: 1,
                         Token.WHITE: 2,
                         Token.BLUE: 1}
        bank.remove_token(token_amounts)
        player.add_token(token_amounts)
        # Reserve card
        player.add_to_reserved_cards(card_to_buy)
        assert card_to_buy in player.cards_reserved
        assert player.num_reserved_cards == 1
        # Perform action
        action = PurchaseCard(card_to_buy, wildcard_collaterals)
        action.perform(player, bank)
        assert card_to_buy not in player.cards_reserved
        assert player.num_reserved_cards == 0
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[bonus_color] == 1
        assert player.prestige_points == card_prestige_points
        # The player should have extra tokens: 1 white & 1 wildcard
        expected_bank = Bank()
        expected_bank.remove_token({Token.WHITE: 1, Token.YELLOW: 1})
        assert bank == expected_bank
        assert player.token_reserved == TokenBag().add({Token.WHITE: 1,
                                                        Token.YELLOW: 1})
