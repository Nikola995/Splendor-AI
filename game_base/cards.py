from dataclasses import dataclass, field, InitVar
from random import shuffle
import pandas as pd
import pickle
from os import path
from game_base.tokens import Token, TokenBag

CARDS_FILE_PATH_CSV = 'splendor_cards_list.csv'
CARDS_FILE_PATH_PICKLE = 'cards_manager_collection.pickle'


@dataclass(order=True, frozen=True, slots=True)
class Card:
    '''
    Cards are purchasable items by players that give them color bonuses
    and possible prestige points
    '''
    # Value by which this class is ordered
    _sort_index: int = field(init=False, repr=False)
    # Difficulty of purchasing development card
    level: int
    # Color of the bonus gem given by owning the card
    bonus_color: Token
    # Number of prestige points given by owning the card
    prestige_points: int
    # Number of tokens required to purchase the card per color
    token_cost: TokenBag
    # Card ID
    card_id: str = field(init=False)

    def __post_init__(self):
        if self.token_cost.tokens[Token.YELLOW]:
            raise ValueError("A card can't require wildcard tokens")
        if self.level not in [1, 2, 3]:
            raise ValueError('Card level is not 1, 2 or 3')
        # Cards are ordered by their level
        object.__setattr__(self, '_sort_index', self.level)
        # Ex. ID: 1 green 2 red -> 100002
        self.card_id = "".join([str(self.token_cost[color])
                                for color in self.token_cost
                                if color != Token.YELLOW])

    def __str__(self) -> str:
        output = []
        output.append(f"Card {self.card_id}")
        output.append("Card Cost")
        output.append(str(self.token_cost))
        output.append("Benefits of Purchasing Card")
        output.append(f"Prestige points: {self.prestige_points}")
        output.append(f"Bonus token: {self.bonus_color.name}")
        return '\n'.join(output)


@dataclass(slots=True)
class CardManager:
    """Contains a deck (face-down) and table (face-up) of
    all cards of the same level,"""
    # All of the not visible cards
    deck: list[Card]
    # Difficulty of purchasing cards
    card_level: int = field(init=False)
    # All of the visible cards
    table: list[Card] = field(default_factory=list)

    def __post_init__(self):
        self.card_level = self.deck[0].level

    def fill_table(self):
        """Fill the table with 4 cards from the deck."""
        # TODO: Make tests for this
        if len(self.table) < 4:
            for _ in range(4 - len(self.table)):
                self.table.append(self.deck.pop())

    def remove_card_from_table(self, card: Card) -> None:
        """Removes a card from the table, and replaces it with
        a card from the deck if possible, else None."""
        # TODO: Make tests for this
        self.table[self.table.index(card)] = (self.deck.pop() if self.deck
                                              else None)


@dataclass(slots=True)
class CardManagerCollection:
    """Contains the card managers for all card levels."""
    managers: list[CardManager] = field(init=False)
    cards: InitVar[list[Card]]

    def __post_init__(self, cards: list[Card]) -> None:
        # Separate the cards by level
        cards_1 = []
        cards_2 = []
        cards_3 = []
        for card in cards:
            match card.level:
                case 1: cards_1.append(card)
                case 2: cards_2.append(card)
                case 3: cards_3.append(card)
                case _: continue
        self.managers = [CardManager(cards_1),
                         CardManager(cards_2),
                         CardManager(cards_3)]

    def get_manager(self, card_level: int) -> CardManager:
        """Returns the card manager for the given card level."""
        for manager in self.managers:
            if manager.card_level == card_level:
                return manager
        raise ValueError(f"There is no cards manager for level {card_level}")

    def get_deck(self, card_level: int) -> list[Card]:
        """Returns the card deck for the given card level."""
        for manager in self.managers:
            if manager.card_level == card_level:
                return manager.deck
        raise ValueError(f"There is no cards deck for level {card_level}")

    def get_all_decks(self) -> list[list[Card]]:
        """Returns all of the card decks."""
        return [manager.deck for manager in self.managers]

    def get_table(self, card_level: int) -> list[Card]:
        """Returns the card table for the given card level."""
        for manager in self.managers:
            if manager.card_level == card_level:
                return manager.table
        raise ValueError(f"There is no cards table for level {card_level}")

    def get_all_tables(self) -> list[list[Card]]:
        """Returns all of the card tables."""
        return [manager.table for manager in self.managers]

    def get_all_cards_on_tables(self) -> list[Card]:
        """Returns a list of all cards on all tables."""
        # TODO: Test this
        # Flatten the list of tables
        return [card for table in self.get_all_tables()
                for card in table]

    def is_card_in_tables(self, card: Card) -> bool:
        """Checks if card is in any of the tables."""
        for manager in self.managers:
            if card in manager.table:
                return True
        return False

    def remove_card_from_tables(self, card: Card) -> None:
        """Removes the given card from the appropriate table.
        (Replaces it with a card from the deck if possible, else None)"""
        for manager in self.managers:
            if manager.card_level == card.level:
                manager.remove_card_from_table(card)

    def shuffle_decks(self) -> None:
        """Shuffle all of the decks."""
        [shuffle(manager.deck) for manager in self.managers]

    def fill_tables(self) -> None:
        """Fill all of the tables."""
        [manager.fill_table() for manager in self.managers]


class CardGenerator:
    """Generates a CardManagerCollection containing all of the cards."""

    def generate_from_csv(self) -> CardManagerCollection:
        """Generates the CardManagerCollection from the original card info
        in the .csv file."""
        cards_df = pd.read_csv(CARDS_FILE_PATH_CSV, header=1)
        columns_to_ffill = ['Level', 'Gem color']
        cards_df[columns_to_ffill] = (cards_df[columns_to_ffill]
                                      .fillna(method='ffill'))
        columns_to_fill_0 = ['PV', '(w)hite', 'bl(u)e', '(g)reen',
                             '(r)ed', 'blac(k)']
        cards_df[columns_to_fill_0] = (cards_df[columns_to_fill_0]
                                       .fillna(0))
        # Create cards from their info
        cards = [Card(level=int(row['Level']), prestige_points=int(row['PV']),
                      token_cost=TokenBag().add(
                          {Token.GREEN: int(row['(g)reen']),
                           Token.WHITE: int(row['(w)hite']),
                           Token.BLUE: int(row['bl(u)e']),
                           Token.BLACK: int(row['blac(k)']),
                           Token.RED: int(row['(r)ed'])}),
                      bonus_color=Token[row['Gem color'].upper()])
                 for row in cards_df.to_dict('records')]
        return CardManagerCollection(cards)

    def save_to_pickle(self, cards_data: CardManagerCollection,
                       filepath: str = 'cards_lists.pickle') -> None:
        """Save the CardManagerCollection from the original card info
        in a .pickle file."""
        with open(filepath, 'wb') as f:
            pickle.dump(cards_data, f)

    def generate_cards(self, shuffled=True) -> CardManagerCollection:
        """Returns the CardManagerCollection from the pickle file
        if it exists, or generated from the .csv file,
        shuffling the decks if requested.
        """
        if not path.exists(CARDS_FILE_PATH_PICKLE):
            cards_data = self.generate_from_csv()
            self.save_to_pickle(cards_data)
        else:
            with open(CARDS_FILE_PATH_PICKLE, 'rb') as f:
                cards_data = pickle.load(f)
        cards_data.shuffle_decks() if shuffled else None
        return cards_data
