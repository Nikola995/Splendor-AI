from dataclasses import dataclass
from random import random


@dataclass
class RandomModel:
    output_size: int = 42

    def evaluate(self, game_state: list[int] = []) -> list[float]:
        return [random() for _ in range(self.output_size)]
    
    def __str__(self) -> str:
        return "Random Choice"
