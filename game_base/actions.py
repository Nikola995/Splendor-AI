from dataclasses import dataclass, field
from typing import Any, Tuple, List
from abc import ABC, abstractmethod
from players import Player
from banks import Bank
from tokens import Token
from copy import deepcopy
from utils import ActionNotPossibleError, IncorrectInputError


@dataclass
class Action(ABC):
    """Abstract class for representation of an action performed by a player."""

    @abstractmethod
    def can_perform(self, player: Player, bank: Bank, **kwargs) -> bool:
        """Abstract method for checking if the action can be performed."""
        pass

    @abstractmethod
    def perform(self, player: Player, bank: Bank, **kwargs) -> bool:
        """Abstract method for performing the action in the game."""
        pass


@dataclass
class Reserve3UniqueColorTokens(Action):
    """Reserve 1 token of 3 unique colors for the player.

    Parameters
    ----------
    player : Player
        The player that will receive the requested tokens.
    bank : Bank
        The bank that will give the requested tokens.
    colors: Tuple[Token, Token, Token]
        Tuple containing 3 unique token colors
    """

    def can_perform(self, player: Player, bank: Bank,
                    colors: Tuple[Token, Token, Token]) -> bool:
        """Check if the requested tokens can be reserved.

        The action will be successful if all of the following is true:
            - The bank holds the requested amount of tokens before
            the action is performed.
            - The player won't have more than 10 tokens in total after
            the action is performed.
        """
        return (bank.can_remove_token(dict.fromkeys(colors, 1))
                and player.can_add_token(dict.fromkeys(colors, 1)))

    def perform(self, player: Player, bank: Bank,
                colors: Tuple[Token, Token, Token]) -> None:
        """Transfer the requested tokens from the bank to the player.
        """
        bank.remove_3_unique_color_tokens(colors)
        player.add_token(dict.fromkeys(colors, 1))

    def __str__(self) -> str:
        return (f"reserved 3 tokens of unique colors.")


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

    def __str__(self) -> str:
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

    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return f"purchase {self.params['card_id']}"
