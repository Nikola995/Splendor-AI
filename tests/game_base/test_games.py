import pytest
from game_base.cards import Card
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from game_base.banks import Bank
from game_base.actions import (ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from game_base.games import Game, GameState
from tests.game_base.test_cards import TestingCardManager


class TestingGameAddPlayer:
    def test_game_adding_players(self) -> None:
        # Testing both can_add_player & add_player
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
            assert game.num_players == i + 1

    def test_game_can_add_player_False_player_exists(self) -> None:
        game = Game()
        player = Player(f'test_player')
        assert game.can_add_player(player)
        game.add_player(player)
        assert not game.can_add_player(player)

    def test_game_can_add_player_False_game_in_progress(self) -> None:
        game = Game()
        for i in range(3):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
            assert game.num_players == i + 1
        game.initialize()
        player = Player(f'test_player')
        assert not game.can_add_player(player)

    def test_game_can_add_player_False_too_many_players(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
            assert game.num_players == i + 1
        player = Player(f'test_player')
        assert not game.can_add_player(player)

    def test_game_add_player_error_player_exists(self) -> None:
        game = Game()
        player = Player(f'test_player')
        assert game.can_add_player(player)
        game.add_player(player)
        with pytest.raises(ValueError) as e:
            game.add_player(player)

    def test_game_add_player_error_game_in_progress(self) -> None:
        game = Game()
        for i in range(3):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
            assert game.num_players == i + 1
        game.initialize()
        player = Player(f'test_player')
        with pytest.raises(ValueError) as e:
            game.add_player(player)

    def test_game_add_player_error_too_many_players(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
            assert game.num_players == i + 1
        player = Player(f'test_player')
        assert not game.can_add_player(player)
        with pytest.raises(ValueError) as e:
            game.add_player(player)


class TestingGameRemovePlayer:
    def test_game_removing_players(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.add_player(player)
        assert game.num_players == 4
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.remove_player(player)
            assert game.num_players == 4 - (i + 1)

    def test_game_removing_players_by_id(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.add_player(player)
        assert game.num_players == 4
        for i in range(4):
            player = game.get_player_by_id(f'test_player_{i + 1}')
            game.remove_player(player)
            assert game.num_players == 4 - (i + 1)

    def test_game_can_remove_player_False_not_player_exists(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.add_player(player)
        assert game.num_players == 4
        player = Player(f'test_player_5')
        assert not game.can_remove_player(player)

    def test_game_can_remove_player_False_game_in_progress(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.add_player(player)
        assert game.num_players == 4
        player = Player(f'test_player_1')
        game.meta_data.change_game_state(GameState.IN_PROGRESS)
        assert not game.can_remove_player(player)

    def test_game_remove_player_error_not_player_exists(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.add_player(player)
        assert game.num_players == 4
        player = Player(f'test_player_5')
        with pytest.raises(ValueError) as e:
            game.remove_player(player)

    def test_game_remove_player_error_game_in_progress(self) -> None:
        game = Game()
        for i in range(4):
            player = Player(f'test_player_{i + 1}')
            game.add_player(player)
        assert game.num_players == 4
        player = Player(f'test_player_1')
        game.meta_data.change_game_state(GameState.IN_PROGRESS)
        with pytest.raises(ValueError) as e:
            game.remove_player(player)


class TestingGameInit:

    def test_game_initialization_2_players(self) -> None:
        game = Game()
        num_players = 2
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        assert game.can_initialize()
        game.initialize()
        assert game.bank == Bank(num_players)
        assert len(game.nobles) == num_players + 1
        assert len(game.cards.get_all_cards_on_tables()) == 12

    def test_game_initialization_3_players(self) -> None:
        game = Game()
        num_players = 3
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        assert game.can_initialize()
        game.initialize()
        assert game.bank == Bank(num_players)
        assert len(game.nobles) == num_players + 1
        assert len(game.cards.get_all_cards_on_tables()) == 12

    def test_game_initialization_4_players(self) -> None:
        game = Game()
        num_players = 4
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        assert game.can_initialize()
        game.initialize()
        assert game.bank == Bank(num_players)
        assert len(game.nobles) == num_players + 1
        assert len(game.cards.get_all_cards_on_tables()) == 12

    def test_game_can_initialize_False_min_players(self) -> None:
        game = Game()
        num_players = 1
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        assert not game.can_initialize()

    def test_game_can_initialize_False_game_started(self) -> None:
        game = Game()
        num_players = 4
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        assert game.can_initialize()
        game.initialize()
        assert not game.can_initialize()

    def test_game_initialization_error_min_players(self) -> None:
        game = Game()
        num_players = 1
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        with pytest.raises(ValueError) as e:
            game.initialize()

    def test_game_initialization_error_game_started(self) -> None:
        game = Game()
        num_players = 4
        for i in range(num_players):
            player = Player(f'test_player_{i + 1}')
            assert game.can_add_player(player)
            game.add_player(player)
        assert game.num_players == num_players
        assert game.can_initialize()
        game.initialize()
        with pytest.raises(ValueError) as e:
            game.initialize()


class TestingGameProperties:
    def test_game_property_num_players(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players)
        assert game.num_players == num_players

    def test_game_property_current_player_idx(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players)
        assert game.current_player_idx == 0

    def test_game_property_current_player(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players)
        assert game.current_player == Player(f'test_player_1')


class TestingGameMakeMoveReserve3UniqueColorTokens:

    def test_game_can_make_move_3_unique_tokens_True(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        assert game.can_make_move_for_current_player(action)
    
    def test_game_make_move_3_unique_tokens(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        game.make_move_for_current_player(action)
        token_amounts = dict.fromkeys(colors, 1)
        expected_bank = Bank(num_players)
        expected_bank.remove_token(token_amounts)
        assert game.current_player_idx == 1
        assert game.current_player == players[1]
        assert game.meta_data.turns_played == 0
        assert not game.is_final_turn()
        assert game.players[0].token_reserved == TokenBag().add(token_amounts)
        assert game.bank == expected_bank
    
    def test_game_can_make_move_3_unique_tokens_False_game(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_can_make_move_3_unique_tokens_False_player(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        game.current_player.token_reserved.add({Token.WHITE: 8})
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_can_make_move_3_unique_tokens_False_bank(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        game.bank.remove_token({Token.GREEN: 2})
        game.bank.remove_token({Token.GREEN: 1})
        game.bank.remove_token({Token.GREEN: 1})
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)


class TestingGameMakeMoveReserve2SameColorTokens:

    def test_game_can_make_move_2_same_tokens_True(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        color = Token.GREEN
        action = Reserve2SameColorTokens(color)
        assert game.can_make_move_for_current_player(action)
        
    def test_game_can_make_move_2_same_tokens_False_game(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        color = Token.GREEN
        action = Reserve2SameColorTokens(color)
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_can_make_move_2_same_tokens_False_player(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        color = Token.GREEN
        action = Reserve2SameColorTokens(color)
        game.current_player.token_reserved.add({Token.WHITE: 9})
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_can_make_move_2_same_tokens_False_bank(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        color = Token.GREEN
        action = Reserve2SameColorTokens(color)
        game.bank.remove_token({Token.GREEN: 1})
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_make_move_2_same_tokens(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        color = Token.GREEN
        action = Reserve2SameColorTokens(color)
        game.make_move_for_current_player(action)
        token_amounts = {color: 2}
        expected_bank = Bank(num_players)
        expected_bank.remove_token(token_amounts)
        assert game.current_player_idx == 1
        assert game.current_player == players[1]
        assert game.meta_data.turns_played == 0
        assert not game.is_final_turn()
        assert game.players[0].token_reserved == TokenBag().add(token_amounts)
        assert game.bank == expected_bank


class TestingGameMakeMoveReserveCard:

    def test_game_can_make_move_reserve_card_True(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_reserve_card_False(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_reserve_card_False_bank(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_reserve_card(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_reserve_card_no_wildcard_bank(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_reserve_card_no_wildcard_player(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMovePurchaseCard:
    def test_game_can_make_move_purchase_card_True(self) -> None:
        raise NotImplementedError()

    def test_game_can_make_move_purchase_card_False_all(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_just_bonuses(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_just_wildcard(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_just_tokens(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_bonuses_and_wildcard(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_bonuses_and_tokens(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_wildcard_and_tokens_choose_wildcard(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_wildcard_and_tokens_choose_token(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_all(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_all_from_reserved(self) -> None:
        raise NotImplementedError()

    def test_game_make_move_purchase_card_eligible_for_noble(self) -> None:
        raise NotImplementedError()


class TestingGameMakeMoveEndTurn:
    def test_game_end_player_turn_default(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_multiple_players(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_another_turn(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_final_turn(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_final_turn_winner(self) -> None:
        raise NotImplementedError()

    def test_game_end_player_turn_final_turn_multiple_eligible_winner(self) -> None:
        raise NotImplementedError()
