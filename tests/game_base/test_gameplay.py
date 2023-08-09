# # %% Tests
# # %%%
# # game.current_player_to_move(verbose)
# game.perform_action_for_current_player(
#     Reserve3DifferentColorTokens(params={'color_list': ['green',
#                                                         'white',
#                                                         'black']}),
#     verbose=verbose)

# # %%%
# # game.current_player_to_move(verbose)
# game.perform_action_for_current_player(
#     Reserve2SameColorTokens(params={'color': 'red'}),
#     verbose=verbose)
# # %%%
# # game.current_player_to_move(verbose)
# game.perform_action_for_current_player(
#     ReserveCard(params={'card_id': 'card_39'}),
#     verbose=verbose)
# # %%%
# winner = end_game_turn(game, 1)
# print(f"The winner is {winner}")

# # %%%
# # game.current_player_to_move(verbose)
# game.perform_action_for_current_player(
#     Reserve3DifferentColorTokens(params={'color_list': ['green',
#                                                         'white',
#                                                         'black']}),
#     verbose=verbose)
# # %%%
# # game.current_player_to_move(verbose)
# game.perform_action_for_current_player(
#     Reserve3DifferentColorTokens(params={'color_list': ['green',
#                                                         'white',
#                                                         'black']}),
#     verbose=verbose)
# # %%%
# # game.current_player_to_move(verbose)

# # =============================================================================
# # print(game.current_player_perform_card_action(partial(purchase_a_card,
# #                                     yellow_replaces = {"green":1,
# #                                        "white":0,
# #                                        "blue":0,
# #                                        "black":0,
# #                                        "red":0}),
# #                             card_id = 'card_39', is_reserved = True,
# #                             verbose = 1))
# # =============================================================================

# game.perform_action_for_current_player(
#     PurchaseCard(params={'card_id': 'card_38',
#                          'is_reserved': False,
#                          'yellow_replaces': {"green": 1, "white": 0,
#                                              "blue": 0, "black": 0,
#                                              "red": 0}}),
#     verbose=verbose)
# # %%%
# winner = end_game_turn(game, 1)
# print(f"The winner is {winner}")
# # %%%
# # print(game.current_player_to_move())
# # %%%
# # print(game.curr_player_index)
# # %%%
# # print(game.cards_on_table_level_1)
# # %%%
# game.players[2].token_reserved['green'] = 3
# game.players[2].token_reserved['red'] = 3
# game.players[2].token_reserved['blue'] = 3
# game.players[2].token_reserved['black'] = 3
# game.players[2].token_reserved['white'] = 3
# # %%%
# # Should return an IncorrectInputError
# # =============================================================================
# # game.perform_action_for_current_player(
# #     PurchaseCard(params={'card_id': 'card_38',
# #                          'is_reserved': False,
# #                          'yellow_replaces': {"green": 1, "white": 0,
# #                                              "blue": 0, "black": 0,
# #                                              "red": 0}}),
# #     verbose=verbose)
# # =============================================================================
# game.perform_action_for_current_player(
#     PurchaseCard(params={'card_id': 'card_38',
#                          'is_reserved': False,
#                          'yellow_replaces': {"green": 0, "white": 0,
#                                              "blue": 0, "black": 0,
#                                              "red": 0}}),
#     verbose=verbose)

# # %%%
# winner = end_game_turn(game, 1)
# print(f"The winner is {winner}")
# # game.state(verbose=1)
# # %%%
# all_actions = game.all_possible_actions()
# # print(all_actions)
# for action_type in all_actions:
#     print(f"Number of {action_type}: {len(all_actions[action_type])}")
# # %%%
# print(sum(game.current_player_to_move().token_reserved.values()))
# # %%%
# for a in all_actions['reserve_card']:
#     print(a.print_string())
# # %%%
# for a in all_actions['purchase_card']:
#     if a.params['is_reserved']:
#         print(a.print_string())
# # %%%
# legal_actions = game.all_legal_actions()
# for action_type in legal_actions:
#     print(f"Number of legal {action_type}: {len(legal_actions[action_type])}")
# # %%%
# temp_tokens = game.bank.token_available
# game.bank.token_available = {"green": 4, "white": 1,
#                              "blue": 1, "black": 4,
#                              "red": 0}

# legal_actions = game.all_legal_actions()
# for action_type in legal_actions:
#     print(f"Number of legal {action_type}: {len(legal_actions[action_type])}")
# game.bank.token_available = temp_tokens
# # %%%
# temp_tokens = game.current_player_to_move().token_reserved['black']
# game.current_player_to_move().token_reserved['black'] = 4

# legal_actions = game.all_legal_actions()
# for action_type in legal_actions:
#     print(f"Number of legal {action_type}: {len(legal_actions[action_type])}")
# game.current_player_to_move().token_reserved['black'] = temp_tokens
# # %%%