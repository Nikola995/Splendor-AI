from game_base.action_sets import (StandardActionSet,
                                   generate_3_unique_token_actions,
                                   generate_2_same_token_actions,
                                   generate_standard_token_actions)
from game_base.games import Game
from game_base.players import Player
from game_base.tokens import Token
from itertools import combinations


class TestingGeneratingTokenActions:
    def test_generate_3_unique_token_actions(self) -> None:
        assert len(generate_3_unique_token_actions()) == 10

    def test_generate_2_same_token_actions(self) -> None:
        assert len(generate_2_same_token_actions()) == 5

    def test_generate_standard_token_actions(self) -> None:
        assert len(generate_standard_token_actions()) == 15


class TestingStandardActionSet:
    def test_standard_action_set_initialization(self) -> None:
        action_set = StandardActionSet()
        assert len(action_set.token_actions) == 15
        assert len(action_set.card_actions) == 0
        assert len(action_set.card_actions_player) == 0
    
    def test_standard_action_set_game_initialization(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players)
        game.initialize()
        action_set = game.possible_actions
        assert isinstance(action_set, StandardActionSet)
        assert len(action_set.token_actions) == 15
        assert len(action_set.card_actions) == 24
        assert len(action_set.card_actions_player) == 3
        assert len(action_set.all_actions()) == 42
    
