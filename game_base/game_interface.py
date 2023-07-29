from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any
from games import Game, GameState
from players import Player


@dataclass
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
    def show_game_state(self) -> Any:
        """Abstract method for showing the entire current state of the game."""
        # TODO: Return a numpy.matrix() for agent interface
        pass


@dataclass
class GameInterfaceConsole(GameInterface):
    """An interface for playing a game using the console."""

    def run(self) -> None:
        if self.meta_data.state == GameState.NOT_STARTED:
            raise ValueError("Game can't run if not initialized")
        if self.meta_data.state == GameState.FINISHED:
            raise ValueError("Game can't run if finished")
        while (self.meta_data.state != GameState.FINISHED):
            for idx, player in enumerate(self.game.players):
                self.meta_data.curr_player_index = idx
                self.player_turn()

    def show_game_meta_data(self) -> None:
        print("----------Game meta-data---------------")
        print(str(self.game.meta_data))

    def show_game_nobles(self) -> None:
        print("----------Available Nobles-------------")
        for noble in self.game.nobles:
            print("_______________________________________")
            print(str(noble))

    def show_game_bank(self) -> None:
        print("----------Bank-------------------------")
        print(str(self.game.bank))

    def show_game_players(self) -> None:
        print("----------Players----------------------")
        for player in self.game.players:
            print("_______________________________________")
            print(str(player))

    def show_game_state(self, dense=0) -> None:
        """Prints the state of the game on the console."""
        # dense - if true, return values as int (ex. player blue tokens = 5)
        # else return as sparse matrix (
        # (ex. player blue tokens = [1 1 1 1 1 0 0]))
        # print("----------G----------------------------")
        print("----------Complete game state----------")
        print("_______________________________________")
        self.show_game_meta_data()
        if self.game.meta_data.state == GameState.NOT_STARTED:
            return None
        self.show_game_nobles()
        self.show_game_bank()
        self.show_game_players()

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
