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
        print("Game meta-data"
              f"\nGame is {self.game.meta_data.state.name}"
              f"\nTurns played: {self.game.meta_data.turns_played}")
        if self.game.meta_data.state == GameState.IN_PROGRESS:
            print("Current player to move: "
                  f"{self.game.current_player().player_id}")
        
    def show_game_state(self, dense=0) -> None:
        """Return the state of the game."""
        # TODO implement a state representation
        # TODO add a game_id asset
        # This means also get state for players, bank, cards on table
        # dense - if true, return values as int (ex. player blue tokens = 5)
        # else return as sparse matrix (
        # (ex. player blue tokens = [1 1 1 1 1 0 0]))
        # verbose - print out the state in pretty string
        print('Current game state')
        self.show_game_meta_data()
        if self.game.meta_data.state == GameState.NOT_STARTED:
            return None
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
