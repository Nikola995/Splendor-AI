from dataclasses import dataclass, field
from typing import Tuple
from abc import ABC, abstractmethod
from itertools import combinations, product
from actions import (Action, Reserve2SameColorTokens,
                     Reserve3UniqueColorTokens, ReserveCard,
                     PurchaseCard)
from players import Player
from .tokens import Token


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


# %% Possible & Legal Actions
# TODO: Move all of this inside the StandardActionSet
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


@dataclass(slots=True)
class StandardActionSet(ActionSet):
    """All standard game actions."""
    actions: list[Action] = field(default_factory=lambda:
                                  ([Reserve2SameColorTokens, PurchaseCard,
                                    ReserveCard, Reserve3UniqueColorTokens]))
    unique_3_token_combos: list(Tuple[Token, Token, Token])
    # TODO Implement method for generating all 3 token combos

    def possible_actions(self, player: Player, **kwargs) -> list[Action]:
        """Checks all possible actions for the given player."""
        # TODO: Implement for agents in the future
        pass

    def legal_actions(self, player: Player, **kwargs) -> list[Action]:
        """Checks all legal actions for the given player."""
        pass
