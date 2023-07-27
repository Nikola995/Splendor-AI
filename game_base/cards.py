from dataclasses import dataclass, field
from random import shuffle
import pandas as pd
import pickle
from os import path
from .tokens import Token, TokenBag

@dataclass(order = True, frozen = True)
class Card:
    '''
    Cards are good
    '''
    #Value by which this class is ordered
    _sort_index: int = field(init=False, repr=False)
    #TODO make the level values:[1-3]
    #Difficulty of purchasing development card
    level: int
    #Color of the bonus gem given by owning the card
    bonus_color: Token
    #Number of prestige points given by owning the card
    prestige_points: int
    #Number of tokens required to purchase the card per color (type)
    token_cost: TokenBag
    
    def __post_init__(self):
        #Cards are ordered by their level
        object.__setattr__(self, '_sort_index', self.level)
        
def generate_cards_from_csv(save_to_pickle = False):
    csv_file_path = path.join(path.dirname(__file__), 'splendor_cards_list.csv')
    cards_df = pd.read_csv(csv_file_path,header=1)
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
    for index,row in cards_df.iterrows():
        card = Card(level = int(row['Level']), prestige_points = int(row['PV']),
                    token_cost = {Token.GREEN:int(row['(g)reen']),
                                  Token.WHITE:int(row['(w)hite']),
                                  Token.BLUE:int(row['bl(u)e']),
                                  Token.BLACK:int(row['blac(k)']),
                                  Token.RED:int(row['(r)ed'])},
                    bonus_color=Token[row['Gem color'].upper()])
        match card.level:
            case 1: cards_1.append(card)
            case 2: cards_2.append(card)
            case 3: cards_3.append(card)
            case other: raise Exception('Card level is not 1, 2 or 3')
            
    
    if save_to_pickle:
        pickle_file_path = path.join(path.dirname(__file__), 'cards_lists.pickle')
        with open(pickle_file_path, 'wb') as f:
            pickle.dump((cards_1, cards_2, cards_3), f)
    return None

def generate_cards_from_pickle():
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
    pickle_file_path = path.join(path.dirname(__file__), 'cards_lists.pickle')
    if not path.exists(pickle_file_path):
        generate_cards_from_csv(save_to_pickle=True)
    with open(pickle_file_path, 'rb') as f:
        cards_tuple = pickle.load(f)
    return cards_tuple