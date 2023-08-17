from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from itertools import combinations
from typing import Any, Callable
from game_base.games import Game, GameState
from game_base.players import Player
from game_base.actions import (Action, ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from game_base.tokens import Token


@dataclass(slots=True)
class GameInterface(ABC):
    """Abstract class for an interface that can interact with a game"""
    game: Game = field(default_factory=Game)

    def can_add_player(self, player: Player) -> bool:
        """Method for checking if a player can be added
        to the game before starting."""
        return self.game.can_add_player(player)

    def add_player(self, player: Player) -> None:
        """Method for adding a player to the game before starting."""
        self.game.add_player(player)

    def can_remove_player(self, player: Player) -> bool:
        """Method for checking if a player can be removed
        from the game before starting."""
        return self.game.can_remove_player(player)

    def remove_player(self, player: Player) -> None:
        """Method for removing a player from the game before starting."""
        self.game.remove_player(player)

    def can_initialize(self) -> bool:
        """Checks if the game can be initialized."""
        return self.game.can_initialize()

    def initialize(self) -> None:
        """Initialize a new game for currently added players."""
        self.game.initialize()

    def can_make_move_for_current_player(self, action: Action) -> bool:
        """Checks if the given action can be performed for the current
        player's move.
        """
        return self.game.can_make_move_for_current_player(action)

    def make_move_for_current_player(self, action: Action) -> None:
        """Performs the given action as the player's move and iterate the
        current player index.
        """
        self.game.make_move_for_current_player(action)

    def get_winner(self) -> Player:
        """Gets the winner if the game is finished."""
        return self.game.get_winner()

    def new_game(self) -> None:
        """Starts a new game."""
        self.game = Game()

    @abstractmethod
    def run(self) -> None:
        """Abstract method for starting and playing a game until it is over."""
        pass

    @abstractmethod
    def show_game_state(self, dense: bool = True) -> Any:
        """Abstract method for showing the entire current state of the game."""
        # TODO: Return a numpy.matrix() for agent interface
        pass


@dataclass(slots=True)
class Command:
    """A representation of a command with its description
    and execution properties."""
    can_execute_fn: Callable[[], bool]
    execute_fn: Callable[[], None]
    description: str
    # If there are usecases with multiple num_params change to tuple[int]
    num_parameters: int = 0  # The number of required parameters of the command
    valid_parameters: list[str] = field(default_factory=list)

    def current_valid_parameters(self) -> set[str]:
        """Returns all of the valid paramaters for which the command
        can currently be executed.
        Unpacks all the parameters from an executable combination in a set."""
        return {parameters for combo
                in combinations(self.valid_parameters, self.num_parameters)
                if self.can_execute_fn(*combo) for parameters in combo}

    def execute(self, *args: list[str]) -> bool:
        """Executes the command if it can be executed.

        If the command can be executed (determined by its 'can_execute_fn'),
        the 'execute_fn' is called to perform the actual execution.

        Args:
            *args: Any number of arguments to be passed to the
            command execution function.

        Returns:
            bool: True if the command was executed successfully, False otherwise.
        """
        if len(args) != self.num_parameters:
            return False
        if self.can_execute_fn(*args):
            self.execute_fn(*args)
            return True
        return False


@dataclass(slots=True)
class CLI(GameInterface):
    """A control line interface for playing a game."""
    # All of the possible commands with their descriptions & executions
    commands: dict[str, Command] = field(default_factory=dict)

    def __post_init__(self):
        self.commands = {
            'exit': Command(lambda: True, self.exit_cmd,
                            "Exit the program."),
            'help': Command(lambda: True, self.show_help_cmd,
                            "Show all available commands and "
                            "their descriptions."),
            'show': Command(self.can_show_game_attr_cmd,
                            self.show_game_attr_cmd,
                            "Shows the state of the game.",
                            1, ['all', 'meta', 'players', 'nobles', 'cards',
                                'bank', 'winner']),
            'add': Command(self.can_add_player_cmd, self.add_player_cmd,
                           "Adds a player to the game by the given name.",
                           1, ['Any Name']),
            'remove': Command(self.can_remove_player_cmd,
                              self.remove_player_cmd,
                              "Removes a player from the game"
                              " by the given name.",
                              1, []),
            'start': Command(self.can_start_game_cmd, self.start_game_cmd,
                             "Starts the game."),
            'token3': Command(self.can_reserve_3_tokens_cmd,
                              self.reserve_3_tokens_cmd,
                              "Reserves 3 unique color tokens from the bank.",
                              3, ['green', 'white', 'blue', 'black', 'red']),
            'token2': Command(self.can_reserve_2_tokens_cmd,
                              self.reserve_2_tokens_cmd,
                              "Reserves 2 same color tokens from the bank.",
                              1, ['green', 'white', 'blue', 'black', 'red']),
            'res': Command(self.can_reserve_card_cmd, self.reserve_card_cmd,
                           "Reserves a card from the table.", 1, []),
            'buy': Command(self.can_purchase_card_cmd, self.purchase_card_cmd,
                           "Purchases a card from the table.", 1, []),
        }

    def show_game_meta_data(self) -> None:
        print("----------Game meta-data---------------")
        print(str(self.game.meta_data))
        if self.game.meta_data.state == GameState.IN_PROGRESS:
            print("Current player to move: "
                  f"{self.game.current_player.id}")

    def show_game_nobles(self) -> None:
        print("----------Available Nobles-------------")
        for noble in self.game.nobles:
            print("_______________________________________")
            print(str(noble))

    def show_game_cards_on_tables(self) -> None:
        print("----------Cards on Tables--------------")
        for card_level in range(1, 4):
            print("_______________________________________")
            print(f"----------Level {card_level}----------------------")
            for idx, card in enumerate(self.game.cards.get_table(card_level)):
                print(f"-- Card {idx} --")
                print(str(card))

    def show_game_bank(self) -> None:
        print("----------Bank-------------------------")
        print(str(self.game.bank))

    def show_game_players(self) -> None:
        print("----------Players----------------------")
        for player in self.game.players:
            print("_______________________________________")
            print(str(player))

    def show_game_winner(self) -> None:
        print("----------Winner-----------------------")
        print(str(self.game.get_winner()))

    def show_game_state(self, dense: bool = False) -> None:
        """Prints the state of the game on the console."""
        print("----------Complete game state----------")
        print("_______________________________________")
        self.show_game_meta_data()
        if self.game.meta_data.state == GameState.FINISHED:
            self.show_game_winner()
        self.show_game_players()
        if self.game.meta_data.state != GameState.NOT_STARTED:
            self.show_game_nobles()
            self.show_game_cards_on_tables()
            self.show_game_bank()

    def can_show_game_attr_cmd(self, game_attr: str) -> bool:
        if game_attr == 'winner':
            return self.game.meta_data.state == GameState.FINISHED
        elif game_attr in ['nobles', 'cards', 'bank']:
            return self.game.meta_data.state != GameState.NOT_STARTED
        elif game_attr in ['all', 'meta', 'players']:
            return True
        else:
            return False

    def show_game_attr_cmd(self, game_attr: str) -> None:
        match game_attr:
            case 'all': self.show_game_state()
            case 'meta': self.show_game_meta_data()
            case 'players': self.show_game_players()
            case 'nobles': self.show_game_nobles()
            case 'cards': self.show_game_cards_on_tables()
            case 'bank': self.show_game_bank()
            case 'winner': self.show_game_winner()
            case _: pass

    def can_add_player_cmd(self, player_name: str) -> bool:
        """Checks if a player by the given name
        can be added to the game."""
        return super(CLI, self).can_add_player(Player(player_name))

    def add_player_cmd(self, player_name: str) -> None:
        """Adds a player by the given name to the game."""
        self.commands['remove'].valid_parameters.append(player_name)
        super(CLI, self).add_player(Player(player_name))

    def can_remove_player_cmd(self, player_name: str) -> bool:
        """Checks if a player by the given name
        can be removed from the game."""
        return super(CLI, self).can_remove_player(Player(player_name))

    def remove_player_cmd(self, player_name: str) -> None:
        """Removes a player by the given name from the game."""
        self.commands['remove'].valid_parameters.remove(player_name)
        super(CLI, self).remove_player(Player(player_name))

    def can_start_game_cmd(self) -> bool:
        """Checks if the game can be started."""
        return super(CLI, self).can_initialize()

    def start_game_cmd(self) -> None:
        """Starts the game."""
        super(CLI, self).initialize()
        for card in self.game.cards.get_all_cards_on_tables():
            self.commands['res'].valid_parameters.append(card.id)
            self.commands['buy'].valid_parameters.append(card.id)

    def can_reserve_3_tokens_cmd(self, colors: tuple[Token]) -> bool:
        return (super(CLI, self)
                .can_make_move_for_current_player(
                    Reserve3UniqueColorTokens(colors)))

    def reserve_3_tokens_cmd(self, colors: tuple[Token]) -> None:
        (super(CLI, self)
         .make_move_for_current_player(
            Reserve3UniqueColorTokens(colors)))

    def can_reserve_2_tokens_cmd(self, color: Token) -> bool:
        return (super(CLI, self)
                .can_make_move_for_current_player(
                    Reserve2SameColorTokens(color)))

    def reserve_2_tokens_cmd(self, color: Token) -> None:
        (super(CLI, self)
         .can_make_move_for_current_player(
            Reserve2SameColorTokens(color)))

    def can_reserve_card_cmd(self, card_id: str) -> bool:
        card = self.game.get_card_by_id(card_id)
        return (super(CLI, self)
                .can_make_move_for_current_player(
                    ReserveCard(card)))

    def reserve_card_cmd(self, card_id: str) -> None:
        card = self.game.get_card_by_id(card_id)
        (super(CLI, self)
         .make_move_for_current_player(
            ReserveCard(card)))

    def can_purchase_card_cmd(self, card_id: str) -> bool:
        card = self.game.get_card_by_id(card_id)
        return (super(CLI, self)
                .can_make_move_for_current_player(
                    PurchaseCard(card)))

    def purchase_card_cmd(self, card_id: str) -> None:
        card = self.game.get_card_by_id(card_id)
        (super(CLI, self)
         .make_move_for_current_player(
            PurchaseCard(card)))

    def show_help_cmd(self) -> None:
        """Displays all currently available commands and their descriptions."""
        print("Available commands:")
        for command_name in self.commands:
            command = self.commands[command_name]
            # Iterate over all executable valid parameters if they exist
            if command.num_parameters:
                params = command.current_valid_parameters()
                # If there is at least one valid combination of params
                if params:
                    print(f"{command_name}: {command.description}\n"
                          f"\tTakes {command.num_parameters} "
                          "of the valid parameters as arguments.\n"
                          f"\tCurrent valid parameters: {params}")
            # If no parameters as input, only executable cmds
            elif command.can_execute_fn():
                print(f"{command_name}: "
                      f"{self.commands[command_name].description}")
            else:
                continue

    def exit_cmd(self) -> None:
        """Exits the program."""
        print("Exiting the program.")
        quit()

    def inexecutable_command(self) -> None:
        """Displays an error message for an inexecutable command."""
        print("Command cannot be executed. Please try another command.")

    def invalid_command(self) -> None:
        """Displays an error message for an invalid command."""
        print("Invalid command name and/or parameters. Please try again.")

    def run(self) -> None:
        """Runs the console interface, waiting for user input and executing
        commands accordingly."""
        print("----------Welcome to Splendor----------\n"
              "Add players before starting the game")
        while True:
            user_input = input("Enter your command "
                               "('help' to show all commands):\n")
            # Split the input into the command name & parameters
            user_cmd, *user_params = user_input.split(" ")
            command = self.commands.get(user_cmd)
            if command:
                if command.execute(*user_params):
                    continue
                else:
                    self.inexecutable_command()
            else:
                self.invalid_command()


@dataclass
class GameInterfaceAgents(GameInterface):
    """An interface for playing a game with agents."""

    def run(self) -> None:
        pass

    def show_game_meta_data(self) -> None:
        pass

    def show_game_nobles(self) -> None:
        pass

    def show_game_bank(self) -> None:
        pass

    def show_game_players(self) -> None:
        pass

    def show_game_cards_on_tables(self) -> None:
        pass

    def show_game_state(self, dense: bool = True) -> None:
        """Prints the state of the game on the console."""
        # TODO: implement dense & sparse matrix representations
        # Ex. dense
        # Player tokens: [1 3 0 0 0 0 2]
        # Ex. sparse
        # Player tokens:
        # [1 0 0 0 0 0 0]
        # [0 0 0 0 0 0 0]
        # [1 1 1 0 0 0 0]
        # [0 0 0 0 0 0 0]
        # [0 0 0 0 0 0 0]
        # [0 0 0 0 0 0 0]
        # [1 1 0 0 0 0 0]
        self.show_game_meta_data()
        self.show_game_nobles()
        self.show_game_bank()
        self.show_game_players()
        self.show_game_cards_on_tables()
