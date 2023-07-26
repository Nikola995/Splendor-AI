from dataclasses import dataclass, field
from utils import IncorrectInputError


# TODO Make it a singleton (refactor) (maybe?)
@dataclass
class Bank:
    """A representation of the unreserved tokens in the game."""

    # Available tokens per color (type)
    token_available: dict[str, int] = field(default_factory=lambda: (
        {"green": 7,
         "white": 7,
         "blue": 7,
         "black": 7,
         "red": 7,
         # Yellow is the wildcard
         "yellow": 5}))

    def _can_remove_token(self, amount_to_remove: dict[str, int],
                          threshold=0) -> bool:
        """Check if tokens of given colors can be removed."""
        for color in amount_to_remove:
            if (self.token_available[color] - amount_to_remove[color]
                    < threshold):
                return False
        return True

    def _remove_token(self, amount_to_remove: dict[str, int],
                      threshold=0, verbose=0) -> bool:
        """Remove an amount of tokens for given colors.

        (*Use in action functions only for wildcard (yellow), other colors
         have already implemented methods)

        Parameters
        ----------
        amount_to_remove : dict[str, int]
            A dict of colors (keys) and amount of tokens to remove (values)

        Raises
        ------
        IncorrectInputError
            Raise if invalid color names are given

        TokenThresholdError
            Raise if the amount of tokens removed for a given color leaves the
            bank with negative amount ( < 0)
        """
        if not set(amount_to_remove.keys()).issubset(
                self.token_available.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_remove_token(amount_to_remove, threshold):
            for color in amount_to_remove:
                self.token_available[color] -= amount_to_remove[color]
            return True
        else:
            return False
# =============================================================================
#             raise TokenThresholdError("Tried to take more tokens"
#                                       "than available in the bank")
# =============================================================================

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

    def remove_3_different_color_tokens(self, color_list: list[str],
                                        verbose=0) -> bool:
        """Remove 3 tokens of different color from the bank.

        Parameters
        ----------
        color_list : list[str]
            List of size 3 of colors

        Raises
        ------
        IncorrectInputError
            Raised if 3 colors are not given, or an incorrect color is given,
            or 'yellow' is given
        """
        if len(color_list) != 3:
            raise IncorrectInputError("3 colors were not given")
        if 'yellow' in color_list:
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        return self._remove_token(dict.fromkeys(color_list, 1))

    def remove_2_same_color_tokens(self, color: str, verbose=0) -> bool:
        """Remove 2 tokens of the same color from the bank.

        Only if the bank has 4 tokens of that color available.

        Parameters
        ----------
        color_list : str
            Color for 2 tokens

        Raises
        ------
        IncorrectInputError
            Raised if an incorrect color is given,
            or 'yellow' is given
        TokenThresholdError
            Bank has less than 4 tokens of a given color, can't remove 2.
        """
        if color == 'yellow':
            raise IncorrectInputError("Yellow token cannot be removed without"
                                      " reserving a card")
        return self._remove_token({color: 2}, threshold=2)