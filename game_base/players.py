from dataclasses import dataclass, field
from cards import Card
from nobles import Noble
from game_base.tokens import Token, TokenBag


@dataclass(order=True, slots=True)
class Player:
    """A representation of a player entity within the game."""

    # TODO make it a user account with elo (in the future)
    # For now just use a string name
    id: str
    token_reserved: TokenBag = field(default_factory=TokenBag)
    cards_reserved: list[Card] = field(default_factory=list)
    cards_owned: list[Card] = field(default_factory=list)
    # Bonuses from Owned Cards, Wildcard in TokenBag is unused
    bonus_owned: TokenBag = field(default_factory=TokenBag)
    nobles_owned: list[Noble] = field(default_factory=list)
    # Metric for winning the game. >= 15 is eligible to win the game
    prestige_points: int = 0

    def can_remove_token(self, amount_to_remove: dict[Token, int]) -> bool:
        """Check if tokens of given colors can be removed."""
        return all([self.token_reserved[color] - amount_to_remove[color] >= 0
                    for color in amount_to_remove])

    def remove_token(self, amount_to_remove: dict[Token, int]) -> None:
        """Remove tokens of given colors by the amount given for each.
        Assumes can_remove_token check was made.
        Function call is only done while a player purchases a card.

        Parameters
        ----------
        amount_to_remove : dict[Token, int]
            A dict of colors and corresponding amount of tokens to remove.
        """
        self.token_reserved.remove(amount_to_remove)

    def can_add_token(self, amount_to_add: dict[Token, int]) -> bool:
        """Check if tokens of given colors can be added."""
        return (sum(self.token_reserved.values()) +
                sum(amount_to_add.values()) <= 10)

    def add_token(self, amount_to_add: dict[Token, int]) -> None:
        """Add tokens of given colors by the amount given for each.
        Assumes can_remove_token check was made.
        Function call is only done when a player reserves a card or
        reserves tokens from the bank.

        Parameters
        ----------
        amount_to_add : dict[Token, int]
            A dict of colors and corresponding amount of tokens to add.
        """
        # Sanity check if you don't check before calling this fn
        if not self.can_add_token():
            raise ValueError("Too many tokens were given to"
                             f" the player {self.id}")
        self.token_reserved.add(amount_to_add)

    def can_reserve_card(self) -> bool:
        """Check if player has less than 3 reserved cards."""
        return len(self.cards_reserved) < 3

    def add_to_reserved_cards(self, card: Card) -> None:
        """Add card to dict of reserved cards.
        Assumes can_reserve_card check was made."""
        # Sanity check if you don't check before calling this fn
        if not self.can_reserve_card():
            raise ValueError(f"Player {self.id} has too many"
                             "reserved cards")
        # The wildcard token given when reserving a card should be handled
        # in the Action, this method just reserves the card for the player
        self.cards_reserved.append(card)

    # TODO: Write tests for this
    def can_purchase_card(self, card: Card) -> bool:
        """Check if the player can purchase the given card.

        Returns True if the sum of each color of owned bonuses,
        reserved tokens of the player and wildcard tokens given as collateral
        is >= than the cost of tokens of the card for those colors.

        Parameters
        ----------
        card : Card
            The card that the player wants to purchase.
        """
        collateral_wildcards = 0
        for color in card.token_cost:
            player_buying_power = (self.bonus_owned[color] +
                                   self.token_reserved[color])
            # If the card can be purchased without wildcards
            if card.token_cost[color] <= player_buying_power:
                continue
            # If the card can be purchased with wildcards
            # that weren't reserved for previous costs
            # in the card requirements
            elif card.token_cost[color] <= (player_buying_power +
                                            self.token_reserved[Token.YELLOW]
                                            - collateral_wildcards):
                # Add the remainder of the cost to the number of
                # collateral wildcards for the purchase
                collateral_wildcards += (card.token_cost[color] -
                                         player_buying_power)
                continue
            # Else the card can't be purchased
            else:
                return False
        return True

    def add_to_owned_cards(self, card: Card) -> None:
        """Add card to list of owned cards.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        card : Card
            Card to add to owned cards
        """
        self.cards_owned.append(card)
        self.bonus_owned.add({card.bonus_color: 1})
        self.prestige_points += card.prestige_points

    def is_eligible_for_noble(self, noble: Noble) -> bool:
        """Check if the player is eligible to own the noble.

        Parameters
        ----------
        noble : Noble
            The noble whose bonuses we check against
        """
        return all([self.bonus_owned[color] >= noble.bonus_required[color]
                    for color in noble.bonus_required])

    def add_noble(self, noble: Noble) -> None:
        """Add noble to list of owned nobles.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        noble : Noble
            Noble to add to owned nobles
        """
        self.nobles_owned.append(noble)
        self.prestige_points += noble.prestige_points

    def __str__(self) -> str:
        return '\n'.join([f"Player ID: {self.id}",
                          f"Prestige points: {self.prestige_points}",
                          f"Number of nobles: {len(self.nobles_owned)}",
                          "Number of reserved cards: "
                          f"{len(self.cards_reserved)}",
                          "Number of purchased cards: "
                          f"{len(self.cards_owned)}",
                          f"--Bonuses from purchased cards--",
                          str(self.bonus_owned),
                          f"--Reserved tokens--",
                          str(self.token_reserved)])
