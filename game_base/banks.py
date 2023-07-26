from dataclasses import dataclass, InitVar
from typing import Tuple
from utils import IncorrectInputError
from tokens import TokenBag, Token


# TODO Make it a singleton (refactor) (maybe?)
@dataclass(slots=True)
class Bank:
    """A representation of the unreserved tokens in the game."""

    token_available: TokenBag
    num_players: InitVar[int] = 4

    def __post_init__(self, num_players: int):
        match num_players:
            case 4: self.token_available = TokenBag(standard_amount=7,
                                                    wildcard_amount=5)
            case 3: self.token_available = TokenBag(standard_amount=5,
                                                    wildcard_amount=5)
            case 2: self.token_available = TokenBag(standard_amount=4,
                                                    wildcard_amount=5)
            case other: raise ValueError("Cannot initialize a bank for "
                                         f"{num_players}, only 2, 3 or 4")

    def can_remove_token(self, amount_to_remove: dict[Token, int]) -> bool:
        """Check if tokens of given colors can be removed."""
        for color in amount_to_remove:
            match amount_to_remove[color]:
                case 2: return False if self.token_available[color] < 4 else None
                case 1: return False if self.token_available[color] < 1 else None
                case other: raise ValueError("Can only remove 1 or 2 tokens "
                                             "per color, tried to remove "
                                             f"{other}")
        return True

    def remove_3_unique_color_tokens(self,
                                     colors: Tuple[Token, Token, Token]) -> bool:
        """Remove 3 tokens of unique colors from the bank.
        Assumes can_remove_token check was made.

        Parameters
        ----------
        color_list : Tuple[Token, Token, Token]
            Tuple containing 3 token colors

        Raises
        ------
        IncorrectInputError
            Raised if 3 unique colors are not given or wildcard is given
        """
        # TODO: Remove the sanity checks if never raised and need speed-up.
        if len(set(colors)) != 3:
            raise IncorrectInputError("The 3 token colors were not unique")
        if Token.YELLOW in colors:
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        for color in colors:
            self.token_available[color] -= 1
        return True

    def remove_2_same_color_tokens(self, color: Token) -> bool:
        """Remove 2 tokens of the same color from the bank.
        Assumes can_remove_token check was made.

        Parameters
        ----------
        color : Token
            Color for the 2 tokens

        Raises
        ------
        IncorrectInputError
            Raised if wildcard color is given
        """
        # TODO: Remove the sanity checks if never raised and need speed-up.
        if color == Token.YELLOW:
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        self.token_available[color] -= 2
        return True

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
