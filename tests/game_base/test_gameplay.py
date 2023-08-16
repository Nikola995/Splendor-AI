import pytest
from game_base.cards import CardGenerator
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from game_base.banks import Bank
from game_base.actions import (ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from game_base.games import Game, GameState


def test_gameplay_game_1_players_2() -> None:
    num_players = 2
    players = [Player(f'test_player_{i + 1}') for i in range(num_players)]
    game = Game(players=players,
                cards=CardGenerator.generate_cards(shuffled=False))
    game.initialize()
    # Player 1
    game.make_move_for_current_player(Reserve2SameColorTokens(Token.WHITE))
    # Player 2
    game.make_move_for_current_player(Reserve3UniqueColorTokens((Token.GREEN,
                                                                 Token.BLUE,
                                                                 Token.RED)))
    assert game.meta_data.turns_played == 1
    # Player 1
    game.make_move_for_current_player(Reserve3UniqueColorTokens((Token.WHITE,
                                                                 Token.BLACK,
                                                                 Token.GREEN)))
    # Player 2
    game.make_move_for_current_player(Reserve3UniqueColorTokens((Token.WHITE,
                                                                 Token.BLUE,
                                                                 Token.RED)))
    assert game.meta_data.turns_played == 2
    # Player 1
    card_reserved_1 = game.cards.get_all_cards_on_tables()[4]
    game.make_move_for_current_player(ReserveCard(card_reserved_1))
    # Player 2
    card_2 = game.cards.get_all_cards_on_tables()[3]
    game.make_move_for_current_player(ReserveCard(card_2))
    assert game.meta_data.turns_played == 3
    # Player 1
    card_owned_1 = game.cards.get_all_cards_on_tables()[0]
    game.make_move_for_current_player(PurchaseCard(card_owned_1))
    # Player 2
    game.make_move_for_current_player(PurchaseCard(card_2))
    assert game.meta_data.turns_played == 4
    assert card_reserved_1 in game.players[0].cards_reserved
    assert game.players[0].num_reserved_cards == 1
    assert card_owned_1 in game.players[0].cards_owned
    assert game.players[0].bonus_owned.tokens[Token.RED] == 1
    assert game.players[0].prestige_points == 1
    expected_tokens_0 = {Token.BLACK: 1, Token.GREEN: 1}
    assert game.players[0].token_reserved == TokenBag().add(expected_tokens_0)
    assert card_2 not in game.players[1].cards_reserved
    assert game.players[1].num_reserved_cards == 0
    assert card_2 in game.players[1].cards_owned
    assert game.players[1].bonus_owned.tokens[Token.RED] == 1
    assert game.players[1].prestige_points == 0
    expected_tokens_1 = {Token.RED: 2,
                         Token.WHITE: 1,
                         Token.YELLOW: 1}
    assert game.players[1].token_reserved == TokenBag().add(expected_tokens_1)
    expected_bank = Bank(num_players)
    for color in expected_tokens_0:
        expected_bank.remove_token({color: expected_tokens_0[color]})
    for color in expected_tokens_1:
        expected_bank.remove_token({color: expected_tokens_1[color]})
    assert game.bank == expected_bank
    assert game.meta_data.state == GameState.IN_PROGRESS
