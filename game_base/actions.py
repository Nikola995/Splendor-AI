from dataclasses import dataclass
from abc import ABC, abstractmethod
from players import Player
from banks import Bank
from game_base.tokens import Token
from cards import Card
from copy import deepcopy


@dataclass
class Action(ABC):
    """Abstract class for representation of an interaction by a player
    with game assets."""

    @abstractmethod
    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Abstract method for checking if the action can be performed."""
        pass

    @abstractmethod
    def perform(self, player: Player, bank: Bank, **kwargs) -> bool:
        """Abstract method for performing the action in the game."""
        # If ultimate perfomance is needed, this can be refactored to not use
        # **kwargs
        pass


@dataclass(slots=True)
class Reserve3UniqueColorTokens(Action):
    """Reserve 1 token of 3 unique colors for the player.

    Parameters
    ----------
    player : Player
        The player that will receive the requested tokens.
    bank : Bank
        The bank that will give the requested tokens.
    colors: tuple[Token, Token, Token]
        Tuple containing 3 unique token colors
    """
    colors: tuple[Token, Token, Token]

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the requested tokens can be reserved.

        The action will be successful if all of the following is true:
            - The bank holds the requested amount of tokens before
            the action is performed.
            - The player won't have more than 10 tokens in total after
            the action is performed.
        """
        return (bank.can_remove_token(dict.fromkeys(self.colors, 1))
                and player.can_add_token(dict.fromkeys(self.colors, 1)))

    def perform(self, player: Player, bank: Bank, **kwargs) -> None:
        """Transfer the requested tokens from the bank to the player.
        (Ignore **kwargs)"""
        bank.remove_3_unique_color_tokens(self.colors)
        player.add_token(dict.fromkeys(self.colors, 1))

    def __str__(self) -> str:
        return (f"reserved 1 {self.colors[0]}, {self.colors[1]} and "
                f"{self.colors[2]} tokens.")


@dataclass(slots=True)
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
    color: Token

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the requested tokens can be reserved.

        The action will be successful if all of the following is true:
            - The bank holds the requested amount of tokens before
            the action is performed.
            - The player won't have more than 10 tokens in total after
            the action is performed.
        """
        return (bank.can_remove_token({self.color: 2})
                and player.can_add_token({self.color: 2}))

    def perform(self, player: Player, bank: Bank, **kwargs) -> None:
        """Transfer the requested tokens from the bank to the player.
        (Ignore **kwargs)"""
        bank.remove_2_same_color_tokens(self.color)
        player.add_token({self.color: 2})

    def __str__(self) -> str:
        return (f"reserved 2 {self.color} tokens.")


@dataclass(slots=True)
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
    """
    card: Card

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the player can reserve the card.
        (bank is unused, but added to comply with generic Action.)

        The action will be successful if :
            - the player has less than 3 reserved cards.
        """
        return player.can_reserve_card()

    def perform(self, player: Player, bank: Bank, **kwargs) -> None:
        """Add the card to the player's reserved cards.
        (Ignore **kwargs)"""
        player.add_to_reserved_cards(self.card)
        # Give the player 1 wildcard token, if the transfer is possible
        single_wildcard = {Token.YELLOW: 1}
        if (bank.can_remove_token(single_wildcard) and
                player.can_add_token(single_wildcard)):
            bank.remove_wildcard_token()
            player.add_token(single_wildcard)

    def __str__(self) -> str:
        return f"reserved card {self.card.id}."


@dataclass(slots=True)
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
    wildcard_collaterals: dict[Token, int]
        The number of Tokens that are replaced by wildcard tokens in the
        player's reserved_tokens
    """
    card: Card

    def can_perform(self, player: Player, bank: Bank) -> bool:
        """Check if the player can purchase the given card.
        (bank is unused, but added to comply with generic Action.)

        Returns True if the sum of each color of owned bonuses,
        reserved tokens of the player and wildcard tokens given as collateral
        is >= than the cost of tokens of the card for those colors.
        """
        return player.can_purchase_card(self.card)

    def _give_card(self, player: Player) -> None:
        """Give the card to the player."""
        # If the card is reserved, remove from there
        if self.card in player.cards_reserved:
            player.cards_reserved.pop(self.card)
        player.add_to_owned_cards(self.card)

    def perform(self, player: Player, bank: Bank,
                wildcard_collaterals: dict[Token, int], **kwargs) -> None:
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

        (Ignore **kwargs, wildcard_collaterals is given explicitly)
        """
        remaining_cost = deepcopy(self.card.token_cost)
        # 1. Reduce the cost by the owned bonuses
        for color in remaining_cost:
            remaining_cost[color] = max((remaining_cost[color] -
                                         player.bonus_owned[color]), 0)
        # Transfer the card if the total remaining cost == 0
        if sum(remaining_cost.values()) == 0:
            self._give_card(player)
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
            self._give_card(player)
            return None
        # 3. Purchase the remaining cost with the player's reserved tokens
        player.remove_token(remaining_cost)
        bank.add_token(remaining_cost)
        self._give_card(player)

    def __str__(self) -> str:
        return f"purchased card {self.card.id}."
