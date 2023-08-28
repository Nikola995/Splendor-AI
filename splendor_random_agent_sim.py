from game_base.games import Game, GameState
from agents.agent import Agent
from agents.models import RandomModel
from game_base.players import Player
from tqdm import tqdm


def simulate_game(agent: Agent, num_players_in_game: int = 4) -> bool:
    """Simulates an entire game of given number of players with given agent."""
    # TODO: Add logger for action choices
    players = [Player(f'random_{i + 1}') for i in range(num_players_in_game)]
    game = Game(players=players)
    game.initialize()
    while game.meta_data.state != GameState.FINISHED:
        action, idx = agent.get_action(game)
        if action is None:
            # print("There was no valid action")
            break
        # print(f"{agent} chose action {idx}: {action}")
        game.make_move_for_current_player(action)
    # if game.meta_data.state == GameState.FINISHED:
    #     print(f"The winner is {game.get_winner()}")
    # TODO: Return is_stalemate, num_turns, avg_action_idx, 
    return game.meta_data.state == GameState.FINISHED


def main():
    num_simulations = 100_000
    agent = Agent(RandomModel())
    num_stalemates = 0
    for i in range(num_simulations):
        ended_game = simulate_game(agent=agent,
                                   num_players_in_game=4)
        if not ended_game:
            num_stalemates += 1
        # TODO: Use tqdm library
        print('\r'+f"Game {i} finished", end='\r')
    # TODO: Save data to data\simulations\random_choice.csv
    print(f"From {num_simulations} simulations using {agent}, "
          f"{num_stalemates} games were stalemated, or "
          f"{(num_stalemates * 100)/num_simulations: .2f}% of games")


if __name__ == '__main__':
    main()
