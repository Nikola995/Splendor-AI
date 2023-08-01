from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Tuple, Callable
from games import Game, GameState
from players import Player


@dataclass(slots=True)
class GameInterface(ABC):
    """Abstract class for an interface that can interact with a game"""
    game: Game = field(default_factory=Game)

    def add_player(self, player: Player) -> None:
        """Method for adding a player to the game before starting."""
        self.game.add_player(player)

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

    def execute(self) -> bool:
        """Executes the command if it can be executed.

        If the command can be executed (determined by its 'can_execute_fn'),
        the 'execute_fn' is called to perform the actual execution.

        Returns:
            bool: True if the command was executed successfully, False otherwise.
        """
        if self.can_execute_fn():
            self.execute_fn()
            return True
        return False


@dataclass(slots=True)
class GameInterfaceConsole(GameInterface):
    """An interface for playing a game using the console."""
    # All of the possible commands with their descriptions & executions
    commands: dict[str, Command] = field(default_factory=dict)

    def __post_init__(self):
        self.commands = {
            'exit': Command(lambda: True, self.exit,
                            "Exit the program."),
            'help': Command(lambda: True, self.show_help,
                            "Show all available commands and "
                            "their descriptions.")

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

    def show_winner(self) -> None:
        print("----------Winner-----------------------")
        print(str(self.game.get_winner()))

    def show_game_state(self, dense: bool = False) -> None:
        """Prints the state of the game on the console."""
        print("----------Complete game state----------")
        print("_______________________________________")
        self.show_game_meta_data()
        if self.game.meta_data.state == GameState.NOT_STARTED:
            return None
        self.show_game_nobles()
        self.show_game_cards_on_tables()
        self.show_game_bank()
        self.show_game_players()
        if self.game.meta_data.state == GameState.FINISHED:
            self.show_winner()

    def show_help(self) -> None:
        """Displays all currently available commands and their descriptions."""
        print("Available commands:")
        for command in self.commands:
            if self.commands[command].can_execute_fn():
                print(f"{command}: {self.commands[command].description}")

    def exit(self) -> None:
        """Exits the program."""
        print("Exiting the program.")
        quit()

    def inexecutable_command(self) -> None:
        """Displays an error message for an inexecutable command."""
        print("Command cannot be executed. Please try another command.")

    def invalid_command(self) -> None:
        """Displays an error message for an invalid command."""
        print("Invalid command. Please try again.")

    def run(self) -> None:
        """Runs the console interface, waiting for user input and executing
        commands accordingly."""
        print("----------Welcome to Splendor----------"
              "Add players before starting the game")
        while True:
            user_input = input("Enter your command "
                               "('help' to show all commands):\n")
            command = self.commands.get(user_input)
            if command:
                if command.execute():
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
