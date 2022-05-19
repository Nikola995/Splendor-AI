# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:45:24 2022.

@author: Nikola
"""

from dataclasses import dataclass, field
from typing import Callable
from functools import partial
from copy import deepcopy
from random import shuffle, seed
from itertools import combinations, product
from game_base.nobles import Noble, generate_nobles
from game_base.cards import Card, generate_cards_from_pickle

seed(10)


# %% Game-related classes
# %%% Token Custom Errors
class TokenThresholdError(Exception):
    pass


class TooManyTokensForPlayerError(Exception):
    pass


class IncorrectInputError(Exception):
    pass


# %%% Game entities
# TODO Make it a singleton (refactor)
@dataclass
class Bank:
    # Available tokens per color (type)
    token_available: dict[str, int] = field(default_factory=lambda: (
        {"green": 7,
         "white": 7,
         "blue": 7,
         "black": 7,
         "red": 7,
         # Yellow is the wildcard
         "yellow": 5}))

    def _can_remove_token(self, amount_to_remove: dict[str, int],
                          threshold=0) -> bool:
        """Check if tokens of given colors can be removed."""
        for color in amount_to_remove:
            if (self.token_available[color] - amount_to_remove[color]
                    < threshold):
                return False
        return True

    # TODO: change game errors to return False
    def _remove_token(self, amount_to_remove: dict[str, int],
                      threshold=0, verbose=0) -> None:
        """Remove an amount of tokens for given colors.

        (*Use in action functions only for wildcard (yellow), other colors
         have already implemented methods)

        Parameters
        ----------
        amount_to_remove : dict[str, int]
            A dict of colors (keys) and amount of tokens to remove (values)

        Raises
        ------
        IncorrectInputError
            Raise if invalid color names are given

        TokenThresholdError
            Raise if the amount of tokens removed for a given color leaves the
            bank with negative amount ( < 0)
        """
        if not set(amount_to_remove.keys()).issubset(
                self.token_available.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_remove_token(amount_to_remove, threshold):
            for color in amount_to_remove:
                self.token_available[color] -= amount_to_remove[color]
            else:
                raise TokenThresholdError("Tried to take more tokens"
                                          "than available in the bank")

    # TODO: Add an input type check
    def add_token(self, amount_to_add: dict[str, int]) -> None:
        """Add an amount of tokens for given colors.

        Parameters
        ----------
        amount_to_add : dict[str,int]
            A dict of colors (keys) and amount of tokens to add (values)

        Raises
        ------
        IncorrectInputError
            Raised if invalid color names are given
        """
        if not set(amount_to_add.keys()).issubset(self.token_available.keys()):
            raise IncorrectInputError("Invalid colors were given")
        for color in amount_to_add:
            self.token_available[color] += amount_to_add[color]

    # TODO: change game errors to return False
    # TODO: Add an proper input type check
    def remove_3_different_color_tokens(self, color_list: list[str],
                                        verbose=0) -> None:
        """Remove 3 tokens of different color from the bank.

        Parameters
        ----------
        color_list : list[str]
            List of size 3 of colors

        Raises
        ------
        IncorrectInputError
            Raised if 3 colors are not given, or an incorrect color is given,
            or 'yellow' is given

        TokenThresholdError
            Bank has 0 tokens of a given color, can't remove 1.
        """
        if len(color_list) != 3:
            raise IncorrectInputError("3 colors were not given")
        if 'yellow' in color_list:
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        try:
            self._remove_token(dict.fromkeys(color_list, 1))
        except TokenThresholdError as TTE:
            print(TTE)

    # TODO: add an input type check
    # TODO: change game errors to return False
    def remove_2_same_color_tokens(self, color: str, verbose=0) -> None:
        """Remove 2 tokens of the same color from the bank.

        Only if the bank has 4 tokens of that color available.

        Parameters
        ----------
        color_list : str
            Color for 2 tokens

        Raises
        ------
        IncorrectInputError
            Raised if an incorrect color is given,
            or 'yellow' is given
        TokenThresholdError
            Bank has less than 4 tokens of a given color, can't remove 2.
        """
        if color == 'yellow':
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        try:
            self._remove_token({color: 2}, threshold=2)
        except TokenThresholdError as TTE:
            print(TTE)


@dataclass(order=True)
class Player:
    # TODO make it a user account with elo (in the future)
    # For now just use a string name
    player_id: str
    # Reserved tokens per color (type)
    token_reserved: dict[str, int] = field(default_factory=lambda: (
        {"green": 0,
         "white": 0,
         "blue": 0,
         "black": 0,
         "red": 0,
         "yellow": 0}))
    # Owned Cards
    cards_owned: list[Card] = field(default_factory=list)
    # Reserved Cards
    cards_reserved: dict[str, Card] = field(default_factory=dict)
    # Owned Nobles
    nobles_owned: list[Noble] = field(default_factory=list)
    # Bonuses per color (type)
    bonus_owned: dict[str, int] = field(default_factory=lambda: ({"green": 0,
                                                                  "white": 0,
                                                                  "blue": 0,
                                                                  "black": 0,
                                                                  "red": 0}))
    # Prestige points
    prestige_points: int = 0

    def _can_remove_token(self, amount_to_remove: dict[str, int]) -> bool:
        """Check if tokens of given colors can be removed."""
        for color in amount_to_remove:
            if (self.token_reserved[color] - amount_to_remove[color] < 0):
                return False
        return True
    
    # TODO: add a docstring
    # TODO: create an action_check for this
    def remove_token(self, amount_to_remove: dict[str, int]) -> None:
        """dafg.

        Parameters
        ----------
        amount_to_remove : dict[str, int]
            DESCRIPTION.

        Raises
        ------
        IncorrectInputError
            DESCRIPTION.
        TokenThresholdError
            DESCRIPTION.

        Returns
        -------
        None
            DESCRIPTION.

        """
        if not set(amount_to_remove.keys()).issubset(
                self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_remove_token(amount_to_remove):
            for color in amount_to_remove:
                self.token_reserved[color] -= amount_to_remove[color]
            else:
                raise TokenThresholdError("Tried to take more tokens"
                                          f"from {self.player_id} than"
                                          "available")

    def _can_add_token(self, amount_to_add: dict[str, int]) -> bool:
        """Check if tokens of given colors can be added."""
        if (sum(self.token_reserved.values()) +
                sum(amount_to_add.values()) > 10):
            return False
        else:
            return True

    # TODO: add a docstring
    # TODO: create an action_check for this
    def add_token(self, amount_to_add: dict[str, int]) -> None:
        if not set(amount_to_add.keys()).issubset(self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_add_token(amount_to_add):
            for color in amount_to_add:
                self.token_reserved[color] += amount_to_add[color]
        else:
            raise TooManyTokensForPlayerError("A player cannot have more than "
                                              "10 tokens in total reserved")

    # TODO: add a docstring
    # TODO: add an input type check
    # TODO: change to not have yellow_replaces as input
    def can_purchase_card(self, card: Card,
                          yellow_replaces: dict[str, int]) -> bool:
        if not set(yellow_replaces.keys()).issubset(
                self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if sum(yellow_replaces.values()) > self.token_reserved['yellow']:
            raise IncorrectInputError(f"{sum(yellow_replaces.values())} yellow"
                                      " tokens given as collateral, but only "
                                      f"{self.token_reserved['yellow']} yellow"
                                      " tokens available")
        player_buying_power = 0
        for color in card.token_cost:
            player_buying_power = (self.bonus_owned[color] +
                                   self.token_reserved[color] +
                                   yellow_replaces[color])
            if card.token_cost[color] > player_buying_power:
                return False
        return True

    # TODO: add an input type check
    def add_to_owned_cards(self, card: Card) -> None:
        """Add card to list of owned cards.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        card : Card
            Card to add to owned cards
        """
        self.cards_owned.append(card)
        self.bonus_owned[card.bonus_color] += 1
        self.prestige_points += card.prestige_points

    # TODO: add an input type check
    def is_eligible_for_noble(self, noble: Noble, verbose=0) -> bool:
        """Check if the player is eligible to own the noble.
        If the player's owned bonuses are more or equal to the
        required bonuses of the noble, they are eligible.

        Parameters
        ----------
        noble : Noble
            The noble whose bonuses we check against

        Returns
        -------
        bool
            Eligibility of the player to own the noble

        """
        for color in noble.bonus_required:
            # If the player doesn't have enough bonuses for the noble
            if self.bonus_owned[color] < noble.bonus_required[color]:
                return False
        # If all the checks pass, that must mean the player is eligible
        return True

    # TODO: add an input type check
    def add_to_owned_nobles(self, noble: Noble) -> None:
        """Add noble to list of owned nobles.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        noble : Noble
            Noble to add to owned nobles
        """
        self.nobles_owned.append(noble)
        self.prestige_points += noble.prestige_points
# %%% Actions


class ActionNotPossibleError(Exception):
    pass


Action = Callable[[Player, Bank], None]


# TODO add a docstring
# TODO change func to return bool
def reserve_3_different_color_tokens(player: Player, bank: Bank,
                                     color_list: list[str],
                                     verbose=0) -> None:
    try:
        bank.remove_3_different_color_tokens(color_list)
        player.add_token(dict.fromkeys(color_list, 1))
        if verbose == 1:
            print(f"{player.player_id} has reserved a {color_list[0]}, "
                  f"{color_list[1]} and {color_list[2]} token")
    except Exception as e:
        raise ActionNotPossibleError(str(e))


# TODO add a docstring
# TODO change func to return bool
def reserve_2_same_color_tokens(player: Player, bank: Bank,
                                color: str, verbose=0) -> None:
    try:
        bank.remove_2_same_color_tokens(color)
        player.add_token({color: 2})
        if verbose == 1:
            print(f"{player.player_id} has reserved 2 {color} tokens")
    except Exception as e:
        raise ActionNotPossibleError(str(e))


# TODO add a docstring
# TODO change func to return bool (false if exception)
# TODO test if the try statement reverts if the player has >10 tokens
def reserve_a_card(player: Player, bank: Bank, card: Card, card_id: str,
                   verbose=0) -> bool:
    if len(player.cards_reserved) == 3:
        raise ActionNotPossibleError("Player has 3 reserved cards, "
                                     "can't reserve more")
    try:
        player.cards_reserved[card_id] = (card)
        if bank.token_available['yellow'] > 0:
            bank._remove_token({'yellow': 1})
            player.add_token({'yellow': 1})
        if verbose == 1:
            print(f"{player.player_id} has reserved {card_id}")
        return True
    except Exception as e:
        raise ActionNotPossibleError(str(e))


# TODO add a docstring
def _purchase_check(remaning_cost: int, card: Card, card_id:  str,
                    player: Player, is_reserved: bool) -> bool:
    if remaning_cost == 0:
        player.add_to_owned_cards(card)
        # If the card is reserved, remove from there
        if is_reserved:
            player.cards_reserved.pop(card_id)
        return True
    else:
        return False


# TODO add a docstring
def purchase_a_card(player: Player, bank: Bank, card_id: str,
                    card: Card = None, is_reserved: bool = False,
                    yellow_replaces: dict[str, int] = {"green": 0,
                                                       "white": 0,
                                                       "blue": 0,
                                                       "black": 0,
                                                       "red": 0},
                    verbose=0) -> bool:
    try:
        # If the action is purchasing a reserved card
        if is_reserved:
            # Get the card by card id
            card = player.cards_reserved[card_id]
        if player.can_purchase_card(card, yellow_replaces):
            card_token_cost = deepcopy(card.token_cost)
            # Reduce the cost by the owned bonuses
            for color in player.bonus_owned:
                if player.bonus_owned[color] > card_token_cost[color]:
                    card_token_cost[color] = 0
                else:
                    card_token_cost[color] -= player.bonus_owned[color]
            # If the card can be purchased by just bonuses
            if _purchase_check(remaning_cost=sum(card_token_cost.values()),
                               card=card, card_id=card_id, player=player,
                               is_reserved=is_reserved):
                if verbose == 1:
                    print(f"{player.player_id} purchased "
                          f"{card_id} with bonuses")
                return True

            # Reduce the cost by the yellow tokens per color
            for color in yellow_replaces:
                if card_token_cost[color] - yellow_replaces[color] >= 0:
                    card_token_cost[color] -= yellow_replaces[color]
                else:
                    raise IncorrectInputError("Too many yellow tokens given "
                                              f"for color {color}")
            # Give all the yellow tokens back to the bank
            player.remove_token({'yellow': sum(yellow_replaces.values())})
            bank.add_token({'yellow': sum(yellow_replaces.values())})

            # If the card can be purchased by just yellow tokens
            if _purchase_check(remaning_cost=sum(card_token_cost.values()),
                               card=card, card_id=card_id, player=player,
                               is_reserved=is_reserved):
                if verbose == 1:
                    print(f"{player.player_id} purchased {card_id} with "
                          "wildcard tokens")
                return True

            # Finish the purchase with the reserved tokens
            for color in card.token_cost:
                if card_token_cost[color] > 0:
                    # Give the tokens back to the bank
                    player.remove_token({color: card_token_cost[color]})
                    bank.add_token({color: card_token_cost[color]})
                    card_token_cost[color] = 0

            # If the card can be purchased by just yellow tokens
            if _purchase_check(remaning_cost=sum(card_token_cost.values()),
                               card=card, card_id=card_id, player=player,
                               is_reserved=is_reserved):
                if verbose == 1:
                    print(f"{player.player_id} has purchased {card_id}"
                          " with tokens")
                return True
            # Something went horribly wrong if you get here
            raise ActionNotPossibleError("The card still has a cost to it, "
                                         "something went horribly wrong")
        else:
            if verbose == 1:
                print(f"{player.player_id} cannot purchase {card_id}"
                      " with tokens")
            return False
    except Exception as e:
        raise ActionNotPossibleError(str(e))


# %%% Game custom errors
class NotEnoughPlayersError(Exception):
    pass


class TooManyPlayersError(Exception):
    pass


class GameNotOverError(Exception):
    pass


class TurnNotOverError(Exception):
    pass


# %% Game mechanics
# TODO add docstring
# TODO add a game_started and game_finished flags and not allow actions
# game_started = False or game_finished = True
@dataclass
class Game:
    # %% Game Assets
    _num_players: int = 0
    players: list[Player] = field(default_factory=list)
    # TODO Make the player order customizable - now it's FCFS
    bank: Bank = field(default_factory=Bank)
    # All of the cards not visible separated by level
    cards_deck_level_1: list[Card] = field(default_factory=list)
    cards_deck_level_2: list[Card] = field(default_factory=list)
    cards_deck_level_3: list[Card] = field(default_factory=list)
    # All of the cards visible separated by level
    cards_on_table_level_1: dict[str, Card] = field(default_factory=dict)
    cards_on_table_level_2: dict[str, Card] = field(default_factory=dict)
    cards_on_table_level_3: dict[str, Card] = field(default_factory=dict)
    # All the available nobles
    nobles: dict[str, Noble] = field(default_factory=dict)

    # TODO (after basic functionalities) create a game history record
    num_turns: int = 1
    curr_player_index: int = 0

    # %% Game initialization methods
    def _add_player(self, new_player, verbose=0) -> None:
        if self._num_players == 4:
            raise TooManyPlayersError("Can't add more players, "
                                      "4 is the maximum")
        self.players.append(new_player)
        if verbose == 1:
            print(f"Player {new_player.player_id} has joined the game")
        self._num_players = self._num_players + 1

    def _create_bank(self, verbose=0) -> None:
        if self._num_players < 2:
            raise NotEnoughPlayersError("Can't create bank for "
                                        f"{self._num_players} players, 2 is "
                                        "the minimum")
        self.bank = Bank()
        if self._num_players == 3:
            # Remove 2 tokens for each non-wildcard color if 3 players
            self.bank._remove_token({"green": 2,
                                     "white": 2,
                                     "blue": 2,
                                     "black": 2,
                                     "red": 2})
        elif self._num_players == 2:
            # Remove 3 tokens for each non-wildcard color if 2 players
            self.bank._remove_token({"green": 3,
                                     "white": 3,
                                     "blue": 3,
                                     "black": 3,
                                     "red": 3})
        if verbose == 1:
            print(f"Bank created for {self._num_players} players")

    def _generate_shuffle_pick_nobles(self, verbose=0) -> None:
        nobles_list = generate_nobles()
        shuffle(nobles_list)
        # Get n + 1 nobles for n players
        for index, noble in enumerate(nobles_list[0:self._num_players + 1]):
            self.nobles[f'noble_{index}'] = noble
        if verbose == 1:
            print(f"{len(self.nobles)} nobles added for "
                  f"{self._num_players} players")

    def _generate_shuffle_cards(self, verbose=0) -> None:
        # Import cards from pickle file (fastest)
        (self.cards_deck_level_1,
         self.cards_deck_level_2,
         self.cards_deck_level_3) = generate_cards_from_pickle()
        # Shuffle the decks
        shuffle(self.cards_deck_level_1)
        shuffle(self.cards_deck_level_2)
        shuffle(self.cards_deck_level_3)
        # Pop the last 4 cards of each deck and add them to the table
        for i in range(4):
            # generate a card id for all the popped cards
            c_id = f'card_{len(self.cards_deck_level_1)}'
            self.cards_on_table_level_1[c_id] = self.cards_deck_level_1.pop()
            c_id = f'card_{len(self.cards_deck_level_2) + 40}'
            self.cards_on_table_level_2[c_id] = self.cards_deck_level_2.pop()
            c_id = f'card_{len(self.cards_deck_level_3) + 70}'
            self.cards_on_table_level_3[c_id] = self.cards_deck_level_3.pop()
        if verbose == 1:
            print("Cards added, shuffled and 4 of each kind set on table")

    # TODO add a docstring
    def initialize_new_game(self, num_players=4, verbose=0) -> None:
        if verbose:
            print("Initializing New Game")
            print(f"Number of players:{num_players}")
        # TODO Add player names/accounts as input
        # Add the players
        for i in range(num_players):
            player_i = Player(f"Player_{i}")
            self._add_player(player_i, verbose)
        # After all the players have been added, create the bank
        self._create_bank(verbose)
        self._generate_shuffle_pick_nobles(verbose)
        self._generate_shuffle_cards(verbose)
        if verbose:
            print("New Game Initialized")

    # %% Active Game methods
    def is_game_over(self) -> bool: # noqa : D301
        """Check if at least one of the players reached 15 prestige points.

        Called at the end of each turn \
        after all the players performed an action

        Returns
        -------
        Bool
            State of the game (is over or is still ongoing)
        """ # noqa : W605
        for player in self.players:
            if player.prestige_points >= 15:
                return True
        return False

    # TODO Switch from raising error if not over to return None
    def declare_winner(self) -> Player:
        """Declare the winner of the game, if it's over.

        If it's one player with >=15 prestige points, they are the winner.
        If it's multiple players with >= 15 prestige points,
        pick the one with the most prestige points.
        if there is still a tie, choose the one with
        the least number of owned development cards.

        Returns
        -------
        Player
            The winner of the game
        """
        if not self.is_over():
            # If the game is not over, don't declare a winner
            raise GameNotOverError("None of the players have 15 or more "
                                   "prestige points")
        winner = []
        # Get all the players with >= 15 prestige points
        for player in self.players:
            if player.prestige_points >= 15:
                winner.append(player)
        # If there's more than one sort by most prestige points, then by
        # least owned cards
        if len(winner) > 1:
            winner = sorted(winner, key=lambda x: (-x.prestige_points,
                                                   len(x.cards_owned)))
        # Return the winner
        return winner[0]

    def is_turn_over(self) -> bool:
        """Check if all of the players have made an action.

        The index of the player next to move has to be less then
        the number of players.

        Returns
        -------
        bool
            State of the turn (is over or is ongoing)
        """
        return self.curr_player_index >= self._num_players

    # TODO Switch from raising error if not over to return bool
    def end_turn(self, verbose=0) -> bool:
        """Reset the player move order and increment the number of turns."""
        if not self.is_turn_over():
            if verbose == 1:
                print("Turn is not over, there are still players to move")
            return False
        if verbose == 1:
            print(f"End of Turn {self.num_turns}")
        self.num_turns += 1
        self.curr_player_index = 0
        return True

    # TODO Add the usecase of multiple available nobles in one turn
    # Currently just returns the first one
    def noble_check_for_player(self, player: Player, verbose=0) -> bool:
        """Check all the available nobles if the player can own them."""
        # Assume bonuses were correctly added
        # (faster than going through the list of owned cards every time)
        for noble_id in self.nobles:
            noble = self.nobles[noble_id]
            if player.is_eligible_for_noble(noble, verbose):
                player.add_to_owned_nobles(self.nobles)
                self.nobles.pop(noble_id)
                return True
        return False

    def end_move_for_player(self, verbose=0) -> None:
        """End the player's move and do a noble check for them."""
        # Do a noble check for the player
        if self.noble_check_for_player(self.players[self.curr_player_index],
                                       verbose) and verbose == 1:
            print(f"{self.players[self.curr_player_index]} has gained a noble")
        if verbose == 1:
            print(f"{self.players[self.curr_player_index].player_id}'s "
                  "turn has ended")
        # End the turn for the player
        self.curr_player_index += 1

    def current_player_to_move(self, verbose=0) -> Player:
        """Return the current player to move.

        Returns
        -------
        Player
            Next player to perform an action (make a move)
        """
        if verbose == 1:
            print("Current player to move is "
                  f"{self.players[self.curr_player_index].player_id}")
        return self.players[self.curr_player_index]

    # %%% Action-related methods
    # TODO Add verbose (successfull execution etc.)
    # %%%% Token-related actions
    def current_player_perform_token_action(self, action: Action,
                                            verbose=0) -> bool:
        """Give the current player to move a token action to perform.

        Parameters
        ----------
        action : Action
            partial(action, *additional_arguments)
            *additional_arguments are all inputs except Player and Bank

        verbose : int
            Set to 1 if you want a string output of the entire process,
            including errors. If set to 0, will just return False
            if there is an error.

        Returns
        -------
        bool
            Whether or not the action was performed succesfully
        """
        try:
            # Perform token-related action
            action(player=self.players[self.curr_player_index],
                   bank=self.bank, verbose=verbose)
            # If reached here, action was completed, so end their move
            self.end_move_for_player(verbose)
            return True
        except Exception as e:
            if verbose == 1:
                print(str(e))
            return False

    def _card_action_on_table(self, action: Action,
                              card_id: str, cards_on_table: dict[str, Card],
                              cards_deck: list[Card], verbose=0) -> bool:
        try:
            if card_id in cards_on_table:
                card = cards_on_table[card_id]
                # Perform card-related action
                if action(player=self.players[self.curr_player_index],
                          bank=self.bank, card=card, card_id=card_id,
                          verbose=verbose):
                    # Remove card from table
                    cards_on_table.pop(card_id)
                    # Add the next card from the deck (if there is one)
                    if len(cards_on_table) > 0:
                        new_card_id = f'card_{len(cards_deck)}'
                        cards_on_table[new_card_id] = cards_deck.pop()
                    return True
                else:
                    # If action wasn't performed and no error was raised
                    return False
            return False
        except Exception as e:
            raise e

    # TODO Add verbose (successfull execution, taking card,
    # removing card, etc.)
    def current_player_perform_card_action(self, action: Action,
                                           card_id: str = '',
                                           card_level: int = 0,
                                           is_reserved: bool = False,
                                           verbose=0) -> bool:
        """Give the current player to move an action to perform.

        Parameters
        ----------
        action : Action
            partial(action, *additional_arguments)
            *additional_arguments are all inputs except Player and Bank
        card_id : str
            if the action is card-related, add the card_id as input.
        card_level : int
            If the card_id is given, then the card level also needs
            to be added, so it can be taken from the right deck.
        verbose : int
            Set to 1 if you want a string output of the entire process,
            including errors. If set to 0, will just return False if there
            is an error.

        Returns
        -------
        bool
            Whether or not the action was performed succesfully
        """
        # Card-related actions
        try:
            # If the action is purchasing a reserved card (specific flag)
            if is_reserved:
                # Perform card-related action
                if action(player=self.players[self.curr_player_index],
                          bank=self.bank, card_id=card_id,
                          is_reserved=is_reserved, verbose=verbose):
                    # If reached here, action was completed,
                    # so end their move
                    self.end_move_for_player(verbose)
                    return True
                else:
                    # If action wasn't performed and no error was raised
                    return False
            # if the action is reserving a card or
            # purchasing a card on the table
            if card_level == 1:
                if self._card_action_on_table(
                        action=action, card_id=card_id,
                        cards_on_table=self.cards_on_table_level_1,
                        cards_deck=self.cards_deck_level_1,
                        verbose=verbose):
                    # If reached here, action was completed, so end their move
                    self.end_move_for_player(verbose)
                    return True
                else:
                    # If action wasn't performed and no error was raised
                    return False
            elif card_level == 2:
                if self._card_action_on_table(
                        action=action, card_id=card_id,
                        cards_on_table=self.cards_on_table_level_2,
                        cards_deck=self.cards_deck_level_2,
                        verbose=verbose):
                    # If reached here, action was completed, so end their move
                    self.end_move_for_player(verbose)
                    return True
                else:
                    # If action wasn't performed and no error was raised
                    return False
            elif card_level == 3:
                if self._card_action_on_table(
                        action=action, card_id=card_id,
                        cards_on_table=self.cards_on_table_level_3,
                        cards_deck=self.cards_deck_level_3,
                        verbose=verbose):
                    # If reached here, action was completed, so end their move
                    self.end_move_for_player(verbose)
                    return True
                else:
                    # If action wasn't performed and no error was raised
                    return False
            else:
                raise IncorrectInputError('Card level was an incorrect input')
            raise IncorrectInputError('Card id was an incorrect input')
        except Exception as e:
            raise e
# =============================================================================
#             if verbose == 1:
#                 print(str(e))
#             return False
# =============================================================================
    # TODO Maybe merge the different action types
    # TODO Add verbosity for failed actions
    # TODO Add verbose = 2 (ex. sucessful token taken from bank,
    # token given to player)
    # %% Game state representation
    #            -> numpy.matrix():

    # TODO Create a docstring
    def state(self, dense=0, verbose=0):
        # TODO implement a state representation
        # TODO add a game_id asset
        # This means also get state for players, bank, cards on table
        # dense - if true, return values as int (ex. player blue tokens = 5)
        # else return as sparse matrix (
        # (ex. player blue tokens = [1 1 1 1 1 0 0]))
        # verbose - print out the state in pretty string
        if verbose == 1:
            # Print global game assets
            print('Current game state')
            print(f'\tCurrent turn: {self.num_turns}')
            print('\tCurrent player to move: '
                  f'{self.players[self.curr_player_index].player_id}')
            # Print bank
            print('\nBank tokens available:')
            print('Color\tAmount')
            for color in self.bank.token_available:
                print(f'{color:<5}\t{self.bank.token_available[color]}')
            # Print players
            print('\nPlayers stats')
            for player in self.players:
                print(f'{player.player_id}')
                print(f'Prestige points: {player.prestige_points}')
                print('Color\tReserved tokens\tOwned bonuses')
                for color in player.bonus_owned:
                    print(f'{color:<5}\t'
                          f'{player.token_reserved[color]:<15}\t'
                          f'{player.bonus_owned[color]}')
                print(f"yellow\t{player.token_reserved['yellow']}")
                if player.cards_reserved:
                    print('\nReserved cards:')
                    for card_id in player.cards_reserved:
                        card = player.cards_reserved[card_id]
                        print(f'{card_id:<6}\tLevel: {card.level}\t'
                              f'\nPrestige points: {card.prestige_points}'
                              f'\tBonus: {card.bonus_color}'
                              '\nToken cost:')
                        for color in card.token_cost:
                            if card.token_cost[color] > 0:
                                print(f'{color:<5}\t'
                                      f'{card.token_cost[color]}')
            print("\nCards on the Table")
            # Print all cards on the Table
            for card_id in self.cards_on_table_level_1:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_1[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}',end='\t')
                print('\n')
            for card_id in self.cards_on_table_level_2:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_2[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}',end='\t')
                print('\n')
            for card_id in self.cards_on_table_level_3:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_3[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}',end='\t')
                print('\n')
            # TODO Print Nobles
            print('\nNobles:')
            for noble_id in self.nobles:
                noble = self.nobles[noble_id]
                print('Noble_id\tPrestige Points')
                print(f'{noble_id:<5}\t{noble.prestige_points}')
                print("Bonuses required:")
                for color in noble.bonus_required:
                    if noble.bonus_required[color] > 0:
                        print(f'{color:<5}\t'
                              f'{noble.bonus_required[color]}')
                print('\n')

        return None


# %% Possible and Legal actions for a player
# TODO generate all possible actions
def all_possible_actions() -> list[Action]:
    """Return all possible actions."""
    all_actions = {}
    current_actions_list = []
    # TODO Change to enum when refactoring
    colors = ["green", "white", "blue", "black", "red"]
    # All combinations of 3 different tokens
    for colors_combo_3 in combinations(colors, 3):
        current_actions_list.append(partial(reserve_3_different_color_tokens,
                                            color_list=list(colors_combo_3)))
    all_actions['reserve_3_different_color_tokens'] = current_actions_list
    # All colors for 2 tokens
    current_actions_list = []
    for color in colors:
        current_actions_list.append(partial(reserve_2_same_color_tokens,
                                            color=color))
    all_actions['reserve_2_same_color_tokens'] = current_actions_list
    # Reserving any slot on table
    # TODO extremely urgent to fix, card id is called in legal moves by
    # index of dict keys (very spaghetti code, fix with creating Table class)
    current_actions_list = []
    for level in range(1,4):
        for index in range(4):
            current_actions_list.append((reserve_a_card,
                                         {'level': level, 'index': index}))
    all_actions['reserve_a_card'] = current_actions_list
    # Purchasing any slot on table with all combinations
    # of wildcard token
    current_actions_list = []
    for token_input in product(range(6), range(6), range(6),
                               range(6), range(6)):
        if sum(token_input) <= 5:
            for level in range(1, 4):
                for index in range(4):
                    current_actions_list.append(
                        (purchase_a_card,
                         {'level': level,
                          'index': index,
                          'yellow_replaces': {colors[0]: token_input[0],
                                              colors[1]: token_input[1],
                                              colors[2]: token_input[2],
                                              colors[3]: token_input[3],
                                              colors[4]: token_input[4]}}))
    all_actions['purchase_a_card'] = current_actions_list
    # TODO purchasing any slot in reserved with all
    # combinations of 10 tokens as input
    return all_actions

# TODO generate all possible actions
def all_legal_actions_for_current_player(game: Game) -> list[Action]:
    """Return all legal actions for the current player to move."""
    all_actions = []
    player = game.current_player_to_move()
    # TODO all combinations of 3 different tokens 
    
    # TODO all colors for 2 tokens
    
    # TODO reserving any slot on table
    
    # TODO purchasing any slot on table
    return all_actions
# %% Running the game script
# TODO Create a docstring
def end_game_turn(game: Game, verbose=0) -> Player:
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

def main(): # noqa: D301
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
#game.current_player_to_move(verbose)
game.current_player_perform_token_action(
    partial(reserve_3_different_color_tokens,
            color_list=['green', 'white', 'black']),
    verbose=verbose)

# %%%
#game.current_player_to_move(verbose)
game.current_player_perform_token_action(
    partial(reserve_2_same_color_tokens,
            color='red'),
    verbose=verbose)
# %%%
#game.current_player_to_move(verbose)
game.current_player_perform_card_action(reserve_a_card,
                                        card_id='card_39', card_level=1,
                                        verbose=verbose)
# %%%
winner = end_game_turn(game, 1)
print(f"The winner is {winner}")

# %%%
#game.current_player_to_move(verbose)
game.current_player_perform_token_action(
    partial(reserve_3_different_color_tokens,
            color_list=['green', 'white', 'black']),
    verbose=verbose)
# %%%
#game.current_player_to_move(verbose)
game.current_player_perform_token_action(
    partial(reserve_3_different_color_tokens,
            color_list=['green', 'white', 'black']),
    verbose=verbose)
# %%%
#game.current_player_to_move(verbose)

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

game.current_player_perform_card_action(purchase_a_card,
                                        card_id='card_38', card_level=1,
                                        verbose=verbose)
# %%%
#print(game.current_player_to_move())
# %%%
#print(game.curr_player_index)
# %%%
#print(game.cards_on_table_level_1)
# %%%
game.players[2].token_reserved['green'] = 3
game.players[2].token_reserved['red'] = 3
game.players[2].token_reserved['blue'] = 3
game.players[2].token_reserved['black'] = 3
game.players[2].token_reserved['white'] = 3
# %%%
game.current_player_perform_card_action(purchase_a_card,
                                        card_id='card_38', card_level=1,
                                        verbose=verbose)
#game.state(verbose=1)
# %%%
all_actions = all_possible_actions()
#print(all_actions)
for action_type in all_actions:
    print(f"Number of {action_type}: {len(all_actions[action_type])}")
# %%
# =============================================================================
# for a in all_actions['purchase_a_card']:
#     print(a[1]['yellow_replaces'])
# =============================================================================
