from dataclasses import dataclass, field
from random import shuffle
import pandas as pd
import pickle
from os import path
from .tokens import Token, TokenBag

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

    def __post_init__(self):
        # Cards are ordered by their level
        object.__setattr__(self, '_sort_index', self.level)

@dataclass(slots=True)
class CardManager:
    """Contains a deck (face-down) and table (face-up) of
    all cards of the same level,"""
    # All of the not visible cards
    deck: list[Card]
    # All of the visible cards
    table: list[Card] = field(default_factory=list)
    # Difficulty of purchasing cards
    card_level: int

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


class CardManagerCollection:
    """Contains the card managers for all card levels."""
    pass


class CardGenerator:
    def generate_from_csv(self) -> CardManagerCollection:
        cards_df = pd.read_csv(CARDS_FILE_PATH_CSV, header=1)
        cards_df['Level'] = cards_df['Level'].fillna(method='ffill')
        cards_df['Gem color'] = cards_df['Gem color'].fillna(method='ffill')
        cards_df['PV'] = cards_df['PV'].fillna(0)
        cards_df['(w)hite'] = cards_df['(w)hite'].fillna(0)
        cards_df['bl(u)e'] = cards_df['bl(u)e'].fillna(0)
        cards_df['(g)reen'] = cards_df['(g)reen'].fillna(0)
        cards_df['(r)ed'] = cards_df['(r)ed'].fillna(0)
        cards_df['blac(k)'] = cards_df['blac(k)'].fillna(0)

        cards_1 = []
        cards_2 = []
        cards_3 = []
        for index, row in cards_df.iterrows():
            card = Card(level=int(row['Level']), prestige_points=int(row['PV']),
                        token_cost={Token.GREEN: int(row['(g)reen']),
                                    Token.WHITE: int(row['(w)hite']),
                                    Token.BLUE: int(row['bl(u)e']),
                                    Token.BLACK: int(row['blac(k)']),
                                    Token.RED: int(row['(r)ed'])},
                        bonus_color=Token[row['Gem color'].upper()])
            match card.level:
                case 1: cards_1.append(card)
                case 2: cards_2.append(card)
                case 3: cards_3.append(card)
                case other: raise Exception('Card level is not 1, 2 or 3')

    def save_to_pickle(self, cards_data: CardManagerCollection,
                       filepath: str = 'cards_lists.pickle') -> None:
        with open(filepath, 'wb') as f:
            pickle.dump(cards_data, f)

    def generate_cards(self, shuffled=True):
        '''Get all the cards formatted in the Card class saved in a pickle file

        Returns tuple (cards_1, cards_2, cards_3)
        -------
        cards_1 : list[Card]
            All cards with level 1\n
        cards_2 : list[Card]
            All cards with level 2\n
        cards_3 : list[Card]
            All cards with level 3

        '''
        if not path.exists(CARDS_FILE_PATH_PICKLE):
            cards_data = self.generate_from_csv()
            self.save_to_pickle(cards_data)
        else:
            with open(CARDS_FILE_PATH_PICKLE, 'rb') as f:
                cards_data = pickle.load(f)
        return cards_data.shuffle_decks() if shuffled else cards_data
