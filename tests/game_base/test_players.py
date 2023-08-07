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
        assert player.can_remove_token({Token.GREEN: 2}) == True

    def test_player_can_remove_token_False(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3})
        assert player.can_remove_token({Token.RED: 2}) == False

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
        assert player.can_add_token({Token.BLUE: 2}) == True

    def test_player_can_add_token_False(self) -> None:
        player = Player('test_player')
        player.token_reserved.add({Token.GREEN: 3,
                                   Token.WHITE: 3,
                                   Token.BLACK: 2,
                                   Token.RED: 1})
        assert player.can_add_token({Token.BLUE: 2}) == False

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
        assert player.can_reserve_card() == True

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
            assert player.can_reserve_card() == True
            assert player.num_reserved_cards == i
            player.add_to_reserved_cards(cards[i])
            assert player.num_reserved_cards == i + 1
            assert player.cards_reserved[i] == cards[i]

    def test_player_can_reserve_card_False(self) -> None:
        cards = TestingCardManager.card_list_for_testing()
        player = Player('test_player')
        for i in range(3):
            player.add_to_reserved_cards(cards[i])
        assert player.can_reserve_card() == False

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

    def test_player_is_eligible_for_noble_True(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        player.add_to_owned_cards(cards[2])
        noble = Noble({Token.GREEN: 3})
        assert player.is_eligible_for_noble(noble) == True

    def test_player_is_eligible_for_noble_False(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        noble = Noble({Token.GREEN: 3})
        assert player.is_eligible_for_noble(noble) == False

    def test_player_add_noble(self) -> None:
        cards = TestingCardManager.card_list_for_testing(prestige=True)
        player = Player('test_player')
        player.add_to_owned_cards(cards[0])
        player.add_to_owned_cards(cards[1])
        player.add_to_owned_cards(cards[2])
        noble = Noble({Token.GREEN: 3})
        assert player.prestige_points == 6
        assert len(player.nobles_owned) == 0
        assert player.is_eligible_for_noble(noble) == True
        player.add_noble(noble) == True
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
        assert player.can_purchase_card(card_to_buy) == True

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
        assert player.can_purchase_card(card_to_buy) == True

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
        assert player.can_purchase_card(card_to_buy) == True

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
        assert player.can_purchase_card(card_to_buy) == True

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
        assert player.can_purchase_card(card_to_buy) == True

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
        wildcard_cost = {Token.GREEN: 1, Token.RED: 1, Token.WHITE: 1}
        expected_cost = expected_cost.add(wildcard_cost)
        card_to_buy = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                           token_cost=expected_cost)
        assert player.can_purchase_card(card_to_buy) == True

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
        assert player.can_purchase_card(card_to_buy) == False

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
        assert player.can_purchase_card(card_to_buy) == False

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
        assert player.can_purchase_card(card_to_buy) == False


class TestingPlayerStr:
    def test_player_str(self) -> None:
        raise NotImplementedError()
