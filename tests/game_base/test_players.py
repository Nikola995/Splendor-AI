from game_base.tokens import TokenBag
from game_base.players import Player

def test_player_token_bag_initialization() -> None:
    empty_token_bag = TokenBag()
    player = Player('test_player')
    assert player.token_reserved.tokens == empty_token_bag.tokens