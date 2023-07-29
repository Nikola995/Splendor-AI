from dataclasses import dataclass, field
from enum import Enum, auto
from players import Player
from banks import Bank
from nobles import Noble, NobleGenerator
from cards import Card, CardGenerator, CardManagerCollection
from actions import Action
from action_sets import ActionSet, StandardActionSet
from utils import (TooManyPlayersError, NotEnoughPlayersError,
                   GameNotOverError, GameInitializedError)


class GameState(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()


@dataclass(slots=True)
class GameMetaData:
    state: GameState = GameState.NOT_STARTED
    curr_turn: int = 0
    curr_player_index: int = 0

    def change_game_state(self, new_state: GameState) -> None:
        """Changes the current state of the game."""
        match new_state:
            case GameState.NOT_STARTED:
                raise ValueError("Game should have been initialized as "
                                 "NOT_STARTED")
            case GameState.IN_PROGRESS:
                self.state = new_state
                self.curr_turn = 1
            case GameState.FINISHED:
                self.state = new_state


@dataclass(slots=True)
class Game:
    """A representation of the whole process of playing the game."""
    # TODO add a game turn & moves record
    # Game information
    meta_data: GameMetaData = field(default_factory=GameMetaData)
    # %% Game Assets
    players: list[Player] = field(default_factory=list)
    bank: Bank = field(default_factory=None)
    cards: CardManagerCollection = field(default_factory=lambda:
                                         (CardGenerator.generate_cards(shuffled=True)))
    nobles: list[Noble] = field(default_factory=list)
    actions: ActionSet = field(default_factory=StandardActionSet)
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

    # TODO Add customizable player order pre-initialization - now only FCFS
    def initialize(self) -> None:
        """Initialize a new game for currently added players."""
        if len(self.players) < 2:
            raise NotEnoughPlayersError(
                "A game has to have at least 2 players")
        # Generate the game assets
        self.bank = Bank(num_players=len(self.players))
        self.nobles = NobleGenerator.generate_nobles(len(self.players))
        self.meta_data.change_game_state(GameState.IN_PROGRESS)

    # %% Active game methods

    def is_final_turn(self) -> bool:
        """Check if at least one of the players reached 15 prestige points.
        Called at the end of each turn.
        """
        for player in self.players:
            if player.prestige_points >= 15:
                return True
        return False

    def declare_winner(self) -> Player:
        """Declares the winner of the finished game.
        """
        if self.meta_data.state != GameState.FINISHED:
            raise ValueError("Game hasn't finished")
        eligible_players = [player for player in self.players
                            if player.prestige_points >= 15]
        # If there's more than one eligible players,
        # sort by most prestige points, then least owned cards
        if len(eligible_players) > 1:
            eligible_players = sorted(eligible_players,
                                      key=lambda x: (-x.prestige_points,
                                                     len(x.cards_owned)))
        # Return the winner
        return eligible_players[0]

    def end_turn(self) -> None:
        """Ends the current turn."""
        if self.meta_data.curr_player_index < len(self.players) - 1:
            raise ValueError("Turn isn't over, all of the players haven't "
                             "made a move")
        if self.is_final_turn():
            # End the game if it is the final turn
            self.meta_data.state = GameState.FINISHED
        else:
            # Continue the game for another turn
            self.meta_data.curr_turn += 1
            self.meta_data.curr_player_index = 0

    def current_player(self) -> Player:
        """Return the current player.
        """
        return self.players[self.meta_data.curr_player_index]

    def noble_check_for_current_player(self) -> None:
        """Automatically add a noble for the current player after their move.
        (Assumes the player is eligible.)
        """
        # TODO: Add the usecase of multiple available nobles in one turn
        # # Currently just returns the first one
        for noble in self.nobles:
            if self.current_player().is_eligible_for_noble(noble):
                self.current_player().add_noble(noble)
                self.nobles.pop(noble)
                break

    def make_move_for_current_player(self, action: Action, **kwargs) -> None:
        """Performs the given action as the player's move and iterate the
        current player index.
        (Allows **kwargs for action.)
        (Automatically makes the noble check after the action is performed.)
        """
        if not action.can_perform(self.current_player(), self.bank):
            raise ValueError(f"Player can't perform {action}")
        action.perform(player=self.current_player(), bank=self.bank, **kwargs)
        # If action with card wasn't purchasing a reserved card.
        if hasattr(action, 'card'):
            if self.cards.is_card_in_tables(action.card):
                self.cards.remove_card_from_tables(action.card)
        self.noble_check_for_current_player()
        # End the turn for the player
        self.meta_data.curr_player_index += 1

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
