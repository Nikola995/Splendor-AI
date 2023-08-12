from dataclasses import dataclass, field
from cards import Card
from nobles import Noble
from game_base.tokens import Token, TokenBag


@dataclass(slots=True)
class Player:
    """A representation of a player entity within the game."""

    # TODO make it a user account with elo (in the future)
    # For now just use a string name
    id: str
    token_reserved: TokenBag = field(default_factory=TokenBag)
    cards_reserved: list[Card] = field(default_factory=lambda: [None] * 3)
    cards_owned: list[Card] = field(default_factory=list)
    # Bonuses from Owned Cards, Wildcard in TokenBag is unused
    bonus_owned: TokenBag = field(default_factory=TokenBag)
    nobles_owned: list[Noble] = field(default_factory=list)
    # Metric for winning the game. >= 15 is eligible to win the game
    prestige_points: int = 0

    def can_remove_token(self, amount_to_remove: dict[Token, int]) -> bool:
        """Check if tokens of given colors can be removed."""
        return all([(self.token_reserved.tokens[color] - amount_to_remove[color]
                     >= 0) for color in amount_to_remove])

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
        return (sum(self.token_reserved.tokens.values()) +
                sum(amount_to_add.values()) <= 10)

    def add_token(self, amount_to_add: dict[Token, int]) -> None:
        """Add tokens of given colors by the amount given for each.
        Assumes can_add_token check was made.
        Function call is only done when a player reserves a card or
        reserves tokens from the bank.

        Parameters
        ----------
        amount_to_add : dict[Token, int]
            A dict of colors and corresponding amount of tokens to add.
        """
        # Sanity check if you don't check before calling this fn
        if not self.can_add_token(amount_to_add):
            raise ValueError("Too many tokens were given to"
                             f" the player {self.id}")
        self.token_reserved.add(amount_to_add)

    @property
    def num_reserved_cards(self) -> int:
        """The number of reserved card slot filled by a card."""
        return len([card for card in self.cards_reserved if card is not None])

    def can_reserve_card(self) -> bool:
        """Check if player has less than 3 reserved cards."""
        return self.num_reserved_cards < 3

    def add_to_reserved_cards(self, card: Card) -> None:
        """Adds card to the first open slot in reserved cards.
        Assumes can_reserve_card check was made."""
        # Sanity check if you don't check before calling this fn
        if not self.can_reserve_card():
            raise ValueError(f"Player {self.id} has no open slots to reserve "
                             "another card.")
        # The wildcard token given when reserving a card should be handled
        # in the Action, this method just reserves the card for the player
        for i in range(len(self.cards_reserved)):
            if self.cards_reserved[i] is None:
                self.cards_reserved[i] = card
                break

    def remove_from_reserved_cards(self, card: Card) -> None:
        """Removes card from its slot in reserved cards.

        Raises:
            ValueError: If the card is not in the Player's reserved cards
        """
        # Sanity check
        if card not in self.cards_reserved:
            raise ValueError(f"Card {card} was not found in the reserved "
                             f"cards of Player {self.id}")
        self.cards_reserved[self.cards_reserved.index(card)] = None

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
        color_costs = card.token_cost.tokens
        for color in color_costs:
            player_buying_power = (self.bonus_owned.tokens[color] +
                                   self.token_reserved.tokens[color])
            # If the card can be purchased without wildcards
            if color_costs[color] <= player_buying_power:
                continue
            # If the card can be purchased with wildcards
            # that weren't reserved for previous costs
            # in the card requirements
            elif color_costs[color] <= (player_buying_power +
                                        self.token_reserved.tokens[Token.YELLOW]
                                        - collateral_wildcards):
                # Add the remainder of the cost to the number of
                # collateral wildcards for the purchase
                collateral_wildcards += (color_costs[color] -
                                         player_buying_power)
                continue
            # Else the card can't be purchased
            else:
                return False
        return True

    def add_to_owned_cards(self, card: Card) -> None:
        """Add card to list of owned cards.

        Automatically removes card from reserved cards if found there.
        Automatically adds bonus and prestige points from card.

        Parameters
        ----------
        card : Card
            Card to add to owned cards
        """
        if card in self.cards_reserved:
            self.remove_from_reserved_cards(card)
        self.cards_owned.append(card)
        self.bonus_owned.add({card.bonus_color: 1})
        self.prestige_points += card.prestige_points

    def purchase_card(self, card: Card) -> dict[Token, int]:
        """Purchases the given card for the player.

        The process of purchasing a card follows this process for each color
        in the card's cost amounts:

            1. The owned bonuses discount the price of the card
            (the card can be purchased with just bonuses)

            3. The reserved tokens are removed from the player's inventory
            by the remaining amount of the card cost

            2. Wildcard tokens are used as collateral for the remaining cost,
            (if there is remaining cost) and remove the total amount from the
            player's inventory.

        Post-purchase, the card is added to the player's owned cards.

        Parameters
        ----------
        card : Card
            The card that the player wants to purchase.

        Returns:
            dict[Token, int]: The token amounts that are removed from the
            player and are to be returned to the bank.
        """
        # Sanity check
        if not self.can_purchase_card(card):
            raise ValueError(f"Player {self.id} can't purchase {card}.")

        removed_tokens = {Token.YELLOW: 0}
        color_costs = card.token_cost.tokens
        for color in color_costs:
            removed_tokens[color] = max((color_costs[color] -
                                         self.bonus_owned.tokens[color]), 0)
            collatteral = max((color_costs[color] -
                               (self.bonus_owned.tokens[color] +
                                removed_tokens[color])), 0)
            if collatteral:
                removed_tokens[color] += collatteral
        self.token_reserved.remove(removed_tokens)
        self.add_to_owned_cards(card)
        return removed_tokens

    def is_eligible_for_noble(self, noble: Noble) -> bool:
        """Check if the player is eligible to own the noble.

        Parameters
        ----------
        noble : Noble
            The noble whose bonuses we check against
        """
        return all([(self.bonus_owned.tokens[color] >=
                     noble.bonus_required.tokens[color])
                    for color in noble.bonus_required.tokens])

    def add_noble(self, noble: Noble) -> None:
        """Add noble to list of owned nobles.

        Automatically adds bonus and prestige points from card

        Parameters
        ----------
        noble : Noble
            Noble to add to owned nobles
        """
        if not self.is_eligible_for_noble(noble):
            raise ValueError(f"Player {self.id} is not eligible for "
                             f"Noble {noble}")
        self.nobles_owned.append(noble)
        self.prestige_points += noble.prestige_points

    def __lt__(self, other):
        """Used for sorting in Game to get the winner.
        If there's more than one eligible player to win,
        sort by most prestige points, then least owned cards."""
        if isinstance(other, Player):
            return ((self.prestige_points, -len(self.cards_owned)) <
                    (other.prestige_points, -len(other.cards_owned)))
        raise TypeError(
            f"Comparison not supported between 'Player' and {type(other)}")

    def __eq__(self, other):
        """Used for sorting in Game to get the winner.
        If there's more than one eligible player to win,
        sort by most prestige points, then least owned cards."""
        if isinstance(other, Player):
            return ((self.id, self.prestige_points, -len(self.cards_owned)) ==
                    (other.id, other.prestige_points, -len(other.cards_owned)))
        return False

    def __str__(self) -> str:
        return '\n'.join([f"Player ID: {self.id}",
                          f"Prestige points: {self.prestige_points}",
                          "Number of purchased cards: "
                          f"{len(self.cards_owned)}",
                          f"Number of nobles: {len(self.nobles_owned)}",
                          "Number of reserved cards: "
                          f"{self.num_reserved_cards}",
                          "--Reserved cards--",
                          *[str(card) for card in self.cards_reserved],
                          "--Bonuses from purchased cards--",
                          str(self.bonus_owned),
                          "--Reserved tokens--",
                          str(self.token_reserved),])
