from dataclasses import dataclass, field
from cards import Card
from nobles import Noble
from utils import IncorrectInputError

@dataclass(order=True)
class Player:
    """A representation of a player entity within the game."""

    # TODO make it a user account with elo (in the future)
    # For now just use a string name
    player_id: str
    # Reserved tokens per color (type)
    token_reserved: dict[str, int] = field(default_factory=lambda: (
        {"green": 0,
         "white": 0,
         "blue": 0,
         "black": 0,
         "red": 0,
         "yellow": 0}))
    # Owned Cards
    cards_owned: list[Card] = field(default_factory=list)
    # Reserved Cards
    cards_reserved: dict[str, Card] = field(default_factory=dict)
    # Owned Nobles
    nobles_owned: list[Noble] = field(default_factory=list)
    # Bonuses per color (type)
    bonus_owned: dict[str, int] = field(default_factory=lambda: ({"green": 0,
                                                                  "white": 0,
                                                                  "blue": 0,
                                                                  "black": 0,
                                                                  "red": 0}))
    # Prestige points
    prestige_points: int = 0

    def _can_remove_token(self, amount_to_remove: dict[str, int]) -> bool:
        """Check if tokens of given colors can be removed."""
        for color in amount_to_remove:
            if (self.token_reserved[color] - amount_to_remove[color] < 0):
                return False
        return True

    def remove_token(self, amount_to_remove: dict[str, int]) -> bool:
        """Remove tokens of given colors by the amount given for each.

        Will be unsuccessful if the given amount for any given color is
        more than the amount reserved by the player (for that color).

        Parameters
        ----------
        amount_to_remove : dict[str, int]
            A dict of colors (keys) and amount of tokens to remove (values)

        Raises
        ------
        IncorrectInputError
            Raise if an invalid color was given in amount_to_remove.

        Returns
        -------
        bool
            Whether or not the tokens were removed from the player.
        """
        if not set(amount_to_remove.keys()).issubset(
                self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_remove_token(amount_to_remove):
            for color in amount_to_remove:
                self.token_reserved[color] -= amount_to_remove[color]
            return True
        else:
            return False
# =============================================================================
#             raise TokenThresholdError("Tried to take more tokens"
#                                       f"from {self.player_id} than"
#                                       "available")
# =============================================================================

    def _can_add_token(self, amount_to_add: dict[str, int]) -> bool:
        """Check if tokens of given colors can be added."""
        if (sum(self.token_reserved.values()) +
                sum(amount_to_add.values()) > 10):
            return False
        else:
            return True

    def add_token(self, amount_to_add: dict[str, int]) -> bool:
        """Add tokens of given colors by the amount given for each.

        Will be unsuccessful if sum amount of all tokens added plus the sum
        amount of all tokens reserved by the player is more than 10.

        Parameters
        ----------
        amount_to_add : dict[str, int]
            A dict of colors (keys) and amount of tokens to add (values).

        Raises
        ------
        IncorrectInputError
            Raise if an invalid color was given in amount_to_add.

        Returns
        -------
        bool
            Whether or not the tokens were added to the player.
        """
        if not set(amount_to_add.keys()).issubset(self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if self._can_add_token(amount_to_add):
            for color in amount_to_add:
                self.token_reserved[color] += amount_to_add[color]
            return True
        else:
            return False
# =============================================================================
#             raise TooManyTokensForPlayerError("A player cannot have more"
#                                               " than 10 tokens in total"
#                                               " reserved")
# =============================================================================

    def can_reserve_card(self) -> bool:
        """Check if player has less than 3 reserved cards."""
        # Should never have more than 3 reserved cards, but just in case use >=
        if len(self.cards_reserved) >= 3:
            return False
        else:
            return True
# =============================================================================
#             raise ActionNotPossibleError("Player has 3 reserved cards, "
#                                          "can't reserve more")
# =============================================================================

    def add_to_reserved_cards(self, card: Card, card_id: str) -> None:
        """Add card to dict of reserved cards."""
        # The card is reserved even if there isn't a wildcard token to reserve
        self.cards_reserved[card_id] = (card)

    def can_purchase_card(self, card: Card,
                          yellow_replaces: dict[str, int]) -> bool:
        """Check if the player can purchase the given card.

        Returns True if the sum of each color of owned bonuses,
        yellow tokens given as collateral and reserved tokens of the player
        is >= than the cost of tokens of the card for those colors.

        Parameters
        ----------
        card : Card
            The card that the player wants to purchase.
        yellow_replaces : dict[str, int]
            A dict of colors (keys) and amount of yellow tokens
            given to replace tokens for each given color (values).

        Raises
        ------
        IncorrectInputError
            Raises in two case:
                If an invalid color was given in yellow_replaces.
                if the sum of tokens (values) in yellow_replaces is more
                than the amount of tokens in token_reserved['yellow']

        Returns
        -------
        bool
            Whether or not the player can purchase the card.
        """
        if not set(yellow_replaces.keys()).issubset(
                self.token_reserved.keys()):
            raise IncorrectInputError("Invalid colors were given")
        if sum(yellow_replaces.values()) > self.token_reserved['yellow']:
            raise IncorrectInputError(f"{sum(yellow_replaces.values())} yellow"
                                      " tokens given as collateral, but only "
                                      f"{self.token_reserved['yellow']} yellow"
                                      " tokens available")
        player_buying_power = 0
        for color in card.token_cost:
            player_buying_power = (self.bonus_owned[color] +
                                   self.token_reserved[color] +
                                   yellow_replaces[color])
            if card.token_cost[color] > player_buying_power:
                return False
        return True

    # TODO: add an input type check, and with that change output to bool
    def add_to_owned_cards(self, card: Card) -> None:
        """Add card to list of owned cards.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        card : Card
            Card to add to owned cards
        """
        self.cards_owned.append(card)
        self.bonus_owned[card.bonus_color] += 1
        self.prestige_points += card.prestige_points

    # TODO: add an input type check
    def is_eligible_for_noble(self, noble: Noble, verbose=0) -> bool:
        """Check if the player is eligible to own the noble.

        If the player's owned bonuses are more or equal to the
        required bonuses of the noble, they are eligible.

        Parameters
        ----------
        noble : Noble
            The noble whose bonuses we check against

        Returns
        -------
        bool
            Eligibility of the player to own the noble
        """
        for color in noble.bonus_required:
            # If the player doesn't have enough bonuses for the noble
            if self.bonus_owned[color] < noble.bonus_required[color]:
                return False
        # If all the checks pass, that must mean the player is eligible
        return True

    # TODO: add an input type check, and with that change output to bool
    def add_to_owned_nobles(self, noble: Noble) -> None:
        """Add noble to list of owned nobles.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        noble : Noble
            Noble to add to owned nobles
        """
        self.nobles_owned.append(noble)
        self.prestige_points += noble.prestige_points