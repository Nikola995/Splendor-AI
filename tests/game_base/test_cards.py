import pytest
from dataclasses import FrozenInstanceError
from game_base.tokens import Token, TokenBag
from game_base.cards import (Card, CardManager,
                             CardManagerCollection, CardGenerator)


class TestingCard:
    def test_card_initialization(self) -> None:
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 1,
                   Token.BLUE: 1}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        expected = {Token.GREEN: 1,
                    Token.WHITE: 1,
                    Token.BLUE: 1,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 0}
        assert card.token_cost.tokens == expected
        assert card.level == 1
        assert card.prestige_points == 0
        assert card.bonus_color == Token.BLUE
        assert card.id == "11100"

    def test_card_initialization_error_wildcard_cost(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.YELLOW: 4}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_wildcard_bonus(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.BLUE: 4}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.YELLOW,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_negative_value(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.RED: -1}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_no_cost(self) -> None:
        amounts = {Token.GREEN: 0,
                   Token.RED: 0}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_level(self) -> None:
        level = 4
        amounts = {Token.GREEN: 4,
                   Token.RED: 4}
        with pytest.raises(ValueError) as e:
            card = Card(level=level, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_frozen_error_level(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        with pytest.raises(FrozenInstanceError) as e:
            card.level = 3

    def test_card_frozen_error_prestige_points(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        with pytest.raises(FrozenInstanceError) as e:
            card.prestige_points += 1

    def test_card_frozen_error_bonus_color(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        with pytest.raises(FrozenInstanceError) as e:
            card.bonus_color = Token.GREEN

    def test_card_sort(self) -> None:
        # The amounts don't matter for sorting
        amounts = {Token.BLUE: 1,
                   Token.BLACK: 1,
                   Token.RED: 1}
        card_1 = Card(level=1, prestige_points=0, bonus_color=Token.GREEN,
                      token_cost=TokenBag().add(amounts))
        card_2 = Card(level=2, prestige_points=0, bonus_color=Token.GREEN,
                      token_cost=TokenBag().add(amounts))
        card_3 = Card(level=3, prestige_points=0, bonus_color=Token.GREEN,
                      token_cost=TokenBag().add(amounts))
        card_list = sorted([card_3, card_2, card_1])
        expected = [card_1, card_2, card_3]
        assert card_list == expected

    def test_card_str(self) -> None:
        amounts = {Token.BLUE: 1,
                   Token.BLACK: 1,
                   Token.RED: 1}
        card = Card(level=1, prestige_points=0, bonus_color=Token.GREEN,
                    token_cost=TokenBag().add(amounts))
        assert str(card) == ("Card 00111\n"
                             "Card Cost\n"
                             "BLUE : 1\n"
                             "BLACK: 1\n"
                             "RED  : 1\n"
                             "Benefits of Purchasing Card\n"
                             "Prestige points: 0\n"
                             "Bonus token: GREEN")
