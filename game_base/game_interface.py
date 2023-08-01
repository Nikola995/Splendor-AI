from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from itertools import combinations
from typing import Any, Tuple, Callable
from games import Game, GameState
from players import Player


@dataclass(slots=True)
class GameInterface(ABC):
    """Abstract class for an interface that can interact with a game"""
    game: Game = field(default_factory=Game)

    @abstractmethod
    def can_add_player(self, player: Player) -> bool:
        """Method for checking if a player can be added
        to the game before starting."""
        return self.game.can_add_player(player)

    @abstractmethod
    def add_player(self, player: Player) -> None:
        """Method for adding a player to the game before starting."""
        self.game.add_player(player)

    @abstractmethod
    def can_remove_player(self, player: Player) -> bool:
        """Method for checking if a player can be removed
        from the game before starting."""
        return self.game.can_remove_player(player)

    @abstractmethod
    def remove_player(self, player: Player) -> None:
        """Method for removing a player from the game before starting."""
        self.game.remove_player(player)

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
class GameInterfaceConsole(GameInterface):
    """An interface for playing a game using the console."""
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
            'add': Command(self.can_add_player, self.add_player,
                           "Adds a player to the game by the given name.",
                           1, ['Any Name']),
            'remove': Command(self.can_remove_player, self.remove_player,
                              "Removes a player from the game by the given name.",
                              1, [])
        }

    def show_game_meta_data(self) -> None:
        print("----------Game meta-data---------------")
        print(str(self.game.meta_data))
        if self.game.meta_data.state == GameState.IN_PROGRESS:
            print("Current player to move: "
                  f"{self.game.get_current_player().player_id}")

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

    def can_show_game_state_cmd(self, game_attr: str) -> bool:
        if game_attr == 'winner':
            return self.game.meta_data.state == GameState.FINISHED
        elif game_attr in ['nobles', 'cards', 'bank']:
            return self.game.meta_data.state != GameState.NOT_STARTED
        elif game_attr in ['all', 'meta', 'players']:
            return True
        else:
            return False

    def show_game_state_cmd(self, game_attr: str) -> None:
        match game_attr:
            case 'all': self.show_game_state()
            case 'meta': self.show_game_meta_data()
            case 'players': self.show_game_players()
            case 'nobles': self.show_game_nobles()
            case 'cards': self.show_game_cards_on_tables()
            case 'bank': self.show_game_bank()
            case 'winner': self.show_game_winner()
            case _: pass

    def can_add_player(self, player_name: str) -> bool:
        """Checks if a player by the given name
        can be added to the game."""
        return super().can_add_player(Player(player_name))

    def add_player(self, player_name: str) -> None:
        """Adds a player by the given name to the game."""
        self.commands['remove'].valid_parameters.append(player_name)
        return super().add_player(Player(player_name))

    def can_remove_player(self, player_name: str) -> bool:
        """Checks if a player by the given name
        can be removed from the game."""
        return super().can_remove_player(Player(player_name))

    def remove_player(self, player_name: str) -> None:
        """Removes a player by the given name from the game."""
        self.commands['remove'].valid_parameters.remove(player_name)
        return super().remove_player(Player(player_name))

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
                    print(f"{command}: {command.description}. "
                          f"Takes {command.num_parameters} "
                          "of the valid parameters as arguments.\n"
                          f"Current valid parameters: {params}")
            # If no parameters as input, only executable cmds
            elif command.can_execute_fn():
                print(f"{command}: {self.commands[command].description}")
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
        print("----------Welcome to Splendor----------"
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

        # if self.meta_data.state == GameState.NOT_STARTED:
        #     raise ValueError("Game can't run if not initialized")
        # if self.meta_data.state == GameState.FINISHED:
        #     raise ValueError("Game can't run if finished")
        # while (self.meta_data.state != GameState.FINISHED):
        #     for idx, player in enumerate(self.game.players):
        #         self.meta_data.curr_player_index = idx
        #         self.player_turn()


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
