from dataclasses import dataclass, field, InitVar
from game_base.tokens import TokenBag, Token


@dataclass(slots=True)
class Bank:
    """A representation of the unreserved tokens in the game."""

    token_available: TokenBag = field(init=False)
    initial_regular_token_amount: int = field(init=False)
    initial_wildcard_token_amount: int = field(init=False)
    num_players: InitVar[int] = 4

    def __post_init__(self, num_players: int):
        match num_players:
            case 4: self.initial_regular_token_amount = 7
            case 3: self.initial_regular_token_amount = 5
            case 2: self.initial_regular_token_amount = 4
            case _: raise ValueError("Cannot initialize a bank for "
                                     f"{num_players}, only 2, 3 or 4")
        self.initial_wildcard_token_amount = 5
        self.token_available = TokenBag(self.initial_regular_token_amount,
                                        self.initial_wildcard_token_amount)

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
                case 0: return True
                case other_amount:
                    raise NotImplementedError("There are no ways to remove "
                                              f"{other_amount} tokens.")
        return True

    def remove_token(self, amount_to_remove: dict[Token, int]) -> None:
        """Remove an amount of tokens for each given colors from the bank.

        Parameters
        ----------
        amount_to_remove : dict[Token, int]
            A dict of colors and corresponding amount of tokens to remove.
        """
        # Sanity check
        if not self.can_remove_token(amount_to_remove):
            raise ValueError("The amounts given can't be removed from "
                             "the bank")
        self.token_available.remove(amount_to_remove)

    # TODO: create can_add_token method
    # TODO: add can_add_token check inside add_token
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
