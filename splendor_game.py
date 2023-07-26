# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:45:24 2022.

@author: Nikola
"""

from game_base.games import Game
from game_base.players import Player
from game_base.utils import TurnNotOverError
from game_base.actions import (Reserve3DifferentColorTokens,
                               Reserve2SameColorTokens,
                               ReserveCard, PurchaseCard)
from random import seed

seed(10)

# %% Running the game script
def end_game_turn(game: Game, verbose=0) -> Player:
    """End the turn in the game if possible."""
    # If all players have made a move (the turn is over)
    if game.is_turn_over():
        # Check if the game is over
        if game.is_game_over():
            # Declare the winner if the game is over
            winner = game.declare_winner()
            return winner
        else:
            # Else end the turn and continue playing
            if not game.end_turn(verbose):
                raise TurnNotOverError('The turn was not ended when'
                                       'it should have')
            return None
    # If the turn is not over, continue playing
    else:
        return None


def main():  # noqa: D301
    # Pre-game meta-data
    num_players = 2
    verbose = 1
    # Setup the game
    game = Game()
    game.initialize_new_game(num_players, verbose)
    # print(game)


if __name__ == '__main__':
    # TODO move everything in the main() function after adding functionalities
    # main()

    # Pre-game meta-data
    num_players = 3
    verbose = 1

    # Setup the game
    game = Game()
    game.initialize_new_game(num_players, verbose)
    # print(game)

    # Start the game
    print("New Game Started")

# %% Tests
# %%%
# game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve3DifferentColorTokens(params={'color_list': ['green',
                                                        'white',
                                                        'black']}),
    verbose=verbose)

# %%%
# game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve2SameColorTokens(params={'color': 'red'}),
    verbose=verbose)
# %%%
# game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    ReserveCard(params={'card_id': 'card_39'}),
    verbose=verbose)
# %%%
winner = end_game_turn(game, 1)
print(f"The winner is {winner}")

# %%%
# game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve3DifferentColorTokens(params={'color_list': ['green',
                                                        'white',
                                                        'black']}),
    verbose=verbose)
# %%%
# game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve3DifferentColorTokens(params={'color_list': ['green',
                                                        'white',
                                                        'black']}),
    verbose=verbose)
# %%%
# game.current_player_to_move(verbose)

# =============================================================================
# print(game.current_player_perform_card_action(partial(purchase_a_card,
#                                     yellow_replaces = {"green":1,
#                                        "white":0,
#                                        "blue":0,
#                                        "black":0,
#                                        "red":0}),
#                             card_id = 'card_39', is_reserved = True,
#                             verbose = 1))
# =============================================================================

game.perform_action_for_current_player(
    PurchaseCard(params={'card_id': 'card_38',
                         'is_reserved': False,
                         'yellow_replaces': {"green": 1, "white": 0,
                                             "blue": 0, "black": 0,
                                             "red": 0}}),
    verbose=verbose)
# %%%
winner = end_game_turn(game, 1)
print(f"The winner is {winner}")
# %%%
# print(game.current_player_to_move())
# %%%
# print(game.curr_player_index)
# %%%
# print(game.cards_on_table_level_1)
# %%%
game.players[2].token_reserved['green'] = 3
game.players[2].token_reserved['red'] = 3
game.players[2].token_reserved['blue'] = 3
game.players[2].token_reserved['black'] = 3
game.players[2].token_reserved['white'] = 3
# %%%
# Should return an IncorrectInputError
# =============================================================================
# game.perform_action_for_current_player(
#     PurchaseCard(params={'card_id': 'card_38',
#                          'is_reserved': False,
#                          'yellow_replaces': {"green": 1, "white": 0,
#                                              "blue": 0, "black": 0,
#                                              "red": 0}}),
#     verbose=verbose)
# =============================================================================
game.perform_action_for_current_player(
    PurchaseCard(params={'card_id': 'card_38',
                         'is_reserved': False,
                         'yellow_replaces': {"green": 0, "white": 0,
                                             "blue": 0, "black": 0,
                                             "red": 0}}),
    verbose=verbose)

# %%%
winner = end_game_turn(game, 1)
print(f"The winner is {winner}")
# game.state(verbose=1)
# %%%
all_actions = game.all_possible_actions()
# print(all_actions)
for action_type in all_actions:
    print(f"Number of {action_type}: {len(all_actions[action_type])}")
# %%%
print(sum(game.current_player_to_move().token_reserved.values()))
# %%%
for a in all_actions['reserve_card']:
    print(a.print_string())
# %%%
for a in all_actions['purchase_card']:
    if a.params['is_reserved']:
        print(a.print_string())
# %%%
legal_actions = game.all_legal_actions()
for action_type in legal_actions:
    print(f"Number of legal {action_type}: {len(legal_actions[action_type])}")
# %%%
temp_tokens = game.bank.token_available
game.bank.token_available = {"green": 4, "white": 1,
                             "blue": 1, "black": 4,
                             "red": 0}

legal_actions = game.all_legal_actions()
for action_type in legal_actions:
    print(f"Number of legal {action_type}: {len(legal_actions[action_type])}")
game.bank.token_available = temp_tokens
# %%%
temp_tokens = game.current_player_to_move().token_reserved['black']
game.current_player_to_move().token_reserved['black'] = 4

legal_actions = game.all_legal_actions()
for action_type in legal_actions:
    print(f"Number of legal {action_type}: {len(legal_actions[action_type])}")
game.current_player_to_move().token_reserved['black'] = temp_tokens
# %%%
