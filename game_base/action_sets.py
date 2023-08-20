from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from itertools import combinations
from game_base.actions import (Action, ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from game_base.players import Player
from game_base.cards import Card
from game_base.tokens import Token


@dataclass
class ActionSet(ABC):
    """Abstract class for working with game actions"""

    @abstractmethod
    def update_card_actions(self, cards: list[Card], player: Player) -> None:
        """Abstract method for updating the possible card actions."""
        pass

    @abstractmethod
    def all_actions(self) -> list[Action]:
        """Abstract method for getting all possible actions."""
        pass

    @abstractmethod
    def get_action_by_idx(self, idx: int) -> list[Action]:
        """Abstract method for getting action from all possible actions
        by idx."""
        pass


def generate_3_unique_token_actions() -> list[Action]:
    """Creates a list of all possible 3 unique color token actions."""
    normal_colors = [x for x in Token if x != Token.YELLOW]
    color_combos = combinations(normal_colors, 3)
    return [Reserve3UniqueColorTokens(combo) for combo in color_combos]


def generate_2_same_token_actions() -> list[Action]:
    """Creates a list of all possible 2 same color token actions."""
    normal_colors = [x for x in Token if x != Token.YELLOW]
    return [Reserve2SameColorTokens(color) for color in normal_colors]


def generate_standard_token_actions() -> list[Action]:
    """Creates a list of all possible token actions."""
    return generate_3_unique_token_actions() + generate_2_same_token_actions()


@dataclass(slots=True)
class StandardActionSet(ActionSet):
    """All standard game actions."""
    # List of possible actions with tokens (immutable during entire game)
    token_actions: list[Action] = field(
        default_factory=generate_standard_token_actions)
    card_actions: list[Action] = field(default_factory=list)
    card_actions_player: list[Action] = field(default_factory=list)

    def update_card_actions_table(self, cards: list[Card]) -> None:
        """Updates the list of card actions with the given cards."""
        reserve_cards = [ReserveCard(card) for card in cards]
        purchase_cards = [PurchaseCard(card) for card in cards]
        self.card_actions = reserve_cards + purchase_cards

    def update_card_actions_player(self, player: Player) -> None:
        """Updates the list of card actions for the player's reserved cards."""
        # Add the reserved card slots from the player's inventory
        self.card_actions_player = [PurchaseCard(card) for
                                    card in player.cards_reserved]

    def update_card_actions(self, cards: list[Card], player: Player) -> None:
        """Updates the list of card actions."""
        self.update_card_actions_table(cards)
        self.update_card_actions_player(player)

    def get_action_by_idx(self, idx: int) -> Action:
        """Gets the action from the list of actions by its index."""
        if idx < len(self.token_actions):
            # If the action idx is in token_actions
            return self.token_actions[idx]
        elif idx < len(self.token_actions) + len(self.card_actions):
            # If the action idx is in card_actions
            return self.card_actions[idx - len(self.token_actions)]
        elif idx < (len(self.token_actions) +
                    len(self.card_actions) +
                    len(self.card_actions_player)):
            # If the action idx is in card_actions_player
            return self.card_actions_player[idx - (len(self.token_actions) +
                                                   len(self.card_actions))]
        else:
            return None

    def all_actions(self) -> list[Action]:
        """Returns all possible actions in the current action set."""
        return (self.token_actions +
                self.card_actions +
                self.card_actions_player)
