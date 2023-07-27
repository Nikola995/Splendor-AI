from dataclasses import dataclass, field
from typing import Any, Tuple, List, Dict
from abc import ABC, abstractmethod
from players import Player
from banks import Bank
from tokens import Token
from cards import Card
from copy import deepcopy
from utils import ActionNotPossibleError, IncorrectInputError


@dataclass
class Action(ABC):
    """Abstract class for representation of an action performed by a player."""

    @abstractmethod
    def can_perform(self, player: Player, **kwargs) -> bool:
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
        return ("reserved 3 tokens of unique colors.")


@dataclass
class Reserve2SameColorTokens(Action):
    """Reserve 2 token of the same color for the player.

    Parameters
    ----------
    player : Player
        The player that will receive the requested tokens.
    bank : Bank
        The bank that will give the requested tokens.
    color : Token
        Color for the 2 tokens
    """

    def can_perform(self, player: Player, bank: Bank, color: Token) -> bool:
        """Check if the requested tokens can be reserved.

        The action will be successful if all of the following is true:
            - The bank holds the requested amount of tokens before
            the action is performed.
            - The player won't have more than 10 tokens in total after
            the action is performed.
        """
        return (bank.can_remove_token({color: 2})
                and player.can_add_token({color: 2}))

    def perform(self, player: Player, bank: Bank, color: Token) -> None:
        """Transfer the requested tokens from the bank to the player.
        """
        bank.remove_2_same_color_tokens(color)
        player.add_token({color: 2})

    def __str__(self) -> str:
        return ("reserved 2 tokens of the same color.")


# TODO: Change the interactions with Cards (remove card_id)
@dataclass
class ReserveCard(Action):
    """Reserve the given card for the player.

    Additionally, if it is possible transfer 1 wildcard token
    from the bank to the player.

    Parameters
    ----------
    player : Player
        The player that will receive the requested card & wildcard token.
    bank : Bank
        The bank that will give the requested wildcard token.
    card : Card
        The card that will be reserved by the player.
    card_id: str
        The id by which the Card is stored in the player's inventory.
    """

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the player can reserve the card.

        The action will be successful if :
            - the player has less than 3 reserved cards.
        """
        return player.can_reserve_card()

    def perform(self, player: Player, bank: Bank,
                card: Card, card_id: str) -> None:
        """Add the card to the player's reserved cards.
        """
        player.add_to_reserved_cards(card, card_id)
        # Give the player 1 wildcard token, if the transfer is possible
        if (bank.can_remove_token({Token.YELLOW}) and
                player.can_add_token({Token.YELLOW})):
            bank.remove_wildcard_token()
            player.add_token({Token.YELLOW})

    def __str__(self) -> str:
        return "reserved a card."


# TODO: Change the interactions with Cards (remove card_id)
@dataclass
class PurchaseCard(Action):
    """Purchase the given card for the player.

    Parameters
    ----------
    player : Player
        The player that will receive the requested card & wildcard token.
    bank : Bank
        The bank that will give the requested wildcard token.
    card : Card
        The card that will be reserved by the player.
    card_id: str
        The id by which the Card is stored in the player's inventory.
    wildcard_collaterals: Dict[Token, int]
        The number of Tokens that are replaced by wildcard tokens in the
        player's reserved_tokens
    """

    def can_perform(self, player: Player, card: Card) -> bool:
        """Check if the player can purchase the given card.

        Returns True if the sum of each color of owned bonuses,
        reserved tokens of the player and wildcard tokens given as collateral
        is >= than the cost of tokens of the card for those colors.
        """
        return player.can_purchase_card(card)

    def _give_card(self, player: Player, card: Card, card_id: str) -> None:
        """Give the card to the player."""
        # If the card is reserved, remove from there
        if card_id in player.cards_reserved:
            player.cards_reserved.pop(card_id)
        player.add_to_owned_cards(card)

    def perform(self, player: Player, bank: Bank,
                card: Card, card_id: str,
                wildcard_collaterals: Dict[Token, int]) -> None:
        """Purchase the card for the player.

        The process of purchasing a card follows this process:
            1. The owned bonuses discount the price of the card
            (for the corresponding color)
            (the card can be purchased with just bonuses)
            2. The collateral wildcard tokens discount the price of the card
            (for the corresponding color) & removed from the player's inventory
            (the card can be purchased with just wildcard tokens)
            3. The reserved tokens are removed from the player's inventory
            by the remaining amount of the card cost
            (for the corresponding color)
        """
        remaining_cost = deepcopy(card.token_cost)
        # 1. Reduce the cost by the owned bonuses
        for color in remaining_cost:
            remaining_cost[color] = max((remaining_cost[color] -
                                         player.bonus_owned[color]), 0)
        # Transfer the card if the total remaining cost == 0
        if sum(remaining_cost.values()) == 0:
            self._give_card(player, card, card_id)
            return None
        # 2. Reduce the cost by collateral wildcard tokens
        for color in remaining_cost:
            remaining_cost[color] = max((remaining_cost[color] -
                                         wildcard_collaterals[color]), 0)
        # Transfer the collateral wildcard tokens from the player to the bank
        player.remove_token({Token.YELLOW: sum(wildcard_collaterals.values())})
        bank.add_token({Token.YELLOW: sum(wildcard_collaterals.values())})
        # Transfer the card if the total remaining cost == 0
        if sum(remaining_cost.values()) == 0:
            self._give_card(player, card, card_id)
            return None
        # 3. Purchase the remaining cost with the player's reserved tokens
        player.remove_token(remaining_cost)
        bank.add_token(remaining_cost)
        self._give_card(player, card, card_id)

    def __str__(self) -> str:
        return "purchased a card."
