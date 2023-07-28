from dataclasses import dataclass
from typing import List
from random import shuffle
from .tokens import Token, TokenBag


@dataclass(frozen=True, slots=True)
class Noble:
    # Number of bonuses per color required to acquire noble
    bonus_required: TokenBag
    # Number of prestige points the noble is worth
    prestige_points: int = 3


@dataclass
class NobleGenerator:
    """Generates a List of Nobles for the number of players in a game."""

    def default_nobles_list(self) -> List[Noble]:
        """Returns a list of all the default nobles."""
        return [Noble({Token.GREEN: 4, Token.WHITE: 0, Token.BLUE: 0,
                       Token.BLACK: 0, Token.RED: 4}),
                Noble({Token.GREEN: 0, Token.WHITE: 3, Token.BLUE: 0,
                       Token.BLACK: 3, Token.RED: 3}),
                Noble({Token.GREEN: 0, Token.WHITE: 4, Token.BLUE: 4,
                       Token.BLACK: 0, Token.RED: 0}),
                Noble({Token.GREEN: 0, Token.WHITE: 4, Token.BLUE: 0,
                       Token.BLACK: 4, Token.RED: 0}),
                Noble({Token.GREEN: 4, Token.WHITE: 0, Token.BLUE: 4,
                       Token.BLACK: 0, Token.RED: 0}),
                Noble({Token.GREEN: 3, Token.WHITE: 0, Token.BLUE: 3,
                       Token.BLACK: 0, Token.RED: 3}),
                Noble({Token.GREEN: 3, Token.WHITE: 3, Token.BLUE: 3,
                       Token.BLACK: 0, Token.RED: 0}),
                Noble({Token.GREEN: 0, Token.WHITE: 0, Token.BLUE: 0,
                       Token.BLACK: 4, Token.RED: 4}),
                Noble({Token.GREEN: 0, Token.WHITE: 3, Token.BLUE: 3,
                       Token.BLACK: 3, Token.RED: 0}),
                Noble({Token.GREEN: 3, Token.WHITE: 0, Token.BLUE: 0,
                       Token.BLACK: 3, Token.RED: 3})]

    def generate_nobles(self, num_players: int = 4) -> List[Noble]:
        """Returns n + 1 nobles for n players from a shuffled list."""
        return shuffle(self.default_nobles_list())[0:num_players + 1]
