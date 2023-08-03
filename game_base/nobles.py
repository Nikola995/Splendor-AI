from dataclasses import dataclass, field, InitVar
from typing import List
from random import shuffle
from game_base.tokens import Token, TokenBag


@dataclass(frozen=True, slots=True)
class Noble:
    """Representation of the Noble cards."""
    # Initialization variable for the bonus amounts
    input_bonuses: InitVar[dict[Token, int]]
    # Number of prestige points the noble is worth
    prestige_points: int = 3
    # Number of bonuses per color required to acquire noble (constant values!)
    bonus_required: TokenBag = field(default_factory=TokenBag)

    def __post_init__(self, input_bonuses: dict[Token, int]) -> None:
        self.bonus_required.add(input_bonuses)
        if self.bonus_required.tokens[Token.YELLOW]:
            raise ValueError("A noble can't require wildcard bonuses")

    def __str__(self) -> str:
        return "\n".join([f"Prestige points: {self.prestige_points}",
                          "Bonuses required:", f"{self.bonus_required}"])


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
