import pytest
from game_base.cards import Card
from game_base.tokens import TokenBag, Token
from game_base.players import Player
from game_base.banks import Bank
from game_base.actions import (ReserveCard, PurchaseCard,
                               Reserve2SameColorTokens,
                               Reserve3UniqueColorTokens)
from tests.game_base.test_cards import TestingCardManager


class TestingReserve2SameColorTokens:
    def test_reserve_2_same_tokens(self) -> None:
        raise NotImplementedError


class TestingReserve3UniqueColorTokens:
    def test_reserve_3_unique_tokens(self) -> None:
        raise NotImplementedError


class TestingReserveCard:
    def test_reserve_card(self) -> None:
        raise NotImplementedError


class TestingPurchaseCard:
    def test_purchase_card(self) -> None:
        raise NotImplementedError
