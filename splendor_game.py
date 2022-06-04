# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:45:24 2022.

@author: Nikola
"""

from dataclasses import dataclass, field
from typing import Callable, Any
from functools import partial
from abc import ABC, abstractmethod
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
# TODO Make it a singleton (refactor) (maybe?)
@dataclass
class Bank:
    """A representation of the unreserved tokens in the game."""

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

    def _remove_token(self, amount_to_remove: dict[str, int],
                      threshold=0, verbose=0) -> bool:
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
            return True
        else:
            return False
# =============================================================================
#             raise TokenThresholdError("Tried to take more tokens"
#                                       "than available in the bank")
# =============================================================================

    # TODO If a maximum threshold is added, add a False scenario
    def add_token(self, amount_to_add: dict[str, int]) -> bool:
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
        return True

    def remove_3_different_color_tokens(self, color_list: list[str],
                                        verbose=0) -> bool:
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
        """
        if len(color_list) != 3:
            raise IncorrectInputError("3 colors were not given")
        if 'yellow' in color_list:
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        return self._remove_token(dict.fromkeys(color_list, 1))

    def remove_2_same_color_tokens(self, color: str, verbose=0) -> bool:
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
        return self._remove_token({color: 2}, threshold=2)


@dataclass(order=True)
class Player:
    """A representation of a player entity within the game."""

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

    def remove_token(self, amount_to_remove: dict[str, int]) -> bool:
        """Remove tokens of given colors by the amount given for each.

        Will be unsuccessful if the given amount for any given color is
        more than the amount reserved by the player (for that color).

        Parameters
        ----------
        amount_to_remove : dict[str, int]
            A dict of colors (keys) and amount of tokens to remove (values)

        Raises
        ------
        IncorrectInputError
            Raise if an invalid color was given in amount_to_remove.

        Returns
        -------
        bool
            Whether or not the tokens were removed from the player.
        """
        if not set(amount_to_remove.keys()).issubset(
                self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_remove_token(amount_to_remove):
            for color in amount_to_remove:
                self.token_reserved[color] -= amount_to_remove[color]
            return True
        else:
            return False
# =============================================================================
#             raise TokenThresholdError("Tried to take more tokens"
#                                       f"from {self.player_id} than"
#                                       "available")
# =============================================================================

    def _can_add_token(self, amount_to_add: dict[str, int]) -> bool:
        """Check if tokens of given colors can be added."""
        if (sum(self.token_reserved.values()) +
                sum(amount_to_add.values()) > 10):
            return False
        else:
            return True

    def add_token(self, amount_to_add: dict[str, int]) -> bool:
        """Add tokens of given colors by the amount given for each.

        Will be unsuccessful if sum amount of all tokens added plus the sum
        amount of all tokens reserved by the player is more than 10.

        Parameters
        ----------
        amount_to_add : dict[str, int]
            A dict of colors (keys) and amount of tokens to add (values).

        Raises
        ------
        IncorrectInputError
            Raise if an invalid color was given in amount_to_add.

        Returns
        -------
        bool
            Whether or not the tokens were added to the player.
        """
        if not set(amount_to_add.keys()).issubset(self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_add_token(amount_to_add):
            for color in amount_to_add:
                self.token_reserved[color] += amount_to_add[color]
            return True
        else:
            return False
# =============================================================================
#             raise TooManyTokensForPlayerError("A player cannot have more"
#                                               " than 10 tokens in total"
#                                               " reserved")
# =============================================================================

    def can_reserve_card(self) -> bool:
        """Check if player has less than 3 reserved cards."""
        # Should never have more than 3 reserved cards, but just in case use >=
        if len(self.cards_reserved) >= 3:
            return False
        else:
            return True
# =============================================================================
#             raise ActionNotPossibleError("Player has 3 reserved cards, "
#                                          "can't reserve more")
# =============================================================================

    def add_to_reserved_cards(self, card: Card, card_id: str) -> None:
        """Add card to dict of reserved cards."""
        # The card is reserved even if there isn't a wildcard token to reserve
        self.cards_reserved[card_id] = (card)

    def can_purchase_card(self, card: Card,
                          yellow_replaces: dict[str, int]) -> bool:
        """Check if the player can purchase the given card.

        Returns True if the sum of each color of owned bonuses,
        yellow tokens given as collateral and reserved tokens of the player
        is >= than the cost of tokens of the card for those colors.

        Parameters
        ----------
        card : Card
            The card that the player wants to purchase.
        yellow_replaces : dict[str, int]
            A dict of colors (keys) and amount of yellow tokens
            given to replace tokens for each given color (values).

        Raises
        ------
        IncorrectInputError
            Raises in two case:
                If an invalid color was given in yellow_replaces.
                if the sum of tokens (values) in yellow_replaces is more
                than the amount of tokens in token_reserved['yellow']

        Returns
        -------
        bool
            Whether or not the player can purchase the card.
        """
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

    # TODO: add an input type check, and with that change output to bool
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

    # TODO: add an input type check, and with that change output to bool
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


@dataclass
class Action(ABC):
    """Abstract class for representation of an action performed by a player."""

    params: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Abstract method for checking if the action can be performed."""
        pass

    @abstractmethod
    def perform(self, player: Player, bank: Bank) -> bool:
        """Abstract method for performing the action in the game."""
        pass

    @abstractmethod
    def print_string(self) -> str:
        """Abstract method for giving a print value in string form."""
        pass


@dataclass
class Reserve3DifferentColorTokens(Action):
    """Reserve 1 token of 3 different colors for the player.

    On initialization provide a dict with a key 'color_list'
    that contains a list of 3 colors

    Parameters
    ----------
    color_list : list[str]
        A list of 3 colors that represent 1 token each.
    """

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the requested tokens can be reserved.

        The action will be successful if :
            - The given bank holds the requested amount of tokens
            - The player won't have more than 10 tokens in total at
              the end of the action.

        The color list is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will receive the requested tokens.
        bank : Bank
            The bank that will give the requested tokens.

        Returns
        -------
        bool
            Whether or not the action will be successful.
        """
        color_list = self.params['color_list']
        if (bank._can_remove_token(dict.fromkeys(color_list, 1)) and
                player._can_add_token(dict.fromkeys(color_list, 1))):
            return True
        else:
            return False

    def perform(self, player: Player, bank: Bank, verbose=0) -> None:
        """Transfer the requested tokens from the bank to the player.

        The color list is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will receive the requested tokens.
        bank : Bank
            The bank that will give the requested tokens.
        """
        color_list = self.params['color_list']
        bank.remove_3_different_color_tokens(color_list)
        player.add_token(dict.fromkeys(color_list, 1))
        if verbose == 1:
            print(f"{player.player_id} has reserved a {color_list[0]}, "
                  f"{color_list[1]} and {color_list[2]} token")
        pass

    def print_string(self) -> str:
        """Give a string to print representing the action."""
        color_list = self.params['color_list']
        return (f"reserve a {color_list[0]}, {color_list[1]} and "
                f"{color_list[2]} token")


@dataclass
class Reserve2SameColorTokens(Action):
    """Reserve 2 token of the color for the player.

    On initialization provide a dict with a key 'color'
    that contains a color

    Parameters
    ----------
    color : str
        The color of the requested tokens.
    """

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the requested tokens can be reserved.

        The action will be successful if :
            - The given bank holds the requested amount of tokens
            - The player won't have more than 10 tokens in total at
              the end of the action.

        The color is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will receive the requested tokens.
        bank : Bank
            The bank that will give the requested tokens.

        Returns
        -------
        bool
            Whether or not the action will be successful.
        """
        color = self.params['color']
        if (bank._can_remove_token({color: 2}, threshold=2) and
                player._can_add_token({color: 2})):
            return True
        else:
            return False

    def perform(self, player: Player, bank: Bank, verbose=0) -> None:
        """Transfer the requested tokens from the bank to the player.

        The color is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will receive the requested tokens.
        bank : Bank
            The bank that will give the requested tokens.
        """
        color = self.params['color']
        bank.remove_2_same_color_tokens(color)
        player.add_token({color: 2})
        if verbose == 1:
            print(f"{player.player_id} has reserved 2 {color} tokens")
        pass

    def print_string(self) -> str:
        """Give a string to print representing the action."""
        return (f"reserve 2 {self.params['color']} tokens.")


@dataclass
class ReserveCard(Action):
    """Reserve the given card for the player.

    On initialization provide a dict with:
        - a key 'card' that contains the card.
        - a key 'card_id' that contains the card_id.

    Parameters
    ----------
    card : Card
        The card that will be reserved by the player.
    card_id : str
        The id by which the card is referenced.
    """

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the player can reserve the card.

        The action will be successful if :
            - the player has less than 3 reserved cards.

        Parameters
        ----------
        player : Player
            The player that will reserve the requested card.

        Returns
        -------
        bool
            Whether or not the action will be successful.
        """
        if player.can_reserve_card():
            return True
        else:
            return False

    def perform(self, player: Player, bank: Bank, verbose=0) -> None:
        """Give the card to the player as a reserved card.

        Additionally, if it is possible transfer one yellow (wildcard)
        token from the bank to the player.

        The card is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will receive the requested tokens.
        bank : Bank
            The bank that will give the requested tokens.
        """
        card = self.params['card']
        card_id = self.params['card_id']
        # Add the card to the dict of reserved cards of the player
        player.add_to_reserved_cards(card, card_id)
        if verbose == 1:
            print(f"{player.player_id} has reserved {card_id}")
        # Give the player a wildcard token
        # if the transfer is possible
        if (bank._can_remove_token({'yellow': 1}) and
                player._can_add_token({'yellow': 1})):
            bank._remove_token({'yellow': 1})
            player.add_token({'yellow': 1})
            if verbose == 1:
                print("A wildcard token has been given to "
                      f"{player.player_id}")
        pass

    def print_string(self) -> str:
        """Give a string to print representing the action."""
        return f"reserve {self.params['card_id']}"


@dataclass
class PurchaseCard(Action):
    """Purchase the given card for the player.

    On initialization provide a dict with:
        - a key 'card' that contains the card.
        - a key 'card_id' that contains the card_id.
        - a key 'is_reserved' that contains a is_reserved flag
          for the card.
        - a key 'yellow_replaces' that contains a dict of
          colors (as keys) and amounts (as values).

    Parameters
    ----------
    card : Card
        The card that will be purchased by the player.
    card_id : str
        The id by which the card is referenced.
    is_reserved : bool, optional
        A flag for whether the card is already reserved by the player.
    yellow_replaces : dict[str, int], optional
        A dict of colors (keys) and amount of yellow tokens
        given to replace tokens for each given color (values).
    """

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the player can purchase the card.

        The action will be successful if :
            - if the sum of each color of owned bonuses,
              yellow tokens given as collateral and
              reserved tokens of the player
              is >= than the cost of tokens of the card for those colors.

        The card is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will purchase the requested card.

        Returns
        -------
        bool
            Whether or not the action will be successful.
        """
        card = self.params['card']
        yellow_replaces = self.params['yellow_replaces']
        if player.can_purchase_card(card, yellow_replaces):
            return True
        else:
            return False

    def _give_card(self, player: Player, remaning_cost: int) -> bool:
        """Give the card to the player if there is no remaining cost."""
        card = self.params['card']
        card_id = self.params['card_id']
        is_reserved = self.params['is_reserved']

        if remaning_cost == 0:
            # If the card is reserved, remove from there
            if is_reserved:
                player.cards_reserved.pop(card_id)
            player.add_to_owned_cards(card)
            return True
        else:
            return False

    def perform(self, player: Player, bank: Bank, verbose=0) -> None:
        """Purchase the card for the player.

        The process of purchasing a card follows this process:
            - First, the owned bonuses discount the price of the card
              (for each color) (if the player has enough bonuses
              the card can be purchased without spending any tokens)
            - Second, the given wildcard (yellow) tokens as collateral
              for each color reduce the price of the card
              (the card can be purchased with just wildcard tokens)
            - Finally the card will be purchased with the reserved tokens
              for each color (the amount is the remaining cost for each color).

        All tokens that the player offers will be added to the given bank.
        After the purchase is complete, give the card to the player
        as an owned card.

        The card is given on initialization of the Action.

        Parameters
        ----------
        player : Player
            The player that will give the requested tokens
            for the cost of the card.
        bank : Bank
            The bank that will receive the requested tokens
            for the cost of the card.

        Raises
        ------
        ActionNotPossibleError
            Precautionary error (should never be raised) if the card
            has remaining cost but wasn't purchased.
        """
        card = self.params['card']
        card_id = self.params['card_id']
        is_reserved = self.params['is_reserved']
        yellow_replaces = self.params['yellow_replaces']
        card_token_cost = deepcopy(card.token_cost)

        # Reduce the cost by the owned bonuses
        for color in player.bonus_owned:
            if player.bonus_owned[color] > card_token_cost[color]:
                card_token_cost[color] = 0
            else:
                card_token_cost[color] -= player.bonus_owned[color]
        # If the card was purchased with just bonuses
        if self._give_card(player=player,
                           remaning_cost=sum(card_token_cost.values())):
            if verbose == 1:
                print(f"{player.player_id} purchased {card_id} with bonuses")
            return None

        # Reduce the cost by the yellow tokens per color
        for color in yellow_replaces:
            if card_token_cost[color] - yellow_replaces[color] >= 0:
                card_token_cost[color] -= yellow_replaces[color]
            else:
                # TODO Issue 11
                raise IncorrectInputError("Too many yellow tokens given "
                                          f"for color {color}")
        # Give all the yellow tokens back to the bank
        player.remove_token({'yellow': sum(yellow_replaces.values())})
        bank.add_token({'yellow': sum(yellow_replaces.values())})

        # If the card was purchased by just yellow tokens
        if self._give_card(player=player,
                           remaning_cost=sum(card_token_cost.values())):
            if verbose == 1:
                print(f"{player.player_id} purchased {card_id} with "
                      "wildcard tokens")
            return None

        # Finish the purchase with the reserved tokens
        for color in card.token_cost:
            if card_token_cost[color] > 0:
                # Transfer the amount of tokens remaining in the cost
                # from the player to the bank
                player.remove_token({color: card_token_cost[color]})
                bank.add_token({color: card_token_cost[color]})
                card_token_cost[color] = 0

        # If the card was purchased by reserved tokens
        if self._give_card(player=player,
                           remaning_cost=sum(card_token_cost.values())):
            if verbose == 1:
                print(f"{player.player_id} has purchased {card_id}"
                      " with reserved tokens")
            return None
        # Something went horribly wrong if you get here
        raise ActionNotPossibleError("The card still has a cost to it, "
                                     "something went horribly wrong")

    def print_string(self) -> str:
        """Give a string to print representing the action."""
        return f"purchase {self.params['card_id']}"


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
# TODO add a game_started and game_finished flags and not allow actions
# game_started = False or game_finished = True
@dataclass
class Game:
    """A representation of the whole process of playing the game."""

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
        """Generate and shuffle and pick the nobles for the game."""
        nobles_list = generate_nobles()
        shuffle(nobles_list)
        # Get n + 1 nobles for n players
        for index, noble in enumerate(nobles_list[0:self._num_players + 1]):
            self.nobles[f'noble_{index}'] = noble
        if verbose == 1:
            print(f"{len(self.nobles)} nobles added for "
                  f"{self._num_players} players")

    def _generate_shuffle_cards(self, verbose=0) -> None:
        """Generate and shuffle the cards for the game."""
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

    def initialize_new_game(self, num_players=4, verbose=0) -> None:
        """Initialize a new game for predetermined number of players."""
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
        """End the player's move and do a noble check for them.

        Assume player has completed an action this turn.
        *Should only be called in succefully performed action methods
        in Game.
        """
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

    # %% Action-related methods
    def _find_card_on_table_by_id(self, card_id: str) -> Card:
        """Find card by id by searching all the cards on table."""
        if card_id in self.cards_on_table_level_1:
            card = self.cards_on_table_level_1[card_id]
        elif card_id in self.cards_on_table_level_2:
            card = self.cards_on_table_level_2[card_id]
        elif card_id in self.cards_on_table_level_3:
            card = self.cards_on_table_level_3[card_id]
        return card

    def _remove_card_on_table_by_id(self, card_id: str) -> bool:
        """Find card by id, remove from table and add new card from deck."""
        # Find the card level and get the deck and the cards on table
        if card_id in self.cards_on_table_level_1:
            cards_on_table = self.cards_on_table_level_1
            cards_deck = self.cards_deck_level_1
        elif card_id in self.cards_on_table_level_2:
            cards_on_table = self.cards_on_table_level_2
            cards_deck = self.cards_deck_level_2
        elif card_id in self.cards_on_table_level_3:
            cards_on_table = self.cards_on_table_level_3
            cards_deck = self.cards_deck_level_3
        # Remove card from table
        cards_on_table.pop(card_id)
        # Add the next card from the deck (if there is one)
        if len(cards_on_table) > 0:
            new_card_id = f'card_{len(cards_deck)}'
            cards_on_table[new_card_id] = cards_deck.pop()
        return True

    def perform_action_for_current_player(self, action: Action,
                                          verbose=0) -> bool:
        """Perform the given action for the current player to move.

        Parameters
        ----------
        action : Action
            The action to be performed with the initialized parameters.

        verbose : int
            If 1, will print output of the entire process,
            If 0, will print nothing.

        Returns
        -------
        bool
            Whether or not the action was performed succesfully
        """
        curr_player = self.current_player_to_move()
        if verbose == 1:
            print(f"Attemping to {action.print_string()} for "
                  f"{curr_player.player_id}")
        # If it's a card-related action, find the card by id
        # and set it as a parameter to the action
        if 'card_id' in action.params:
            card_id = action.params['card_id']
            if 'is_reserved' in action.params:
                is_reserved = action.params['is_reserved']
            else:
                is_reserved = False
            if is_reserved:
                card = curr_player.cards_reserved[card_id]
            else:
                card = self._find_card_on_table_by_id(card_id)

            action.params['card'] = card

        if action.can_perform(curr_player,
                              self.bank):
            action.perform(curr_player, self.bank, verbose)
            # If it's a card-related action, find the card by id
            # and remove it from the table (if it isn't reserved)
            if 'card_id' in action.params:
                if not is_reserved:
                    self._remove_card_on_table_by_id(card_id)
            # Action was completed, so end the player's move
            self.end_move_for_player(verbose)
            return True
        else:
            if verbose == 1:
                print("This action could not be performed")
            return False

    # %% Possible & Legal Actions
    def _all_possible_reserve_3_different_color_tokens(self) -> list[Action]:
        """Return all possible actions of this type."""
        current_actions_list = []
        # TODO Change to enum when refactoring
        colors = ["green", "white", "blue", "black", "red"]
        # All combinations of 3 different tokens
        for colors_combo_3 in combinations(colors, 3):
            current_actions_list.append(
                Reserve3DifferentColorTokens(params={'color_list':
                                                     list(colors_combo_3)}))
        return current_actions_list

    def _all_possible_reserve_2_same_color_tokens(self) -> list[Action]:
        """Return all possible actions of type Reserve2SameColorTokens."""
        current_actions_list = []
        # TODO Change to enum when refactoring
        colors = ["green", "white", "blue", "black", "red"]
        # All colors for 2 tokens
        current_actions_list = []
        for color in colors:
            current_actions_list.append(
                Reserve2SameColorTokens(params={'color': color}))
        return current_actions_list

    def _all_possible_reserve_card(self) -> list[Action]:
        """Return all possible actions of type ReserveCard."""
        # Reserving any card slot on table
        current_actions_list = []
        # TODO With fix with creating Table class, get card by
        # table index (ex level=1, card=4), not by generating card_id
# =============================================================================
#         for level in range(1, 4):
#             for index in range(4):
#                 current_actions_list.append(
#                     ReserveCard(params={'level': level, 'index': index}))
# =============================================================================
        for card_id in self.cards_on_table_level_1:
            current_actions_list.append(
                ReserveCard(params={'card_id': card_id}))
        for card_id in self.cards_on_table_level_2:
            current_actions_list.append(
                ReserveCard(params={'card_id': card_id}))
        for card_id in self.cards_on_table_level_3:
            current_actions_list.append(
                ReserveCard(params={'card_id': card_id}))
        return current_actions_list

    def _all_possible_purchase_card(self) -> list[Action]:
        """Return all possible actions of type PurchaseCard."""
        # Purchasing any slot on table with all combinations
        # of wildcard token
        current_actions_list = []
        # TODO Change to enum when refactoring
        colors = ["green", "white", "blue", "black", "red"]
        # TODO With fix with creating Table class, get card by
        # table index (ex level=1, card=4), not by generating card_id
# =============================================================================
#         for token_input in product(range(6), range(6), range(6),
#                                    range(6), range(6)):
#             if sum(token_input) <= 5:
#                 for level in range(1, 4):
#                     for index in range(4):
#                         current_actions_list.append(
#                             (purchase_a_card,
#                              {'level': level,
#                               'index': index,
#                               'yellow_replaces': {colors[0]: token_input[0],
#                                                   colors[1]: token_input[1],
#                                                   colors[2]: token_input[2],
#                                                   colors[3]: token_input[3],
#                                                   colors[4]: token_input[4]}}))
# =============================================================================
        curr_player = self.current_player_to_move()
        for token_input in product(range(6), range(6), range(6),
                                   range(6), range(6)):
            if sum(token_input) <= 5:
                yellow_replaces = {colors[0]: token_input[0],
                                   colors[1]: token_input[1],
                                   colors[2]: token_input[2],
                                   colors[3]: token_input[3],
                                   colors[4]: token_input[4]}
                for card_id in curr_player.cards_reserved:
                    card = curr_player.cards_reserved[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': True,
                                    'yellow_replaces': yellow_replaces}))
                for card_id in self.cards_on_table_level_1:
                    card = self.cards_on_table_level_1[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': False,
                                    'yellow_replaces': yellow_replaces}))
                for card_id in self.cards_on_table_level_2:
                    card = self.cards_on_table_level_2[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': False,
                                    'yellow_replaces': yellow_replaces}))
                for card_id in self.cards_on_table_level_3:
                    card = self.cards_on_table_level_3[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': False,
                                    'yellow_replaces': yellow_replaces}))
        return current_actions_list

    def all_possible_actions(self) -> list[Action]:
        """Return all possible actions."""
        all_actions = {}
        # Reserve3DifferentColorTokens
        actions_list = self._all_possible_reserve_3_different_color_tokens()
        all_actions['reserve_3_different_color_tokens'] = actions_list
        # Reserve2SameColorTokens
        actions_list = self._all_possible_reserve_2_same_color_tokens()
        all_actions['reserve_2_same_color_tokens'] = actions_list
        # ReserveCard
        actions_list = self._all_possible_reserve_card()
        all_actions['reserve_card'] = actions_list
        # PurchaseCard
        actions_list = self._all_possible_purchase_card()
        all_actions['purchase_card'] = actions_list
        return all_actions

    def all_legal_actions_of_list(self,
                                  action_list: list[Action]) -> list[Action]:
        """Return all legal actions from given list of actions.

        These are calculated for the current player to move.
        Usually the list should be of one action type.
        """
        legal_action_list = []
        player = self.current_player_to_move()
        bank = self.bank
        for action in action_list:
            try:
                if action.can_perform(player, bank):
                    legal_action_list.append(action)
            except IncorrectInputError as e:
                continue
        return legal_action_list

    def all_legal_actions(self) -> list[Action]:
        """Return all legal actions from all possible actions.

        These are calculated for the current player to move.
        """
        all_legal_actions = {}
        all_actions = self.all_possible_actions()
        for action_type in all_actions:
            all_legal_actions[action_type] = self.all_legal_actions_of_list(
                all_actions[action_type])
        return all_legal_actions
    # %% Game state representation
    #            -> numpy.matrix():

    def state(self, dense=0, verbose=0):
        """Return the state of the game."""
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
                    print(f'{card.token_cost[color]:<5}', end='\t')
                print('\n')
            for card_id in self.cards_on_table_level_2:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_2[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}', end='\t')
                print('\n')
            for card_id in self.cards_on_table_level_3:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_3[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}', end='\t')
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
game.perform_action_for_current_player(
    Reserve3DifferentColorTokens(params={'color_list': ['green',
                                                        'white',
                                                        'black']}),
    verbose=verbose)

# %%%
#game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve2SameColorTokens(params={'color': 'red'}),
    verbose=verbose)
# %%%
#game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    ReserveCard(params={'card_id': 'card_39'}),
    verbose=verbose)
# %%%
winner = end_game_turn(game, 1)
print(f"The winner is {winner}")

# %%%
#game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve3DifferentColorTokens(params={'color_list': ['green',
                                                        'white',
                                                        'black']}),
    verbose=verbose)
# %%%
#game.current_player_to_move(verbose)
game.perform_action_for_current_player(
    Reserve3DifferentColorTokens(params={'color_list': ['green',
                                                        'white',
                                                        'black']}),
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
#game.state(verbose=1)
# %%%
all_actions = game.all_possible_actions()
#print(all_actions)
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