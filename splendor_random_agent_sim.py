from game_base.games import Game, GameState
from agents.agent import Agent
from agents.models import RandomModel
from game_base.players import Player

def simulate_game(num_players: int = 4) -> int:
    """Simulates an entire game with Random Choice Agents."""
    players = [Player(f'random_{i + 1}') for i in range(num_players)]
    game = Game(players=players)
    game.initialize()
    while game.meta_data.state != GameState.FINISHED:
        agent = Agent(RandomModel())
        action, idx = agent.get_action(game)
        if action is None:
            print("There was no valid action")
            break
        print(f"{agent} chose action {idx}: {action}")
        game.make_move_for_current_player(action)
    if game.meta_data.state == GameState.FINISHED:
        print(f"The winner is {game.get_winner()}")
    

def main():
    simulate_game(num_players=4)
    


if __name__ == '__main__':
    main()
