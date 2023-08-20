from dataclasses import dataclass, field
from game_base.games import Game
from game_base.actions import Action
from game_base.action_sets import ActionSet, StandardActionSet
from typing import Optional, Protocol


class Model(Protocol):
    def evaluate(self, game_state: list[int] = []) -> list[int]:
        ...


@dataclass
class Agent:
    model: Model

    def get_action(self, game: Game) -> Optional[tuple[Action, int]]:
        """Returns the first legal action and its index in the order of the
        probability vector."""
        # np.argsort(probability_vector)
        probability_vector = self.model.evaluate(game.state_matrix())
        action_idxs = sorted(range(len(probability_vector)),
                             key=probability_vector.__getitem__,
                             reverse=True)
        for idx in action_idxs:
            action = game.possible_actions.get_action_by_idx(idx)
            if game.can_make_move_for_current_player(action):
                return (action, idx)
        return (None, -1)
    
    def __str__(self) -> str:
        return f"Agent with {self.model} model"
