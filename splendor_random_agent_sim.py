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


def run_simulations(agent: Agent, num_agents: int = 4,
                    num_simulations: int = 100) -> list[tuple]:
    """Runs the given number of simulations of games with given number of 
    players with given Agent type.

    Returns:
        list[tuple]: Each tuple is the result from a simulated game.
    """
    return [simulate_game(agent=agent, num_players_in_game=num_agents)
            for _ in tqdm(range(num_simulations), unit=' games',
                          desc=f'Simulation for {num_agents} {agent}')]


def show_simulations_analysis(agent: Agent, num_agents: int = 4) -> None:
    simulations_df = (pd.read_csv(SIMULATIONS_PATH_CSV, header=0, index_col=0)
                      .query(f"Num_Players == {num_agents}"))
    num_simulations = simulations_df.shape[0]
    num_stalemates = simulations_df['Game_Ended'].value_counts()[False]
    num_turns_sum = simulations_df['Num_Turns'].sum()
    action_index_sum = simulations_df['Avg_Action_Idx'].sum()
    print(f"From {num_simulations} simulations using {num_agents} {agent}, "
          f"{num_stalemates} games were stalemated, or "
          f"{(num_stalemates * 100)/num_simulations:.2f}% of games")
    print(f"Games lasted on average {num_turns_sum/ num_simulations:.2f} "
          "turns")
    print("The actions chosen were on average the "
          f"{action_index_sum/num_simulations:.2f} legal move")


def main():
    num_simulations = 100
    num_agents = 4
    print(list(range(2, 5)))
    agent = Agent(RandomModel())
    simulation_results = run_simulations(agent, num_agents, num_simulations)
    (pd.DataFrame(simulation_results,
                  columns=['Game_Ended', 'Num_Turns', 'Avg_Action_Idx'])
     .assign(Num_Players=num_agents)
     .to_csv(SIMULATIONS_PATH_CSV))
    show_simulations_analysis(agent, num_agents)


if __name__ == '__main__':
    main()
