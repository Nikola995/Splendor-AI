from dataclasses import dataclass, field, InitVar
from game_base.utils import IncorrectInputError
from game_base.tokens import TokenBag, Token


# TODO Make it a singleton (refactor) (maybe?)
@dataclass(slots=True)
class Bank:
    """A representation of the unreserved tokens in the game."""

    token_available: TokenBag = field(init=False)
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
                case 2:
                    if self.token_available.tokens[color] < 4:
                        return False
                case 1:
                    if self.token_available.tokens[color] < 1:
                        return False
                case other:
                    raise ValueError("Can only remove 1 or 2 tokens per color"
                                     f", tried to remove {other}")
        return True

    def remove_3_unique_color_tokens(self,
                                     colors: tuple[Token, Token, Token]) -> None:
        """Remove 3 tokens of unique colors from the bank.
        Assumes can_remove_token check was made.

        Parameters
        ----------
        color_list : tuple[Token, Token, Token]
            Tuple containing 3 unique token colors

        Raises
        ------
        IncorrectInputError
            Raised if 3 unique colors are not given or wildcard is given
        """
        # TODO: Remove the sanity checks if never raised and need speed-up.
        if len(colors) != 3:
            raise IncorrectInputError("The number of token colors was not 3")
        if len(set(colors)) != 3:
            raise IncorrectInputError("The 3 token colors were not unique")
        if Token.YELLOW in colors:
            raise IncorrectInputError("Yellow token can only be removed when"
                                      " reserving a card")

        self.token_available.remove(dict.fromkeys(colors, 1))

    def remove_2_same_color_tokens(self, color: Token) -> None:
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
        amount_to_remove = {color: 2}
        # Sanity check if you don't check before calling this fn
        if not self.can_remove_token(amount_to_remove):
            raise ValueError(f"Can't take 2 {color} tokens when there are"
                             f"{self.token_available.tokens[color]} left "
                             "in the bank")
        self.token_available.remove(amount_to_remove)

    def remove_wildcard_token(self) -> None:
        """Removes a single wildcard token from the bank.
        Assumes can_remove_token check was made and function call is
        only done while a player reserves a card.
        """
        self.token_available.remove({Token.YELLOW: 1})

    def add_token(self, amount_to_add: dict[Token, int]) -> None:
        """Add an amount of tokens for given colors to the bank.
        Function call is only done while a player purchases a card.

        Parameters
        ----------
        amount_to_add : dict[Token, int]
            A dict of colors and corresponding amount of tokens to add.
        """
        self.token_available.add(amount_to_add)

    def __str__(self) -> str:
        return ("Available Bank tokens:\n"
                f"{self.token_available}")
