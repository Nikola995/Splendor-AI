from dataclasses import dataclass, field
from enum import Enum, auto
from players import Player
from banks import Bank
from nobles import Noble, NobleGenerator
from cards import CardGenerator, CardManagerCollection
from actions import Action
from action_sets import ActionSet, StandardActionSet
from utils import (GameInitializedError)


class GameState(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()


@dataclass(slots=True)
class GameMetaData:
    state: GameState = GameState.NOT_STARTED
    turns_played: int = 0
    curr_player_index: int = 0

    def change_game_state(self, new_state: GameState) -> None:
        """Changes the current state of the game."""
        if new_state == GameState.NOT_STARTED:
            raise ValueError("Game can't be changed to NOT_STARTED")
        self.state = new_state

    def __str__(self) -> str:
        output = [f"Game is {self.game.meta_data.state.name}",
                  f"Turns played: {self.game.meta_data.turns_played}"]
        if self.game.meta_data.state == GameState.IN_PROGRESS:
            output.append("Current player to move: "
                          f"{self.game.current_player().player_id}")
        return "\n".join(output)


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
        if self.meta_data.state != GameState.NOT_STARTED:
            raise GameInitializedError("Players can only be added before "
                                       "the start of the game")
        if len(self.players) == 4:
            raise ValueError("A game can't have more than 4 players")
        self.players.append(player)

    def remove_player(self, player: Player) -> None:
        if self.meta_data.state != GameState.NOT_STARTED:
            raise GameInitializedError("Players can only be removed before "
                                       "the start of the game")
        self.players.remove(player)

    # TODO Add customizable player order pre-initialization - now only FCFS
    def initialize(self) -> None:
        """Initialize a new game for currently added players."""
        if len(self.players) < 2:
            raise ValueError("A game can't begin without at least 2 players")
        # Generate the game assets
        self.bank = Bank(num_players=len(self.players))
        self.nobles = NobleGenerator.generate_nobles(len(self.players))
        self.meta_data.change_game_state(GameState.IN_PROGRESS)

    # %% Active game methods
    def is_final_turn(self) -> bool:
        """Check if at least one of the players reached 15 prestige points.
        Called at the end of each turn."""
        for player in self.players:
            if player.prestige_points >= 15:
                return True
        return False

    def declare_winner(self) -> Player:
        """Declares the winner of the finished game."""
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
            self.meta_data.change_game_state(GameState.FINISHED)
        else:
            # Continue the game for another turn
            self.meta_data.turns_played += 1
            self.meta_data.curr_player_index = 0

    def current_player(self) -> Player:
        """Return the current player."""
        return self.players[self.meta_data.curr_player_index]

    def noble_check_for_current_player(self) -> None:
        """Automatically add a noble for the current player after their move.
        (Assumes the player is eligible.)"""
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
