import pytest
import random
from game_base.cards import Card, CardGenerator
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from game_base.nobles import Noble
from game_base.banks import Bank
from game_base.actions import (ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from game_base.games import Game, GameState
from tests.game_base.test_cards import TestingCardManager

random.seed(42)


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


class TestingGameGettingCard:
    def test_game_getting_card_by_id_True(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_id = '21400'
        assert card.id == card_id
        assert game.get_card_by_id(card_id) == card

    def test_game_getting_card_by_id_False(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        card_id = '21400'
        assert game.get_card_by_id(card_id) is None

    def test_game_getting_card_by_idx_True(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        for _ in range(100):
            card_idx = random.randint(0, 11)
            card = game.cards.get_all_cards_on_tables()[card_idx]
            assert game.get_card_by_idx(card_idx) == card

    def test_game_getting_card_by_id_False(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        for _ in range(100):
            card_idx = random.randint(0, 11)
            assert game.get_card_by_idx(card_idx) is None


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
        assert game.players[0].token_reserved == TokenBag().add(token_amounts)
        assert game.bank == expected_bank


class TestingGameMakeMoveReserveCard:

    def test_game_can_make_move_reserve_card_True(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        card = random.sample(game.cards.get_all_cards_on_tables(), 1)[0]
        action = ReserveCard(card)
        assert game.can_make_move_for_current_player(action)

    def test_game_can_make_move_reserve_card_False_game(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        # There should be no cards available to get from the tables
        assert len([card for card in game.cards.get_all_cards_on_tables()
                    if card is not None]) == 0

    def test_game_can_make_move_reserve_card_False_player_no_free_slots(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        sample_cards = random.sample(game.cards.get_all_cards_on_tables(), 4)
        card_to_reserve = sample_cards[0]
        action = ReserveCard(card_to_reserve)
        for card in sample_cards[1:]:
            game.current_player.add_to_reserved_cards(card)
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_can_make_move_reserve_card_False_player_already_reserved(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        card = random.sample(game.cards.get_all_cards_on_tables(), 1)[0]
        action = ReserveCard(card)
        game.current_player.add_to_reserved_cards(card)
        assert not game.can_make_move_for_current_player(action)
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)

    def test_game_make_move_reserve_card(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        card = random.sample(game.cards.get_all_cards_on_tables(), 1)[0]
        action = ReserveCard(card)
        game.make_move_for_current_player(action)
        token_amounts = {Token.YELLOW: 1}
        expected_bank = Bank(num_players)
        expected_bank.remove_token(token_amounts)
        assert game.players[0].token_reserved == TokenBag().add(token_amounts)
        assert game.bank == expected_bank
        assert card in game.players[0].cards_reserved
        assert game.players[0].num_reserved_cards == 1

    def test_game_make_move_reserve_card_no_wildcard_bank(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        card = random.sample(game.cards.get_all_cards_on_tables(), 1)[0]
        action = ReserveCard(card)
        extra_tokens = {Token.WHITE: 10}
        game.current_player.add_token(extra_tokens)
        game.make_move_for_current_player(action)
        expected_bank = Bank(num_players)
        assert game.players[0].token_reserved == TokenBag().add(extra_tokens)
        assert game.bank == expected_bank
        assert card in game.players[0].cards_reserved
        assert game.players[0].num_reserved_cards == 1

    def test_game_make_move_reserve_card_no_wildcard_player(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        card = random.sample(game.cards.get_all_cards_on_tables(), 1)[0]
        action = ReserveCard(card)
        for _ in range(5):
            game.bank.remove_token({Token.YELLOW: 1})
        game.make_move_for_current_player(action)
        expected_bank = Bank(num_players)
        for _ in range(5):
            expected_bank.remove_token({Token.YELLOW: 1})
        assert game.players[0].token_reserved == TokenBag()
        assert game.bank == expected_bank
        assert card in game.players[0].cards_reserved
        assert game.players[0].num_reserved_cards == 1


class TestingGameMakeMoveEndTurn:
    def test_game_end_player_turn_default(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        game.make_move_for_current_player(action)
        assert game.current_player_idx == 1
        assert game.current_player == players[1]
        assert game.meta_data.turns_played == 0
        assert not game.is_final_turn()

    def test_game_end_player_turn_multiple_players(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        for i in range(num_players - 1):
            assert game.current_player_idx == i
            assert game.current_player == players[i]
            game.make_move_for_current_player(action)
            assert game.current_player_idx == i + 1
            assert game.current_player == players[i + 1]
            assert game.meta_data.turns_played == 0
            assert not game.is_final_turn()

    def test_game_end_player_turn_another_turn(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        for i in range(num_players - 1):
            game.make_move_for_current_player(action)
        # Test after last player's action, starts a new turn
        assert game.current_player_idx == num_players - 1
        assert game.current_player == players[num_players - 1]
        game.make_move_for_current_player(action)
        assert game.current_player_idx == 0
        assert game.current_player == players[0]
        assert game.meta_data.turns_played == 1
        assert not game.is_final_turn()

    def test_game_end_player_turn_final_turn(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        for i in range(num_players - 1):
            game.make_move_for_current_player(action)
        # Test end of turn with a player having >= prestige points to winning.
        assert game.current_player_idx == num_players - 1
        assert game.current_player == players[num_players - 1]
        game.players[random.randint(0, 3)].prestige_points = 15
        game.make_move_for_current_player(action)
        assert game.current_player_idx == 0
        assert game.current_player == players[0]
        assert game.meta_data.turns_played == 1
        assert game.is_final_turn()
        assert game.meta_data.state == GameState.FINISHED

    def test_game_end_player_turn_final_turn_winner(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        random_winner_idx = random.randint(0, 3)
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        game.players[random_winner_idx].prestige_points = 15
        for _ in range(num_players):
            game.make_move_for_current_player(action)
        assert game.meta_data.state == GameState.FINISHED
        assert game.get_winner() == game.players[random_winner_idx]

    def test_game_end_player_turn_final_turn_multiple_eligible_winner(self) -> None:
        num_players = 4
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players)
        game.initialize()
        # Add prestige points and cards to players
        game.players[0].prestige_points = 14
        game.players[1].prestige_points = 16
        game.players[2].prestige_points = 15
        game.players[3].prestige_points = 16
        test_cards = TestingCardManager.card_list_for_testing()
        for _ in range(2):
            card = test_cards.pop()
            game.players[1].add_to_owned_cards(card)
        for _ in range(3):
            card = test_cards.pop()
            game.players[3].add_to_owned_cards(card)
        assert game.players[1].prestige_points == 16
        assert game.players[3].prestige_points == 16
        colors = (Token.GREEN, Token.BLACK, Token.BLUE)
        action = Reserve3UniqueColorTokens(colors)
        for _ in range(num_players):
            game.make_move_for_current_player(action)
        assert game.meta_data.state == GameState.FINISHED
        assert game.get_winner() == game.players[1]


class TestingGameMakeMovePurchaseCard:
    def test_game_can_make_move_purchase_card_True_all(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add bonuses
        bonus_cost = {Token.GREEN: 1,
                      Token.BLUE: 2}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        # Add regular tokens
        token_cost = {Token.GREEN: 1,
                      Token.WHITE: 1,
                      Token.BLUE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        # Add wildcard tokens
        game.current_player.add_token({Token.YELLOW: 1})
        game.bank.remove_token({Token.YELLOW: 1})
        assert game.can_make_move_for_current_player(action)

    def test_game_can_make_move_purchase_card_False_all(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        assert not game.can_make_move_for_current_player(action)
        # Add bonuses
        bonus_cost = {Token.GREEN: 1,
                      Token.BLUE: 1}  # One missing Token.BLUE
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        assert not game.can_make_move_for_current_player(action)
        # Add regular tokens
        token_cost = {Token.GREEN: 1,
                      Token.WHITE: 1,
                      Token.BLUE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        assert not game.can_make_move_for_current_player(action)
        # Add wildcard tokens
        game.current_player.add_token({Token.YELLOW: 1})
        game.bank.remove_token({Token.YELLOW: 1})
        assert not game.can_make_move_for_current_player(action)

    def test_game_make_move_purchase_card_just_bonus(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add bonuses
        bonus_cost = {Token.GREEN: 2,
                      Token.WHITE: 1,
                      Token.BLUE: 4}
        bonus_extra = {Token.BLACK: 1,
                       Token.WHITE: 1}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        game.make_move_for_current_player(action)
        assert game.players[0].token_reserved == TokenBag()
        assert game.bank == Bank(num_players)
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_just_token(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        extra_tokens_per_color = 1
        # Add tokens
        token_cost = {Token.GREEN: 2,
                      Token.WHITE: 1,
                      Token.BLUE: 4}
        token_extra = {Token.RED: 1,
                       Token.WHITE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        for color in token_extra:
            for _ in range(token_extra[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        for color in token_extra:
            for _ in range(token_extra[color]):
                expected_player_tokens.add({color: 1})
                expected_bank.remove_token({color: 1})
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_just_wildcard(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[0]
        card_cost = {Token.WHITE: 4}
        card_bonus = Token.RED
        card_prestige_points = 1
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add wildcards
        extra_wildcard = 1
        for _ in range(sum(card_cost.values()) + extra_wildcard):
            game.current_player.add_token({Token.YELLOW: 1})
            game.bank.remove_token({Token.YELLOW: 1})
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        for _ in range(extra_wildcard):
            expected_player_tokens.add({Token.YELLOW: 1})
            expected_bank.remove_token({Token.YELLOW: 1})
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_no_bonus(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add tokens
        token_cost = {Token.GREEN: 2,
                      Token.WHITE: 1,
                      Token.BLUE: 3}
        token_extra = {Token.RED: 1,
                       Token.WHITE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        game.current_player.add_token(token_extra)
        game.bank.remove_token(token_extra)
        # Add wildcards
        wildcard_cost = 1
        extra_wildcard = 1
        game.current_player.add_token({Token.YELLOW: (wildcard_cost +
                                                      extra_wildcard)})
        game.bank.remove_token({Token.YELLOW: (wildcard_cost +
                                               extra_wildcard)})
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        expected_player_tokens.add(token_extra)
        expected_bank.remove_token(token_extra)
        expected_player_tokens.add({Token.YELLOW: extra_wildcard})
        expected_bank.remove_token({Token.YELLOW: extra_wildcard})
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_no_token(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add bonuses
        bonus_cost = {Token.GREEN: 2,
                      Token.WHITE: 1,
                      Token.BLUE: 3}
        bonus_extra = {Token.BLACK: 1,
                       Token.WHITE: 1}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        # Add wildcards
        wildcard_cost = 1
        extra_wildcard = 1
        game.current_player.add_token({Token.YELLOW: (wildcard_cost +
                                                      extra_wildcard)})
        game.bank.remove_token({Token.YELLOW: (wildcard_cost +
                                               extra_wildcard)})
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        expected_player_tokens.add({Token.YELLOW: extra_wildcard})
        expected_bank.remove_token({Token.YELLOW: extra_wildcard})
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_no_wildcard(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add tokens
        token_cost = {Token.GREEN: 1,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 2,
                       Token.WHITE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        for color in token_extra:
            for _ in range(token_extra[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        # Add bonuses
        bonus_cost = {Token.GREEN: 1,
                      Token.WHITE: 1,
                      Token.BLUE: 3}
        bonus_extra = {Token.BLACK: 1,
                       Token.WHITE: 1}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        expected_player_tokens.add(token_extra)
        expected_bank.remove_token(token_extra)
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_all(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add tokens
        token_cost = {Token.GREEN: 1,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 2,
                       Token.WHITE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        for color in token_extra:
            for _ in range(token_extra[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        # Add bonuses
        bonus_cost = {Token.GREEN: 1,
                      Token.WHITE: 1,
                      Token.BLUE: 2}
        bonus_extra = {Token.BLACK: 1,
                       Token.WHITE: 1}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        # Add wildcards
        wildcard_cost = 1
        extra_wildcard = 1
        game.current_player.add_token({Token.YELLOW: (wildcard_cost +
                                                      extra_wildcard)})
        game.bank.remove_token({Token.YELLOW: (wildcard_cost +
                                               extra_wildcard)})
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        expected_player_tokens.add(token_extra)
        expected_bank.remove_token(token_extra)
        expected_player_tokens.add({Token.YELLOW: extra_wildcard})
        expected_bank.remove_token({Token.YELLOW: extra_wildcard})
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_all_from_reserved(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add tokens
        token_cost = {Token.GREEN: 1,
                      Token.BLUE: 1}
        token_extra = {Token.GREEN: 2,
                       Token.WHITE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        for color in token_extra:
            for _ in range(token_extra[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        # Add bonuses
        bonus_cost = {Token.GREEN: 1,
                      Token.WHITE: 1,
                      Token.BLUE: 2}
        bonus_extra = {Token.BLACK: 1,
                       Token.WHITE: 1}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        for color in bonus_extra:
            for _ in range(bonus_extra[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        # Add wildcards
        wildcard_cost = 1
        extra_wildcard = 1
        game.current_player.add_token({Token.YELLOW: (wildcard_cost +
                                                      extra_wildcard)})
        game.bank.remove_token({Token.YELLOW: (wildcard_cost +
                                               extra_wildcard)})
        # Reserve the card before purchase
        game.current_player.add_to_reserved_cards(card)
        game.cards.remove_card_from_tables(card)
        assert game.current_player.num_reserved_cards == 1
        assert card in game.current_player.cards_reserved
        game.make_move_for_current_player(action)
        expected_player_tokens = TokenBag()
        expected_bank = Bank(num_players)
        expected_player_tokens.add(token_extra)
        expected_bank.remove_token(token_extra)
        expected_player_tokens.add({Token.YELLOW: extra_wildcard})
        expected_bank.remove_token({Token.YELLOW: extra_wildcard})
        assert game.players[0].token_reserved == expected_player_tokens
        assert game.bank == expected_bank
        assert card in game.players[0].cards_owned
        assert not game.cards.is_card_in_tables(card)
        assert game.players[0].num_reserved_cards == 0
        assert card not in game.players[0].cards_reserved
        assert game.players[0].prestige_points == card_prestige_points
        assert game.players[0].bonus_owned.tokens[card_bonus] == 1

    def test_game_make_move_purchase_card_eligible_for_noble(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        # The last bonus required is gotten from the card purchase
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        # Noble is valid, but injected to eliminate randomness
        noble = Noble({Token.GREEN: 4, Token.WHITE: 0, Token.BLUE: 0,
                       Token.BLACK: 0, Token.RED: 4})
        if noble not in game.nobles:
            game.nobles[0] = noble
        action = PurchaseCard(card)
        # Add tokens
        token_cost = {Token.WHITE: 1,
                      Token.BLUE: 4}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        # Add bonuses
        bonus_cost = {Token.GREEN: 2}
        bonus_noble = {Token.GREEN: 3,
                       Token.RED: 3}
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        for color in bonus_noble:
            for _ in range(bonus_noble[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        assert not game.current_player.is_eligible_for_noble(noble)
        game.make_move_for_current_player(action)
        assert noble in game.players[0].nobles_owned
        assert noble not in game.nobles
        # game starts with n + 1 nobles for n players
        assert len(game.nobles) == num_players
        assert game.players[0].prestige_points == (card.prestige_points +
                                                   noble.prestige_points)

    def test_game_make_move_purchase_card_all_error(self) -> None:
        num_players = 2
        players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
        game = Game(players=players,
                    cards=CardGenerator.generate_cards(shuffled=False))
        game.initialize()
        card = game.cards.get_all_cards_on_tables()[7]
        card_cost = {Token.GREEN: 2,
                     Token.WHITE: 1,
                     Token.BLUE: 4}
        card_bonus = Token.RED
        card_prestige_points = 2
        assert card.token_cost == TokenBag().add(card_cost)
        assert card.bonus_color == card_bonus
        assert card.prestige_points == card_prestige_points
        action = PurchaseCard(card)
        # Add tokens
        token_cost = {Token.GREEN: 1,
                      Token.BLUE: 1}
        for color in token_cost:
            for _ in range(token_cost[color]):
                game.current_player.add_token({color: 1})
                game.bank.remove_token({color: 1})
        # Add bonuses
        bonus_cost = {Token.GREEN: 1,
                      Token.WHITE: 1,
                      Token.BLUE: 1}  # One missing Token.BLUE
        for color in bonus_cost:
            for _ in range(bonus_cost[color]):
                mock_card = Card(level=1, prestige_points=0, bonus_color=color,
                                 token_cost=TokenBag().add({Token.RED: 1}))
                game.current_player.add_to_owned_cards(mock_card)
        # Add wildcards
        wildcard_cost = 1
        game.current_player.add_token({Token.YELLOW: wildcard_cost})
        with pytest.raises(ValueError) as e:
            game.make_move_for_current_player(action)
