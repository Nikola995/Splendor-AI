from dataclasses import dataclass, InitVar
from typing import Tuple, Dict
from utils import IncorrectInputError
from .tokens import TokenBag, Token


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

    def can_remove_token(self, amount_to_remove: Dict[Token, int]) -> bool:
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
            if self.token_available[color] < 0:
                # Should only happen if you don't do the can_remove_token check
                raise ValueError(f"Too many {color} tokens "
                                 "were taken from the bank")
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
        if self.token_available[color] < 2:
            # Should only happen if you don't do the can_remove_token check
            raise ValueError(f"Too many {color} tokens "
                             "were taken from the bank")
        return True

    def remove_wildcard_token(self) -> bool:
        """Removes a single wildcard token from the bank.
        Assumes can_remove_token check was made and function call is
        only done while a player reserves a card.
        """
        self.token_available[Token.YELLOW] -= 1
        if self.token_available[Token.YELLOW] < 0:
            # Should only happen if you don't do the can_remove_token check
            raise ValueError(f"Too many {Token.YELLOW} tokens "
                             "were taken from the bank")
        return True

    def add_token(self, amount_to_add: Dict[Token, int]) -> bool:
        """Add an amount of tokens for given colors to the bank.
        Function call is only done while a player purchases a card.

        Parameters
        ----------
        amount_to_add : Dict[Token, int]
            A dict of colors and corresponding amount of tokens to add.
        """
        for color in amount_to_add:
            self.token_available[color] += amount_to_add[color]
        return True
