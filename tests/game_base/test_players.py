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
        assert player.can_reserve_card()

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
            assert player.can_reserve_card()
            assert player.num_reserved_cards == i
            player.add_to_reserved_cards(cards[i])
            assert player.num_reserved_cards == i + 1
            assert player.cards_reserved[i] == cards[i]

    def test_player_can_reserve_card_False(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            player.add_to_reserved_cards(cards[i])
        assert not player.can_reserve_card()

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
        num_bonuses = 3
        bonus_color = Token.GREEN
        for _ in range(num_bonuses):
            amounts = {Token.BLUE: 1}
            card = Card(level=1, prestige_points=0, bonus_color=bonus_color,
                        token_cost=TokenBag().add(amounts))
            player.add_to_owned_cards(card)
        expected_cost = TokenBag().add({bonus_color: num_bonuses})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_no_wildcards(self) -> None:
        player = Player('test_player')
        num_bonuses = 2
        bonus_color = Token.GREEN
        for _ in range(num_bonuses):
            card = Card(level=1, prestige_points=0, bonus_color=bonus_color,
                        token_cost=TokenBag().add({Token.BLUE: 1}))
            player.add_to_owned_cards(card)
        num_tokens = 3
        token_color = Token.RED
        player.add_token({token_color: num_tokens})
        expected_cost = TokenBag().add({bonus_color: num_bonuses,
                                        token_color: num_tokens})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_wildcards(self) -> None:
        player = Player('test_player')
        num_bonuses = 2
        bonus_color = Token.GREEN
        for _ in range(num_bonuses):
            card = Card(level=1, prestige_points=0, bonus_color=bonus_color,
                        token_cost=TokenBag().add({Token.BLUE: 1}))
            player.add_to_owned_cards(card)
        num_tokens = 3
        token_color = Token.RED
        num_wildcards = 1
        player.add_token({token_color: num_tokens,
                          Token.YELLOW: num_wildcards})
        expected_cost = TokenBag().add({bonus_color: (num_bonuses +
                                                      num_wildcards),
                                        token_color: num_tokens})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        wildcard_collaterals = {bonus_color: num_wildcards}
        assert player.can_purchase_card(card_to_buy, wildcard_collaterals)

    def test_player_can_purchase_card_True_just_bonus_multi(self) -> None:
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

    def test_player_can_purchase_card_True_no_wildcards_multi(self) -> None:
        player = Player('test_player')
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        tokens = {Token.BLUE: 1,
                  Token.RED: 3}
        player.add_token(tokens)
        expected_cost = TokenBag().add(bonuses).add(tokens)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_True_wildcards_multi(self) -> None:
        player = Player('test_player')
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        tokens = {Token.BLUE: 1,
                  Token.RED: 3,
                  Token.YELLOW: 4}
        player.add_token(tokens)
        expected_cost = TokenBag().add(bonuses).add(tokens)
        # Add the wildcard collaterals
        expected_cost = expected_cost.remove(
            {Token.YELLOW: tokens[Token.YELLOW]})
        wildcard_collaterals = {Token.GREEN: 1, Token.RED: 1, Token.WHITE: 1}
        expected_cost = expected_cost.add(wildcard_collaterals)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy, wildcard_collaterals)

    def test_player_can_purchase_card_False_just_bonus(self) -> None:
        player = Player('test_player')
        extra_cost_color = Token.BLACK
        bonuses = {Token.GREEN: 3,
                   extra_cost_color: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        expected_cost = TokenBag().add(bonuses)
        expected_cost = expected_cost.add({extra_cost_color: 1})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert not player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_False_no_wildcards(self) -> None:
        player = Player('test_player')
        extra_cost_color = Token.BLACK
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        tokens = {Token.BLUE: 1,
                  extra_cost_color: 3}
        player.add_token(tokens)
        expected_cost = TokenBag().add(bonuses).add(tokens)
        expected_cost = expected_cost.add({extra_cost_color: 1})
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert not player.can_purchase_card(card_to_buy)

    def test_player_can_purchase_card_False_wildcards(self) -> None:
        player = Player('test_player')
        bonuses = {Token.GREEN: 3,
                   Token.BLUE: 2}
        for color in bonuses:
            for _ in range(bonuses[color]):
                amounts = {Token.BLUE: 1}
                card = Card(level=1, prestige_points=0, bonus_color=color,
                            token_cost=TokenBag().add(amounts))
                player.add_to_owned_cards(card)
        tokens = {Token.BLUE: 1,
                  Token.RED: 3,
                  Token.YELLOW: 2}
        player.add_token(tokens)
        expected_cost = TokenBag().add(bonuses).add(tokens)
        # Add the wildcard collaterals
        expected_cost = expected_cost.remove(
            {Token.YELLOW: tokens[Token.YELLOW]})
        wildcard_cost = {Token.GREEN: 1, Token.RED: 1}
        expected_cost = expected_cost.add(wildcard_cost)
        extra_cost = {Token.WHITE: 1}
        expected_cost = expected_cost.add(extra_cost)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert not player.can_purchase_card(card_to_buy)


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
