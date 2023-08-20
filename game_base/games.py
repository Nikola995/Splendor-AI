from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from game_base.players import Player
from game_base.banks import Bank
from game_base.nobles import Noble, NobleGenerator
from game_base.cards import CardGenerator, CardManagerCollection
from game_base.actions import Action
from game_base.cards import Card
from game_base.action_sets import ActionSet, StandardActionSet


class GameState(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()

    def __str__(self) -> str:
        return f"{self.name.replace('_', ' ').lower()}"


@dataclass(slots=True)
class GameMetaData:
    # TODO add a game turn & moves record
    state: GameState = GameState.NOT_STARTED
    turns_played: int = 0
    curr_player_index: int = 0

    def change_game_state(self, new_state: GameState) -> None:
        """Changes the current state of the game."""
        if new_state == GameState.NOT_STARTED:
            raise ValueError("The game state is initialized to NOT_STARTED & "
                             "can't be changed to it")
        self.state = new_state

    def __str__(self) -> str:
        output = [f"Game is {self.state}",
                  f"Turns played: {self.turns_played}"]
        return "\n".join(output)


@dataclass(slots=True)
class Game:
    """A representation of the whole process of playing the game."""
    # Game information
    meta_data: GameMetaData = field(init=False)
    _MIN_PLAYERS = 2
    _MAX_PLAYERS = 4
    _WINNER_PRESTIGE_POINTS_THRESHOLD = 15
    # %% Game Assets
    players: list[Player] = field(default_factory=list)
    bank: Bank = field(init=False)
    nobles: list[Noble] = field(init=False)
    cards: CardManagerCollection = field(default_factory=lambda:
                                         (CardGenerator.generate_cards(shuffled=True)))
    possible_actions: ActionSet = field(default_factory=StandardActionSet)
    # %% Game properties

    @property
    def num_players(self) -> int:
        """The number of players currently in the game."""
        return len(self.players)

    @property
    def current_player_idx(self) -> int:
        """Return the current player index."""
        return self.meta_data.curr_player_index

    @property
    def current_player(self) -> Player:
        """Return the current player."""
        return self.players[self.current_player_idx]

    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """Returns the card from the table with the given id.
        (Used for human players.)
        """
        for card in self.cards.get_all_cards_on_tables():
            if card is not None and card.id == card_id:
                return card
        return None

    def get_card_by_idx(self, card_idx: int) -> Optional[Card]:
        """Returns the card from the table with the given index.
        (Used for agents.)
        """
        return self.cards.get_all_cards_on_tables()[card_idx]

    def __post_init__(self) -> None:
        if self.num_players > self._MAX_PLAYERS:
            raise ValueError("Game can't be initialized with "
                             f"{self.num_players} players")
        self.meta_data = GameMetaData()
        self.bank = None
        self.nobles = None
    # %% Game initialization methods

    def can_add_player(self, player: Player) -> bool:
        """Returns True if the game hasn't started,
        the number of players in game < max. number of players (4) and
        player is not in the game."""
        return (self.meta_data.state == GameState.NOT_STARTED and
                self.num_players < self._MAX_PLAYERS and
                player not in self.players)

    def add_player(self, player: Player) -> None:
        """Adds the given player to the game if the game has not started."""
        if not self.can_add_player(player):
            raise ValueError(f"Player {player.id} can't be added to the game.")
        self.players.append(player)

    def get_player_by_id(self, id: str) -> Optional[Player]:
        """Returns the player with the given id if they're in the game."""
        for player in self.players:
            if player.id == id:
                return player
        return None

    def can_remove_player(self, player: Player) -> bool:
        """Checks if the game hasn't started and
        the given player is in the game."""
        return (self.meta_data.state == GameState.NOT_STARTED and
                player in self.players)

    def remove_player(self, player: Player) -> None:
        """Removes the given player from the game
        if the game has not started."""
        if not self.can_remove_player(player):
            raise ValueError(f"Player {player.id} can't be removed from the "
                             "game.")
        self.players.remove(player)

    def change_player_order(self, new_order: list[int]) -> bool:
        """Changes the order of the players and returns whether the re-ordering
        was successful."""
        # TODO Implement this method
        raise NotImplementedError()

    def can_initialize(self) -> bool:
        """Checks if the game hasn't started and has at least 2 players."""
        return (self.meta_data.state == GameState.NOT_STARTED and
                self.num_players >= self._MIN_PLAYERS)

    def initialize(self) -> None:
        """Initialize a new game for currently added players."""
        if not self.can_initialize():
            raise ValueError("Game can't be initialized")
        # Generate the game assets
        self.bank = Bank(self.num_players)
        self.nobles = NobleGenerator.generate_nobles(self.num_players)
        self.meta_data.change_game_state(GameState.IN_PROGRESS)
        self.cards.fill_tables()
        self.possible_actions.update_card_actions(
            cards=self.cards.get_all_cards_on_tables(),
            player=self.current_player)

    # %% Active game methods
    def is_final_turn(self) -> bool:
        """Check if at least one of the players reached 15 prestige points.
        Called at the end of each turn."""
        return any([player.prestige_points >=
                    self._WINNER_PRESTIGE_POINTS_THRESHOLD
                    for player in self.players])

    def get_winner(self) -> Player:
        """Gets the winner if the game is finished.

        If there's more than one eligible player to win,
        sort by most prestige points, then least owned cards.
        (Sorting keys are implemented in the Player class)"""
        if self.meta_data.state != GameState.FINISHED:
            raise ValueError("Can't get winner because game isn't finished")
        eligible_players = [player for player in self.players
                            if player.prestige_points >= 15]
        # Return the winner
        return sorted(eligible_players, reverse=True)[0]

    def noble_check_for_current_player(self) -> None:
        """Automatically add a noble for the current player after their move.
        (Assumes the player is eligible.)"""
        # BUG: Usecase of multiple available nobles at the same time.
        for noble in self.nobles:
            if self.current_player.is_eligible_for_noble(noble):
                self.current_player.add_noble(noble)
                self.nobles.remove(noble)
                break

    def _end_player_turn(self) -> None:
        """Updates everything turn-related automatically after player
        performs an action."""
        # If all the players made their turn
        if self.current_player_idx + 1 == self.num_players:
            if self.is_final_turn():
                # End the game if it is the final turn
                self.meta_data.change_game_state(GameState.FINISHED)
            # Update the meta-data for the finished turn
            self.meta_data.turns_played += 1
            self.meta_data.curr_player_index = 0
        else:
            # Continue the game with the next player to move
            self.meta_data.curr_player_index += 1

    def can_make_move_for_current_player(self, action: Action) -> bool:
        """Checks if the given action can be performed for the current
        player's move.
        """
        if hasattr(action, 'card'):
            if ((action.card not in self.cards.get_all_cards_on_tables() and
                 action.card not in self.current_player.cards_reserved) or
                    action.card is None):
                return False
        return (self.meta_data.state == GameState.IN_PROGRESS and
                action.can_perform(self.current_player, self.bank))

    def all_actions_legality(self) -> list[bool]:
        """Returns the legality of all possible actions in
        the current game state."""
        return [self.can_make_move_for_current_player(action)
                for action in self.possible_actions.all_actions()]

    def make_move_for_current_player(self, action: Action) -> None:
        """Performs the given action as the player's move and iterate the
        current player index.
        (Automatically makes the noble check after the action is performed.)
        """
        if not self.can_make_move_for_current_player(action):
            raise ValueError(f"Player {self.current_player.id} can't {action}")
        action.perform(player=self.current_player, bank=self.bank)
        self.noble_check_for_current_player()
        self._end_player_turn()
        # If action with card wasn't purchasing a reserved card.
        if hasattr(action, 'card'):
            if self.cards.is_card_in_tables(action.card):
                self.cards.remove_card_from_tables(action.card)
            self.possible_actions.update_card_actions(
                cards=self.cards.get_all_cards_on_tables(),
                player=self.current_player)

    # %% Game state representation

    def state_matrix(self, dense: bool = True) -> list[int]:
        """Returns the entire game state information in matrix form."""
        # TODO: fill the matrix
        return []
