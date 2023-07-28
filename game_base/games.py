from dataclasses import dataclass, field
from enum import Enum, auto
from random import shuffle
from itertools import combinations, product
from players import Player
from banks import Bank
from nobles import Noble, generate_nobles
from cards import Card, generate_cards_from_pickle
from actions import (Action, Reserve3DifferentColorTokens,
                     Reserve2SameColorTokens, ReserveCard,
                     PurchaseCard)
from utils import (TooManyPlayersError, NotEnoughPlayersError,
                   GameNotOverError, IncorrectInputError,
                   GameInitializedError)


@dataclass
class GameMechanicsStandard:
    # Game should have initialize after players are added
    # and then just run, where a GameMechanics instance processes turns until game is over
    pass


@dataclass
class GameState(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()


@dataclass
class Game:
    """A representation of the whole process of playing the game."""

    # %% Game Assets
    players: list[Player] = field(default_factory=list)
    # TODO Make the player order customizable - now it's FCFS
    bank: Bank = field(default_factory=Bank)
    # All of the cards not visible separated by level
    cards_deck_level_1: list[Card] = field(default_factory=list)
    cards_deck_level_2: list[Card] = field(default_factory=list)
    cards_deck_level_3: list[Card] = field(default_factory=list)
    # All of the cards visible separated by level
    cards_on_table_level_1: dict[str, Card] = field(default_factory=dict)
    cards_on_table_level_2: dict[str, Card] = field(default_factory=dict)
    cards_on_table_level_3: dict[str, Card] = field(default_factory=dict)
    # All the available nobles
    nobles: dict[str, Noble] = field(default_factory=dict)

    # TODO (after basic functionalities) create a game history record
    # Game information
    state: GameState = GameState.NOT_STARTED
    num_turns: int = 0
    curr_player_index: int = 0

    # %% Game initialization methods
    def add_player(self, player: Player) -> None:
        if self.state != GameState.NOT_STARTED:
            raise GameInitializedError("Players can only be added before "
                                       "the start of the game")
        if len(self.players) == 4:
            raise TooManyPlayersError("A game can't have more than 4 players")
        self.players.append(player)

    def remove_player(self, player: Player) -> None:
        if self.state != GameState.NOT_STARTED:
            raise GameInitializedError("Players can only be removed before "
                                       "the start of the game")
        self.players.remove(player)

    def _generate_nobles(self) -> None:
        """Generate and shuffle and pick the nobles for the game."""
        nobles_list = generate_nobles()
        shuffle(nobles_list)
        # Get n + 1 nobles for n players
        for index, noble in enumerate(nobles_list[0:len(self.players) + 1]):
            self.nobles[f'noble_{index}'] = noble

    def _generate_shuffle_cards(self, verbose=0) -> None:
        """Generate and shuffle the cards for the game."""
        # Import cards from pickle file (fastest)
        (self.cards_deck_level_1,
         self.cards_deck_level_2,
         self.cards_deck_level_3) = generate_cards_from_pickle()
        # Shuffle the decks
        shuffle(self.cards_deck_level_1)
        shuffle(self.cards_deck_level_2)
        shuffle(self.cards_deck_level_3)
        # Pop the last 4 cards of each deck and add them to the table
        for i in range(4):
            # generate a card id for all the popped cards
            c_id = f'card_{len(self.cards_deck_level_1)}'
            self.cards_on_table_level_1[c_id] = self.cards_deck_level_1.pop()
            c_id = f'card_{len(self.cards_deck_level_2) + 40}'
            self.cards_on_table_level_2[c_id] = self.cards_deck_level_2.pop()
            c_id = f'card_{len(self.cards_deck_level_3) + 70}'
            self.cards_on_table_level_3[c_id] = self.cards_deck_level_3.pop()
        if verbose == 1:
            print("Cards added, shuffled and 4 of each kind set on table")

    def initialize(self) -> None:
        """Initialize a new game for currently added players."""
        if len(self.players) < 2:
            raise NotEnoughPlayersError(
                "A game has to have at least 2 players")
        # Generate the game assets
        self.bank = Bank(num_players=len(self.players))
        self._generate_nobles()
        self._generate_shuffle_cards()

    # %% Active Game methods
    def is_game_over(self) -> bool:  # noqa : D301
        """Check if at least one of the players reached 15 prestige points.

        Called at the end of each turn \
        after all the players performed an action

        Returns
        -------
        Bool
            State of the game (is over or is still ongoing)
        """  # noqa : W605
        for player in self.players:
            if player.prestige_points >= 15:
                return True
        return False

    # TODO Switch from raising error if not over to return None
    def declare_winner(self) -> Player:
        """Declare the winner of the game, if it's over.

        If it's one player with >=15 prestige points, they are the winner.
        If it's multiple players with >= 15 prestige points,
        pick the one with the most prestige points.
        if there is still a tie, choose the one with
        the least number of owned development cards.

        Returns
        -------
        Player
            The winner of the game
        """
        if not self.is_over():
            # If the game is not over, don't declare a winner
            raise GameNotOverError("None of the players have 15 or more "
                                   "prestige points")
        winner = []
        # Get all the players with >= 15 prestige points
        for player in self.players:
            if player.prestige_points >= 15:
                winner.append(player)
        # If there's more than one sort by most prestige points, then by
        # least owned cards
        if len(winner) > 1:
            winner = sorted(winner, key=lambda x: (-x.prestige_points,
                                                   len(x.cards_owned)))
        # Return the winner
        return winner[0]

    def is_turn_over(self) -> bool:
        """Check if all of the players have made an action.

        The index of the player next to move has to be less then
        the number of players.

        Returns
        -------
        bool
            State of the turn (is over or is ongoing)
        """
        return self.curr_player_index >= self._num_players

    def end_turn(self, verbose=0) -> bool:
        """Reset the player move order and increment the number of turns."""
        if not self.is_turn_over():
            if verbose == 1:
                print("Turn is not over, there are still players to move")
            return False
        if verbose == 1:
            print(f"End of Turn {self.num_turns}")
        self.num_turns += 1
        self.curr_player_index = 0
        return True

    # TODO Add the usecase of multiple available nobles in one turn
    # Currently just returns the first one
    def noble_check_for_player(self, player: Player, verbose=0) -> bool:
        """Check all the available nobles if the player can own them."""
        # Assume bonuses were correctly added
        # (faster than going through the list of owned cards every time)
        for noble_id in self.nobles:
            noble = self.nobles[noble_id]
            if player.is_eligible_for_noble(noble, verbose):
                player.add_to_owned_nobles(self.nobles)
                self.nobles.pop(noble_id)
                return True
        return False

    def end_move_for_player(self, verbose=0) -> None:
        """End the player's move and do a noble check for them.

        Assume player has completed an action this turn.
        *Should only be called in succefully performed action methods
        in Game.
        """
        # Do a noble check for the player
        if self.noble_check_for_player(self.players[self.curr_player_index],
                                       verbose) and verbose == 1:
            print(f"{self.players[self.curr_player_index]} has gained a noble")
        if verbose == 1:
            print(f"{self.players[self.curr_player_index].player_id}'s "
                  "turn has ended")
        # End the turn for the player
        self.curr_player_index += 1

    def current_player_to_move(self, verbose=0) -> Player:
        """Return the current player to move.

        Returns
        -------
        Player
            Next player to perform an action (make a move)
        """
        if verbose == 1:
            print("Current player to move is "
                  f"{self.players[self.curr_player_index].player_id}")
        return self.players[self.curr_player_index]

    # %% Action-related methods
    def _find_card_on_table_by_id(self, card_id: str) -> Card:
        """Find card by id by searching all the cards on table."""
        if card_id in self.cards_on_table_level_1:
            card = self.cards_on_table_level_1[card_id]
        elif card_id in self.cards_on_table_level_2:
            card = self.cards_on_table_level_2[card_id]
        elif card_id in self.cards_on_table_level_3:
            card = self.cards_on_table_level_3[card_id]
        return card

    def _remove_card_on_table_by_id(self, card_id: str) -> bool:
        """Find card by id, remove from table and add new card from deck."""
        # Find the card level and get the deck and the cards on table
        if card_id in self.cards_on_table_level_1:
            cards_on_table = self.cards_on_table_level_1
            cards_deck = self.cards_deck_level_1
        elif card_id in self.cards_on_table_level_2:
            cards_on_table = self.cards_on_table_level_2
            cards_deck = self.cards_deck_level_2
        elif card_id in self.cards_on_table_level_3:
            cards_on_table = self.cards_on_table_level_3
            cards_deck = self.cards_deck_level_3
        # Remove card from table
        cards_on_table.pop(card_id)
        # Add the next card from the deck (if there is one)
        if len(cards_on_table) > 0:
            new_card_id = f'card_{len(cards_deck)}'
            cards_on_table[new_card_id] = cards_deck.pop()
        return True

    def perform_action_for_current_player(self, action: Action,
                                          verbose=0) -> bool:
        """Perform the given action for the current player to move.

        Parameters
        ----------
        action : Action
            The action to be performed with the initialized parameters.

        verbose : int
            If 1, will print output of the entire process,
            If 0, will print nothing.

        Returns
        -------
        bool
            Whether or not the action was performed succesfully
        """
        curr_player = self.current_player_to_move()
        if verbose == 1:
            print(f"Attemping to {action.print_string()} for "
                  f"{curr_player.player_id}")
        # If it's a card-related action, find the card by id
        # and set it as a parameter to the action
        if 'card_id' in action.params:
            card_id = action.params['card_id']
            if 'is_reserved' in action.params:
                is_reserved = action.params['is_reserved']
            else:
                is_reserved = False
            if is_reserved:
                card = curr_player.cards_reserved[card_id]
            else:
                card = self._find_card_on_table_by_id(card_id)

            action.params['card'] = card

        if action.can_perform(curr_player,
                              self.bank):
            action.perform(curr_player, self.bank, verbose)
            # If it's a card-related action, find the card by id
            # and remove it from the table (if it isn't reserved)
            if 'card_id' in action.params:
                if not is_reserved:
                    self._remove_card_on_table_by_id(card_id)
            # Action was completed, so end the player's move
            self.end_move_for_player(verbose)
            return True
        else:
            if verbose == 1:
                print("This action could not be performed")
            return False

    # %% Possible & Legal Actions
    def _all_possible_reserve_3_different_color_tokens(self) -> list[Action]:
        """Return all possible actions of this type."""
        current_actions_list = []
        # TODO Change to enum when refactoring
        colors = ["green", "white", "blue", "black", "red"]
        # All combinations of 3 different tokens
        for colors_combo_3 in combinations(colors, 3):
            current_actions_list.append(
                Reserve3DifferentColorTokens(params={'color_list':
                                                     list(colors_combo_3)}))
        return current_actions_list

    def _all_possible_reserve_2_same_color_tokens(self) -> list[Action]:
        """Return all possible actions of type Reserve2SameColorTokens."""
        current_actions_list = []
        # TODO Change to enum when refactoring
        colors = ["green", "white", "blue", "black", "red"]
        # All colors for 2 tokens
        current_actions_list = []
        for color in colors:
            current_actions_list.append(
                Reserve2SameColorTokens(params={'color': color}))
        return current_actions_list

    def _all_possible_reserve_card(self) -> list[Action]:
        """Return all possible actions of type ReserveCard."""
        # Reserving any card slot on table
        current_actions_list = []
        # TODO With fix with creating Table class, get card by
        # table index (ex level=1, card=4), not by generating card_id
# =============================================================================
#         for level in range(1, 4):
#             for index in range(4):
#                 current_actions_list.append(
#                     ReserveCard(params={'level': level, 'index': index}))
# =============================================================================
        for card_id in self.cards_on_table_level_1:
            current_actions_list.append(
                ReserveCard(params={'card_id': card_id}))
        for card_id in self.cards_on_table_level_2:
            current_actions_list.append(
                ReserveCard(params={'card_id': card_id}))
        for card_id in self.cards_on_table_level_3:
            current_actions_list.append(
                ReserveCard(params={'card_id': card_id}))
        return current_actions_list

    def _all_possible_purchase_card(self) -> list[Action]:
        """Return all possible actions of type PurchaseCard."""
        # Purchasing any slot on table with all combinations
        # of wildcard token
        current_actions_list = []
        # TODO Change to enum when refactoring
        colors = ["green", "white", "blue", "black", "red"]
        # TODO With fix with creating Table class, get card by
        # table index (ex level=1, card=4), not by generating card_id
# =============================================================================
#         for token_input in product(range(6), range(6), range(6),
#                                    range(6), range(6)):
#             if sum(token_input) <= 5:
#                 for level in range(1, 4):
#                     for index in range(4):
#                         current_actions_list.append(
#                             (purchase_a_card,
#                              {'level': level,
#                               'index': index,
#                               'yellow_replaces': {colors[0]: token_input[0],
#                                                   colors[1]: token_input[1],
#                                                   colors[2]: token_input[2],
#                                                   colors[3]: token_input[3],
#                                                   colors[4]: token_input[4]}}))
# =============================================================================
        curr_player = self.current_player_to_move()
        for token_input in product(range(6), range(6), range(6),
                                   range(6), range(6)):
            if sum(token_input) <= 5:
                yellow_replaces = {colors[0]: token_input[0],
                                   colors[1]: token_input[1],
                                   colors[2]: token_input[2],
                                   colors[3]: token_input[3],
                                   colors[4]: token_input[4]}
                for card_id in curr_player.cards_reserved:
                    card = curr_player.cards_reserved[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': True,
                                    'yellow_replaces': yellow_replaces}))
                for card_id in self.cards_on_table_level_1:
                    card = self.cards_on_table_level_1[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': False,
                                    'yellow_replaces': yellow_replaces}))
                for card_id in self.cards_on_table_level_2:
                    card = self.cards_on_table_level_2[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': False,
                                    'yellow_replaces': yellow_replaces}))
                for card_id in self.cards_on_table_level_3:
                    card = self.cards_on_table_level_3[card_id]
                    current_actions_list.append(
                        PurchaseCard(
                            params={'card': card,
                                    'card_id': card_id,
                                    'is_reserved': False,
                                    'yellow_replaces': yellow_replaces}))
        return current_actions_list

    def all_possible_actions(self) -> list[Action]:
        """Return all possible actions."""
        all_actions = {}
        # Reserve3DifferentColorTokens
        actions_list = self._all_possible_reserve_3_different_color_tokens()
        all_actions['reserve_3_different_color_tokens'] = actions_list
        # Reserve2SameColorTokens
        actions_list = self._all_possible_reserve_2_same_color_tokens()
        all_actions['reserve_2_same_color_tokens'] = actions_list
        # ReserveCard
        actions_list = self._all_possible_reserve_card()
        all_actions['reserve_card'] = actions_list
        # PurchaseCard
        actions_list = self._all_possible_purchase_card()
        all_actions['purchase_card'] = actions_list
        return all_actions

    def all_legal_actions_of_list(self,
                                  action_list: list[Action]) -> list[Action]:
        """Return all legal actions from given list of actions.

        These are calculated for the current player to move.
        Usually the list should be of one action type.
        """
        legal_action_list = []
        player = self.current_player_to_move()
        bank = self.bank
        for action in action_list:
            try:
                if action.can_perform(player, bank):
                    legal_action_list.append(action)
            except IncorrectInputError as e:
                continue
        return legal_action_list

    def all_legal_actions(self) -> list[Action]:
        """Return all legal actions from all possible actions.

        These are calculated for the current player to move.
        """
        all_legal_actions = {}
        all_actions = self.all_possible_actions()
        for action_type in all_actions:
            all_legal_actions[action_type] = self.all_legal_actions_of_list(
                all_actions[action_type])
        return all_legal_actions
    # %% Game state representation
    #            -> numpy.matrix():

    def state(self, dense=0, verbose=0):
        """Return the state of the game."""
        # TODO implement a state representation
        # TODO add a game_id asset
        # This means also get state for players, bank, cards on table
        # dense - if true, return values as int (ex. player blue tokens = 5)
        # else return as sparse matrix (
        # (ex. player blue tokens = [1 1 1 1 1 0 0]))
        # verbose - print out the state in pretty string
        if verbose == 1:
            # Print global game assets
            print('Current game state')
            print(f'\tCurrent turn: {self.num_turns}')
            print('\tCurrent player to move: '
                  f'{self.players[self.curr_player_index].player_id}')
            # Print bank
            print('\nBank tokens available:')
            print('Color\tAmount')
            for color in self.bank.token_available:
                print(f'{color:<5}\t{self.bank.token_available[color]}')
            # Print players
            print('\nPlayers stats')
            for player in self.players:
                print(f'{player.player_id}')
                print(f'Prestige points: {player.prestige_points}')
                print('Color\tReserved tokens\tOwned bonuses')
                for color in player.bonus_owned:
                    print(f'{color:<5}\t'
                          f'{player.token_reserved[color]:<15}\t'
                          f'{player.bonus_owned[color]}')
                print(f"yellow\t{player.token_reserved['yellow']}")
                if player.cards_reserved:
                    print('\nReserved cards:')
                    for card_id in player.cards_reserved:
                        card = player.cards_reserved[card_id]
                        print(f'{card_id:<6}\tLevel: {card.level}\t'
                              f'\nPrestige points: {card.prestige_points}'
                              f'\tBonus: {card.bonus_color}'
                              '\nToken cost:')
                        for color in card.token_cost:
                            if card.token_cost[color] > 0:
                                print(f'{color:<5}\t'
                                      f'{card.token_cost[color]}')
            print("\nCards on the Table")
            # Print all cards on the Table
            for card_id in self.cards_on_table_level_1:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_1[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}', end='\t')
                print('\n')
            for card_id in self.cards_on_table_level_2:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_2[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}', end='\t')
                print('\n')
            for card_id in self.cards_on_table_level_3:
                print("Card_id\tLevel\tBonus\tPrestige Points")
                card = self.cards_on_table_level_3[card_id]
                print(f'{card_id:<5}\t{card.level:<5}\t{card.bonus_color:<5}\t'
                      f'{card.prestige_points:<10}')
                print("Token cost:")
                print("Green\tWhite\tBlue\tBlack\tRed")
                for color in card.token_cost:
                    print(f'{card.token_cost[color]:<5}', end='\t')
                print('\n')
            # TODO Print Nobles
            print('\nNobles:')
            for noble_id in self.nobles:
                noble = self.nobles[noble_id]
                print('Noble_id\tPrestige Points')
                print(f'{noble_id:<5}\t{noble.prestige_points}')
                print("Bonuses required:")
                for color in noble.bonus_required:
                    if noble.bonus_required[color] > 0:
                        print(f'{color:<5}\t'
                              f'{noble.bonus_required[color]}')
                print('\n')

        return None
