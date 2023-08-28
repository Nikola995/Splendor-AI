from game_base.games import Game, GameState
from agents.agent import Agent
from agents.models import RandomModel
from game_base.players import Player
from pathlib import Path
import pandas as pd
from tqdm import tqdm


SIMULATIONS_PATH_CSV: Path = (Path(__file__).parent / 'data' / 'simulations' /
                              'random_choice.csv').resolve()


def simulate_game(agent: Agent, num_players_in_game: int = 4) -> bool:
    """Simulates an entire game of given number of players with given agent."""
    # TODO: Add logger for action choices
    players = [Player(f'random_{i + 1}') for i in range(num_players_in_game)]
    game = Game(players=players)
    game.initialize()
    idx_sum = 0
    while game.meta_data.state != GameState.FINISHED:
        action, idx = agent.get_action(game)
        idx_sum += idx
        if action is None:
            # print("There was no valid action")
            break
        # print(f"{agent} chose action {idx}: {action}")
        game.make_move_for_current_player(action)
    # if game.meta_data.state == GameState.FINISHED:
    #     print(f"The winner is {game.get_winner()}")
    num_moves = (game.meta_data.turns_played * num_players_in_game +
                 game.meta_data.curr_player_index)
    # Return (is_stalemate, num_turns, avg_action_idx)
    return (game.meta_data.state == GameState.FINISHED,
            game.meta_data.turns_played,
            (idx_sum/num_moves))


def main():
    num_simulations = 100
    num_agents = 4
    agent = Agent(RandomModel())
    simulation_results = []
    pbar = tqdm(desc='Simulated Games', unit=' games', initial=0,
                total=num_simulations, leave=False)
    for _ in range(num_simulations):
        simulation_result = simulate_game(agent=agent,
                                          num_players_in_game=num_agents)
        simulation_results.append(simulation_result)
        pbar.update(1)
    pbar.close()
    (pd.DataFrame(simulation_results,
                  columns=['Game_Ended', 'Num_Turns', 'Avg_Action_Idx'])
     .to_csv(SIMULATIONS_PATH_CSV))
    # print(f"From {num_simulations} simulations using {num_agents} {agent}, "
    #       f"{num_stalemates} games were stalemated, or "
    #       f"{(num_stalemates * 100)/num_simulations:.2f}% of games")
    # print(f"Games lasted on average {num_turns_sum/ num_simulations:.2f} "
    #       "turns")
    # print("The actions chosen were on average the "
    #       f"{action_index_sum/num_simulations:.2f} legal move")


if __name__ == '__main__':
    main()
