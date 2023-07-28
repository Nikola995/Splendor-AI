from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from actions import (Action, Reserve2SameColorTokens,
                     Reserve3UniqueColorTokens, ReserveCard,
                     PurchaseCard)
from players import Player


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


@dataclass(slots=True)
class StandardActionSet(ActionSet):
    """All standard game actions."""
    actions: list[Action] = field(default_factory=lambda:
                                  ([Reserve2SameColorTokens, PurchaseCard,
                                    ReserveCard, Reserve3UniqueColorTokens]))
    
    def possible_actions(self, player: Player, ) -> list[Action]:
        """Checks all possible actions for the given player."""
        # TODO: Implement for agents in the future
        pass

    def legal_actions(self, player: Player, **kwargs) -> list[Action]:
        """Checks all legal actions for the given player."""
        pass
