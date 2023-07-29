from dataclasses import dataclass
from abc import ABC, abstractmethod
from itertools import combinations
from actions import (Action, ReserveCard, PurchaseCard,
                     Reserve2SameColorTokens,
                     Reserve3UniqueColorTokens)
from players import Player
from banks import Bank
from cards import Card
from game_base.tokens import Token


@dataclass
class ActionSet(ABC):
    """Abstract class for working with game actions"""
    actions: list[Action]

    @abstractmethod
    def possible_actions(self, player: Player, **kwargs) -> list[Action]:
        """Abstract method for checking all possible actions for a player."""
        pass

    @abstractmethod
    def legal_actions(self, player: Player, **kwargs) -> list[Action]:
        """Abstract method for checking all legal actions for a player."""
        pass


def generate_3_unique_token_actions() -> list[Action]:
    """Creates a list of all possible 3 unique color token actions."""
    color_combos = combinations([Token.GREEN, Token.WHITE, Token.BLUE,
                                 Token.BLACK, Token.RED], 3)
    return [Reserve3UniqueColorTokens(combo) for combo in color_combos]


def generate_2_same_token_actions() -> list[Action]:
    """Creates a list of all possible 2 same color token actions."""
    normal_colors = [x for x in Token if x != Token.YELLOW]
    return [Reserve2SameColorTokens(color) for color in normal_colors]


def generate_standard_token_actions() -> list[Action]:
    """Creates a list of all possible token actions."""
    return generate_3_unique_token_actions() + generate_2_same_token_actions()


STANDARD_TOKEN_ACTIONS = generate_standard_token_actions()


@dataclass(slots=True)
class StandardActionSet(ActionSet):
    """All standard game actions."""
    # List of possible actions with tokens (immutable during entire game)
    token_actions: list[Action] = STANDARD_TOKEN_ACTIONS

    def possible_card_actions(self, player: Player,
                              cards: list[Card]) -> list[Action]:
        """Creates a list of actions for all available cards."""
        reserve_cards = [ReserveCard(card) for card in cards]
        # Add all of the cards on the tables.
        purchase_cards = [PurchaseCard(card) for card in cards]
        # Add the already reserved cards in the player's inventory
        purchase_cards += [PurchaseCard(card) for
                           card in player.cards_reserved]
        return reserve_cards + purchase_cards

    def possible_actions(self, player: Player,
                         cards: list[Card]) -> list[Action]:
        """Returns all possible actions for the given player."""
        return self.token_actions + self.possible_card_actions(player, cards)

    def legal_actions(self, player: Player, bank: Bank,
                      cards: list[Card]) -> list[Action]:
        """Returns all legal actions for the given player."""
        return [action for action in self.possible_actions(player, cards)
                if action.can_perform(player=player, bank=bank)]
