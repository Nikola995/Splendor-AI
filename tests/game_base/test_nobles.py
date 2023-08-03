import pytest
import random
from dataclasses import FrozenInstanceError
from game_base.tokens import Token, TokenBag
from game_base.nobles import Noble, NobleGenerator


class TestingNoble:
    def test_noble_initialization_default_simple(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.RED: 4}
        noble = Noble(amounts)
        expected = TokenBag()
        expected.add(amounts)
        assert noble.bonus_required == expected

    def test_noble_initialization_default_all(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        noble = Noble(amounts)
        expected = TokenBag()
        expected.add(amounts)
        assert noble.bonus_required == expected

    def test_noble_initialization_error_wildcard(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.YELLOW: 4}
        with pytest.raises(ValueError) as e:
            noble = Noble(amounts)

    def test_noble_initialization_error_negative_value(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.RED: -1}
        with pytest.raises(ValueError) as e:
            noble = Noble(amounts)

    def test_noble_frozen_error_prestige_points(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        noble = Noble(amounts)
        with pytest.raises(FrozenInstanceError) as e:
            noble.prestige_points += 1

    def test_noble_str(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        noble = Noble(amounts)
        assert str(noble) == ("Prestige points: 3\n"
                              "Bonuses required:\n"
                              "GREEN: 4\n"
                              "RED  : 4")


class TestingNobleGenerator:
    def test_noble_generator_len_default(self) -> None:
        nobles = NobleGenerator().generate_nobles()
        assert len(nobles) == 5

    def test_noble_generator_len_custom(self) -> None:
        num_players = 3
        nobles = NobleGenerator().generate_nobles(num_players)
        assert len(nobles) == 4

    def test_noble_generator_types(self) -> None:
        nobles = NobleGenerator().generate_nobles()
        for noble in nobles:
            assert isinstance(noble, Noble)
