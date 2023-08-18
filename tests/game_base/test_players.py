import pytest
from game_base.cards import Card
from game_base.nobles import Noble
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from tests.game_base.test_cards import TestingCardManager


class TestingPlayer:
    def test_player_initialization_default(self) -> None:
        player = Player('test_player')
        assert player.id == 'test_player'
        assert player.token_reserved == TokenBag()
        assert player.cards_reserved == [None] * 3
        assert player.cards_owned == []
        assert player.bonus_owned == TokenBag()
        assert player.nobles_owned == []
        assert player.prestige_points == 0

    def test_player_can_remove_token_True(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3})
        assert player.can_remove_token({Token.GREEN: 2})

    def test_player_can_remove_token_False(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3})
        assert not player.can_remove_token({Token.RED: 2})

    def test_player_remove_token(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3})
        player.remove_token({Token.GREEN: 2})
        expected = TokenBag()
        expected.add({Token.GREEN: 1})
        assert player.token_reserved == expected

    def test_player_remove_token_error_negative(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3})
        with pytest.raises(ValueError) as e:
            player.remove_token({Token.RED: 2})

    def test_player_can_add_token_True(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3,
                                   Token.WHITE: 3,
                                   Token.BLACK: 2})
        assert player.can_add_token({Token.BLUE: 2})

    def test_player_can_add_token_False(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3,
                                   Token.WHITE: 3,
                                   Token.BLACK: 2,
                                   Token.RED: 1})
        assert not player.can_add_token({Token.BLUE: 2})

    def test_player_add_token(self) -> None:
        player = Player('test_player')
        player.add_token({Token.GREEN: 3})
        player.add_token({Token.RED: 2})
        expected = TokenBag()
        expected.add({Token.GREEN: 3,
                      Token.RED: 2})
        assert player.token_reserved == expected

    def test_player_add_token_error_check(self) -> None:
        player = Player('test_player')
        player.add_token({Token.GREEN: 3})
        player.add_token({Token.RED: 2})
        player.add_token({Token.WHITE: 3})
        player.add_token({Token.BLACK: 2})
        with pytest.raises(ValueError) as e:
            player.remove_token({Token.YELLOW: 1})

    def test_player_property_num_reserved_cards_default(self) -> None:
        player = Player('test_player')
        assert player.num_reserved_cards == 0

    def test_player_can_reserve_card_True(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        assert player.num_reserved_cards == 0
        assert player.can_reserve_card(cards[0])

    def test_player_add_to_reserved_cards(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        assert player.num_reserved_cards == 0
        player.add_to_reserved_cards(cards[0])
        assert player.num_reserved_cards == 1
        assert player.cards_reserved[0] == cards[0]

    def test_player_add_to_reserved_cards_all(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            assert player.can_reserve_card(cards[i])
            assert player.num_reserved_cards == i
            player.add_to_reserved_cards(cards[i])
            assert player.num_reserved_cards == i + 1
            assert player.cards_reserved[i] == cards[i]

    def test_player_can_reserve_card_False_no_free_slot(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            player.add_to_reserved_cards(cards[i])
        assert not player.can_reserve_card(cards[4])
    
    def test_player_can_reserve_card_False_already_reserved(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        player.add_to_reserved_cards(cards[0])
        assert not player.can_reserve_card(cards[0])

    def test_player_remove_from_reserved_cards(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            player.add_to_reserved_cards(cards[i])
        player.remove_from_reserved_cards(cards[1])
        assert player.num_reserved_cards == 2
        assert isinstance(player.cards_reserved[0], Card)
        assert player.cards_reserved[1] is None
        assert isinstance(player.cards_reserved[2], Card)

    def test_player_remove_from_reserved_cards_error(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            player.add_to_reserved_cards(cards[i])
        with pytest.raises(ValueError) as e:
            player.remove_from_reserved_cards(cards[3])

    def test_player_add_to_reserved_cards_error(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            player.add_to_reserved_cards(cards[i])
        with pytest.raises(ValueError) as e:
            player.add_to_reserved_cards(cards[3])

    def test_player_add_to_owned_cards(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        prestige_expected = 0
        bonus_expected = TokenBag()
        for i in range(3):
            player.add_to_owned_cards(cards[i])
            prestige_expected += i + 1
            bonus_expected.add({Token.GREEN: 1})
            assert len(player.cards_owned) == i + 1
            assert player.bonus_owned == bonus_expected
            assert player.prestige_points == prestige_expected

    def test_player_add_to_owned_cards_reserved(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        prestige_expected = 0
        bonus_expected = TokenBag()
        num_test_cards = 3
        for i in range(num_test_cards):
            player.add_to_reserved_cards(cards[i])
            assert player.num_reserved_cards == i + 1
        for i in range(num_test_cards):
            player.add_to_owned_cards(cards[i])
            assert player.num_reserved_cards == num_test_cards - (i + 1)
            assert player.cards_reserved[i] is None
            prestige_expected += i + 1
            bonus_expected.add({Token.GREEN: 1})
            assert len(player.cards_owned) == i + 1
            assert player.bonus_owned == bonus_expected
            assert player.prestige_points == prestige_expected

    def test_player_is_eligible_for_noble_True(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        player.add_to_owned_cards(cards[2])
        noble = Noble({Token.GREEN: 3})
        assert player.is_eligible_for_noble(noble)

    def test_player_is_eligible_for_noble_False(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        noble = Noble({Token.GREEN: 3})
        assert not player.is_eligible_for_noble(noble)

    def test_player_add_noble(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        player.add_to_owned_cards(cards[2])
        noble = Noble({Token.GREEN: 3})
        assert player.prestige_points == 6
        assert len(player.nobles_owned) == 0
        assert player.is_eligible_for_noble(noble)
        player.add_noble(noble)
        assert player.prestige_points == 9
        assert len(player.nobles_owned) == 1

    def test_player_add_noble_error(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        noble = Noble({Token.GREEN: 3})
        with pytest.raises(ValueError) as e:
            player.add_noble(noble)

    def test_player_sort(self) -> None:
        player_1 = Player('test_player_1')
        player_2 = Player('test_player_2')
        player_3 = Player('test_player_3')
        player_4 = Player('test_player_4')
        cards = TestingCardManager.card_list_for_testing(num_cards=10)
        player_1.prestige_points = 16
        player_2.prestige_points = 16
        player_3.prestige_points = 15
        player_4.prestige_points = 15
        player_1.cards_owned = cards[0:3]
        assert len(player_1.cards_owned) == 3
        player_2.cards_owned = cards[3:7]
        assert len(player_2.cards_owned) == 4
        player_3.cards_owned = cards[7:8]
        assert len(player_3.cards_owned) == 1
        player_4.cards_owned = cards[8:10]
        assert len(player_4.cards_owned) == 2
        # Do the same sort as used in Game class
        player_list = sorted([player_2, player_4, player_3, player_1],
                             reverse=True)
        expected = [player_1, player_2, player_3, player_4]
        assert player_list == expected


class TestingPlayerCanPurchaseCard:
    def test_player_can_purchase_card_True_just_bonus(self) -> None:
        player = Player('test_player')
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_just_token(self) -> None:
        player = Player('test_player')
        tokens = {Token.GREEN: 3,
                  Token.BLUE: 2}
        player.add_token(tokens)
        expected_cost = TokenBag().add(tokens)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_just_wildcard(self) -> None:
        player = Player('test_player')
        token_cost = {Token.BLUE: 1,
                      Token.RED: 3}
        expected_cost = TokenBag().add(token_cost)
        player.add_token({Token.YELLOW: sum(token_cost.values())})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_no_bonus(self) -> None:
        player = Player('test_player')
        # Add the regular tokens
        tokens = {Token.GREEN: 3,
                  Token.BLUE: 2}
        player.add_token(tokens)
        # Add the wildcard tokens
        collaterals = {Token.BLUE: 1,
                       Token.RED: 3}
        expected_cost = TokenBag().add(tokens).add(collaterals)
        player.add_token({Token.YELLOW: sum(collaterals.values())})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_no_token(self) -> None:
        player = Player('test_player')
        # Add the bonuses
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        # Add the wildcard tokens
        collaterals = {Token.BLUE: 1,
                       Token.RED: 3}
        expected_cost = TokenBag().add(bonuses).add(collaterals)
        player.add_token({Token.YELLOW: sum(collaterals.values())})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_no_wildcard(self) -> None:
        player = Player('test_player')
        # Add the bonuses
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        # Add the regular tokens
        tokens = {Token.GREEN: 3,
                  Token.BLUE: 2}
        player.add_token(tokens)
        expected_cost = TokenBag().add(bonuses).add(tokens)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_all(self) -> None:
        player = Player('test_player')
        # Add the bonuses
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        # Add the regular tokens
        tokens = {Token.GREEN: 3,
                  Token.BLUE: 2}
        player.add_token(tokens)
        # Add the wildcard tokens
        collaterals = {Token.BLUE: 1,
                       Token.RED: 3}
        player.add_token({Token.YELLOW: sum(collaterals.values())})
        expected_cost = TokenBag().add(bonuses).add(tokens).add(collaterals)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_False_all(self) -> None:
        player = Player('test_player')
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        tokens = {Token.GREEN: 3,
                  Token.BLUE: 2}
        collaterals = {Token.BLUE: 1,
                       Token.RED: 3}
        expected_cost = (TokenBag().add(bonuses).add(tokens).add(collaterals)
                         .add({Token.WHITE: 1}))
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert not player.can_purchase_card(card_to_buy)
        # Add the bonuses
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        assert not player.can_purchase_card(card_to_buy)
        # Add the regular tokens
        player.add_token(tokens)
        assert not player.can_purchase_card(card_to_buy)
        # Add the wildcard tokens
        player.add_token({Token.YELLOW: sum(collaterals.values())})
        assert not player.can_purchase_card(card_to_buy)


class TestingPlayerPurchaseCard:
    def test_player_purchase_card_just_bonus(self) -> None:
        player = Player('test_player')
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
        removed_tokens = player.purchase_card(card_to_buy)
        assert removed_tokens == TokenBag().tokens
        assert player.token_reserved == TokenBag()
        assert card_to_buy in player.cards_owned
        for color in bonuses:
            assert player.bonus_owned.tokens[color] == bonuses[color]
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert (player.prestige_points ==
                (bonus_card_prestige_points * sum(bonuses.values())
                 + card_prestige_points))

    def test_player_purchase_card_just_token(self) -> None:
        player = Player('test_player')
        token_cost = {Token.GREEN: 3,
                      Token.BLUE: 2}
        token_extra = {Token.GREEN: 1,
                       Token.RED: 2}
        player.add_token(token_cost)
        player.add_token(token_extra)
        expected_cost = TokenBag().add(token_cost)
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        removed_tokens = player.purchase_card(card_to_buy)
        assert removed_tokens == TokenBag().add(token_cost).tokens
        assert player.token_reserved == TokenBag().add(token_extra)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_just_wildcard(self) -> None:
        player = Player('test_player')
        token_cost = {Token.BLUE: 1,
                      Token.RED: 3}
        expected_cost = TokenBag().add(token_cost)
        extra_wildcard = 2
        player.add_token({Token.YELLOW: (sum(token_cost.values()) +
                                         extra_wildcard)})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        removed_tokens = player.purchase_card(card_to_buy)
        assert removed_tokens == (TokenBag()
                                  .add({Token.YELLOW: sum(token_cost.values())})
                                  .tokens)
        assert player.token_reserved == (TokenBag()
                                         .add({Token.YELLOW: extra_wildcard}))
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_no_bonus(self) -> None:
        player = Player('test_player')
        # Add the regular tokens
        token_cost = {Token.GREEN: 2,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 1,
                       Token.WHITE: 1}
        player.add_token(token_cost)
        player.add_token(token_extra)
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 2
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = TokenBag().add(wildcard_cost).add(token_cost)
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        removed_tokens = player.purchase_card(card_to_buy)
        expected_removed = (TokenBag()
                            .add({Token.YELLOW: sum(wildcard_cost.values())})
                            .add(token_cost))
        assert removed_tokens == expected_removed.tokens
        assert player.token_reserved == (TokenBag()
                                         .add({Token.YELLOW: extra_wildcard})
                                         .add(token_extra))
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_no_token(self) -> None:
        player = Player('test_player')
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
        extra_wildcard = 2
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = TokenBag().add(wildcard_cost).add(bonus_cost)
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        removed_tokens = player.purchase_card(card_to_buy)
        expected_removed = (TokenBag()
                            .add({Token.YELLOW: sum(wildcard_cost.values())}))
        assert removed_tokens == expected_removed.tokens
        assert player.token_reserved == (TokenBag()
                                         .add({Token.YELLOW: extra_wildcard}))
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_no_wildcard(self) -> None:
        player = Player('test_player')
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
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = TokenBag().add(token_cost).add(bonus_cost)
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        removed_tokens = player.purchase_card(card_to_buy)
        expected_removed = TokenBag().add(token_cost)
        assert removed_tokens == expected_removed.tokens
        assert player.token_reserved == TokenBag().add(token_extra)
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_all(self) -> None:
        player = Player('test_player')
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
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 2
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = (TokenBag().add(wildcard_cost)
                         .add(bonus_cost).add(token_cost))
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        removed_tokens = player.purchase_card(card_to_buy)
        expected_removed = (TokenBag()
                            .add({Token.YELLOW: sum(wildcard_cost.values())})
                            .add(token_cost))
        assert removed_tokens == expected_removed.tokens
        assert player.token_reserved == (TokenBag()
                                         .add({Token.YELLOW: extra_wildcard})
                                         .add(token_extra))
        assert card_to_buy in player.cards_owned
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_all_from_reserved(self) -> None:
        player = Player('test_player')
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
        # Add the wildcard tokens
        wildcard_cost = {Token.BLUE: 1,
                         Token.RED: 1}
        extra_wildcard = 2
        player.add_token({Token.YELLOW: (sum(wildcard_cost.values()) +
                                         extra_wildcard)})
        card_bonus_color = Token.BLACK
        card_prestige_points = 3
        expected_cost = (TokenBag().add(wildcard_cost)
                         .add(bonus_cost).add(token_cost))
        card_to_buy = Card(level=1, prestige_points=card_prestige_points,
                           bonus_color=card_bonus_color,
                           token_cost=expected_cost)
        # Reserve the card before purchase
        player.add_to_reserved_cards(card_to_buy)
        assert player.num_reserved_cards == 1
        assert card_to_buy in player.cards_reserved
        removed_tokens = player.purchase_card(card_to_buy)
        expected_removed = (TokenBag()
                            .add({Token.YELLOW: sum(wildcard_cost.values())})
                            .add(token_cost))
        assert removed_tokens == expected_removed.tokens
        assert player.token_reserved == (TokenBag()
                                         .add({Token.YELLOW: extra_wildcard})
                                         .add(token_extra))
        assert card_to_buy in player.cards_owned
        assert player.num_reserved_cards == 0
        assert card_to_buy not in player.cards_reserved
        assert player.bonus_owned.tokens[card_bonus_color] == 1
        assert player.prestige_points == card_prestige_points

    def test_player_purchase_card_all_error(self) -> None:
        player = Player('test_player')
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        tokens = {Token.GREEN: 3,
                  Token.BLUE: 2}
        collaterals = {Token.BLUE: 1,
                       Token.RED: 3}
        expected_cost = (TokenBag().add(bonuses).add(tokens).add(collaterals)
                         .add({Token.WHITE: 1}))
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        with pytest.raises(ValueError) as e:
            player.purchase_card(card_to_buy)
        # Add the bonuses
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        with pytest.raises(ValueError) as e:
            player.purchase_card(card_to_buy)
        # Add the regular tokens
        player.add_token(tokens)
        with pytest.raises(ValueError) as e:
            player.purchase_card(card_to_buy)
        # Add the wildcard tokens
        player.add_token({Token.YELLOW: sum(collaterals.values())})
        with pytest.raises(ValueError) as e:
            player.purchase_card(card_to_buy)


class TestingPlayerStr:
    def test_player_str_default(self) -> None:
        player = Player('test_player')
        assert str(player) == ("Player ID: test_player\n"
                               "Prestige points: 0\n"
                               "Number of purchased cards: 0\n"
                               "Number of nobles: 0\n"
                               "Number of reserved cards: 0\n"
                               "--Reserved cards--\n"
                               "None\n"
                               "None\n"
                               "None\n"
                               "--Bonuses from purchased cards--\n"
                               "\n"
                               "--Reserved tokens--\n"
                               )

    def test_player_str_tokens_reserved(self) -> None:
        player = Player('test_player')
        player.add_token({Token.BLACK: 1, Token.BLUE: 1, Token.RED: 1})
        assert str(player) == ("Player ID: test_player\n"
                               "Prestige points: 0\n"
                               "Number of purchased cards: 0\n"
                               "Number of nobles: 0\n"
                               "Number of reserved cards: 0\n"
                               "--Reserved cards--\n"
                               "None\n"
                               "None\n"
                               "None\n"
                               "--Bonuses from purchased cards--\n"
                               "\n"
                               "--Reserved tokens--\n"
                               "Blue : 1\n"
                               "Black: 1\n"
                               "Red  : 1"
                               )

    def test_player_str_cards_reserved(self) -> None:
        player = Player('test_player')
        amounts = {Token.BLUE: 1}
        card = Card(level=1, prestige_points=0, bonus_color=Token.RED,
                    token_cost=TokenBag().add(amounts))
        player.add_to_reserved_cards(card)
        assert str(player) == ("Player ID: test_player\n"
                               "Prestige points: 0\n"
                               "Number of purchased cards: 0\n"
                               "Number of nobles: 0\n"
                               "Number of reserved cards: 1\n"
                               "--Reserved cards--\n"
                               "Card 00100\n"
                               "Card Cost\n"
                               "Blue : 1\n"
                               "Benefits of Purchasing Card\n"
                               "Prestige points: 0\n"
                               "Bonus token: Red\n"
                               "None\n"
                               "None\n"
                               "--Bonuses from purchased cards--\n"
                               "\n"
                               "--Reserved tokens--\n"
                               )

    def test_player_str_cards_purchased(self) -> None:
        player = Player('test_player')
        amounts = {Token.BLUE: 1}
        card = Card(level=1, prestige_points=2, bonus_color=Token.RED,
                    token_cost=TokenBag().add(amounts))
        player.add_to_owned_cards(card)
        assert str(player) == ("Player ID: test_player\n"
                               "Prestige points: 2\n"
                               "Number of purchased cards: 1\n"
                               "Number of nobles: 0\n"
                               "Number of reserved cards: 0\n"
                               "--Reserved cards--\n"
                               "None\n"
                               "None\n"
                               "None\n"
                               "--Bonuses from purchased cards--\n"
                               "Red  : 1\n"
                               "--Reserved tokens--\n"
                               )

    def test_player_str_nobles_owned(self) -> None:
        player = Player('test_player')
        bonus_color = Token.RED
        num_cards = 3
        for _ in range(num_cards):
            amounts = {Token.BLUE: 1}
            card = Card(level=1, prestige_points=1, bonus_color=bonus_color,
                        token_cost=TokenBag().add(amounts))
            player.add_to_owned_cards(card)
        noble = Noble({bonus_color: num_cards})
        player.add_noble(noble)
        assert str(player) == ("Player ID: test_player\n"
                               "Prestige points: 6\n"
                               "Number of purchased cards: 3\n"
                               "Number of nobles: 1\n"
                               "Number of reserved cards: 0\n"
                               "--Reserved cards--\n"
                               "None\n"
                               "None\n"
                               "None\n"
                               "--Bonuses from purchased cards--\n"
                               "Red  : 3\n"
                               "--Reserved tokens--\n"
                               )

    def test_player_str_all(self) -> None:
        player = Player('test_player')
        # Reserve tokens
        player.add_token({Token.BLACK: 1, Token.BLUE: 1, Token.RED: 1})
        # Reserve card
        amounts = {Token.BLUE: 1}
        card = Card(level=1, prestige_points=0, bonus_color=Token.RED,
                    token_cost=TokenBag().add(amounts))
        player.add_to_reserved_cards(card)
        # Purchase cards
        bonus_color = Token.RED
        num_cards = 3
        for _ in range(num_cards):
            amounts = {Token.BLUE: 1}
            card = Card(level=1, prestige_points=1, bonus_color=bonus_color,
                        token_cost=TokenBag().add(amounts))
            player.add_to_owned_cards(card)
        # Add Noble
        noble = Noble({bonus_color: num_cards})
        player.add_noble(noble)
        assert str(player) == ("Player ID: test_player\n"
                               "Prestige points: 6\n"
                               "Number of purchased cards: 3\n"
                               "Number of nobles: 1\n"
                               "Number of reserved cards: 1\n"
                               "--Reserved cards--\n"
                               "Card 00100\n"
                               "Card Cost\n"
                               "Blue : 1\n"
                               "Benefits of Purchasing Card\n"
                               "Prestige points: 0\n"
                               "Bonus token: Red\n"
                               "None\n"
                               "None\n"
                               "--Bonuses from purchased cards--\n"
                               "Red  : 3\n"
                               "--Reserved tokens--\n"
                               "Blue : 1\n"
                               "Black: 1\n"
                               "Red  : 1"
                               )
