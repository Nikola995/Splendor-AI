# %% Game entity errors
class IncorrectInputError(Exception):
    pass


class TokenThresholdError(Exception):
    pass


class TooManyTokensForPlayerError(Exception):
    pass


# %% Action errors
class ActionNotPossibleError(Exception):
    pass


# %% Game errors
class NotEnoughPlayersError(Exception):
    pass


class TooManyPlayersError(Exception):
    pass


class GameInitializedError(Exception):
    pass


class GameNotOverError(Exception):
    pass


class TurnNotOverError(Exception):
    pass
