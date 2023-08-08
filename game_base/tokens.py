from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass, field, InitVar


class Token(Enum):
    GREEN = auto()
    WHITE = auto()
    BLUE = auto()
    BLACK = auto()
    RED = auto()
    YELLOW = auto()

    def __str__(self) -> str:
        return f"{self.name.lower()}"


@dataclass(slots=True)
class TokenBag:
    """A collection that holds the amount of tokens for each color that
    game entities use."""
    tokens: dict[Token, int] = field(init=False)
    standard_amount: InitVar[int] = 0
    wildcard_amount: InitVar[Optional[int]] = None

    def __post_init__(self, standard_amount: int,
                      wildcard_amount: Optional[int]):
        """Initialize the Token Bag with a standard amount of tokens
        for all colors and possible separate amount for wildcard tokens.
        Default initialization is an empty Token Bag.
        Cannot work with negative values.

        Args:
            standard_amount InitVar[int]: The standard amount of tokens for
            all colors. Defaults to 0.
            wildcard_amount InitVar[int]: The separate amount for wildcard tokens.
            Will only apply if different value than standard_amount.
            Defaults to 0.
        """
        if (standard_amount < 0 or
                (wildcard_amount is not None and wildcard_amount < 0)):
            raise ValueError("TokenBag cannot work with negative values.")
        self.tokens = {token_color: standard_amount
                       for token_color in Token}
        if wildcard_amount is not None:
            self.tokens[Token.YELLOW] = wildcard_amount

    def add(self, amount: dict[Token, int]) -> 'TokenBag':
        """Adds tokens of given colors by the amount given for each."""
        for color in amount:
            if amount[color] < 0:
                raise ValueError("TokenBag cannot work with negative values.")
            self.tokens[color] += amount[color]
        return self

    def remove(self, amount: dict[Token, int]) -> 'TokenBag':
        """Removes tokens of given colors by the amount given for each.
        Assumes you're not going to 'remove' negative amounts."""
        for color in amount:
            self.tokens[color] -= amount[color]
            if self.tokens[color] < 0 or amount[color] < 0:
                raise ValueError("TokenBag cannot work with negative values.")
        return self

    def __eq__(self, other):
        if isinstance(other, TokenBag):
            return self.tokens == other.tokens
        return False

    def __lt__(self, other):
        if isinstance(other, TokenBag):
            return all([self.tokens[color] < other.tokens[color]
                        for color in self.tokens])
        raise TypeError(
            f"Comparison not supported between 'TokenBag' and {type(other)}")

    def __le__(self, other):
        if isinstance(other, TokenBag):
            return all([self.tokens[color] <= other.tokens[color]
                        for color in self.tokens])
        raise TypeError(
            f"Comparison not supported between 'TokenBag' and {type(other)}")

    def __gt__(self, other):
        if isinstance(other, TokenBag):
            return all([self.tokens[color] > other.tokens[color]
                        for color in self.tokens])
        raise TypeError(
            f"Comparison not supported between 'TokenBag' and {type(other)}")

    def __ge__(self, other):
        if isinstance(other, TokenBag):
            return all([self.tokens[color] >= other.tokens[color]
                        for color in self.tokens])
        raise TypeError(
            f"Comparison not supported between 'TokenBag' and {type(other)}")

    def __str__(self) -> str:
        return "\n".join([f"{str(color).capitalize():<5}: {self.tokens[color]}"
                          for color in self.tokens if self.tokens[color] > 0])
