import pytest
from dataclasses import FrozenInstanceError
from game_base.tokens import Token, TokenBag
from game_base.cards import (Card, CardManager,
                             CardManagerCollection, CardGenerator)


class TestingCard:
    def test_card_initialization(self) -> None:
        amounts = {Token.GREEN: 1,
                   Token.WHITE: 1,
                   Token.BLUE: 1}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        expected = {Token.GREEN: 1,
                    Token.WHITE: 1,
                    Token.BLUE: 1,
                    Token.BLACK: 0,
                    Token.RED: 0,
                    Token.YELLOW: 0}
        assert card.token_cost.tokens == expected
        assert card.level == 1
        assert card.prestige_points == 0
        assert card.bonus_color == Token.BLUE
        assert card.id == "11100"

    def test_card_initialization_error_wildcard_cost(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.YELLOW: 4}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_wildcard_bonus(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.BLUE: 4}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.YELLOW,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_negative_value(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.RED: -1}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_no_cost(self) -> None:
        amounts = {Token.GREEN: 0,
                   Token.RED: 0}
        with pytest.raises(ValueError) as e:
            card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_initialization_error_level(self) -> None:
        level = 4
        amounts = {Token.GREEN: 4,
                   Token.RED: 4}
        with pytest.raises(ValueError) as e:
            card = Card(level=level, prestige_points=0, bonus_color=Token.BLUE,
                        token_cost=TokenBag().add(amounts))

    def test_card_frozen_error_level(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        with pytest.raises(FrozenInstanceError) as e:
            card.level = 3

    def test_card_frozen_error_prestige_points(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        with pytest.raises(FrozenInstanceError) as e:
            card.prestige_points += 1

    def test_card_frozen_error_bonus_color(self) -> None:
        amounts = {Token.GREEN: 4,
                   Token.WHITE: 0,
                   Token.BLUE: 0,
                   Token.BLACK: 0,
                   Token.RED: 4}
        card = Card(level=1, prestige_points=0, bonus_color=Token.BLUE,
                    token_cost=TokenBag().add(amounts))
        with pytest.raises(FrozenInstanceError) as e:
            card.bonus_color = Token.GREEN

    def test_card_sort(self) -> None:
        # The amounts don't matter for sorting
        amounts = {Token.BLUE: 1,
                   Token.BLACK: 1,
                   Token.RED: 1}
        card_1 = Card(level=1, prestige_points=0, bonus_color=Token.GREEN,
                      token_cost=TokenBag().add(amounts))
        card_2 = Card(level=2, prestige_points=0, bonus_color=Token.GREEN,
                      token_cost=TokenBag().add(amounts))
        card_3 = Card(level=3, prestige_points=0, bonus_color=Token.GREEN,
                      token_cost=TokenBag().add(amounts))
        card_list = sorted([card_3, card_2, card_1])
        expected = [card_1, card_2, card_3]
        assert card_list == expected

    def test_card_str(self) -> None:
        amounts = {Token.BLUE: 1,
                   Token.BLACK: 1,
                   Token.RED: 1}
        card = Card(level=1, prestige_points=0, bonus_color=Token.GREEN,
                    token_cost=TokenBag().add(amounts))
        assert str(card) == ("Card 00111\n"
                             "Card Cost\n"
                             "Blue : 1\n"
                             "Black: 1\n"
                             "Red  : 1\n"
                             "Benefits of Purchasing Card\n"
                             "Prestige points: 0\n"
                             "Bonus token: Green")


class TestingCardManager:
    def card_list_for_testing(self, level: int = 1,
                              num_cards: int = 5) -> list[Card]:
        return [Card(level=level, prestige_points=0, bonus_color=Token.GREEN,
                     token_cost=TokenBag().add({Token.BLUE: i}))
                for i in range(1, num_cards + 1)]

    def test_card_manager_initialization(self) -> None:
        card_list = self.card_list_for_testing()
        card_manager = CardManager(card_list)
        assert card_manager.deck == card_list
        assert card_manager.card_level == 1
        assert len(card_manager.table) == card_manager.table_size
        assert card_manager.num_cards_on_table() == 0

    def test_card_manager_initialization_error_level(self) -> None:
        card_list = self.card_list_for_testing()
        card_list.append(Card(level=2, prestige_points=0,
                              bonus_color=Token.GREEN,
                              token_cost=TokenBag().add({Token.BLACK: 1})))
        with pytest.raises(ValueError) as e:
            card_manager = CardManager(card_list)

    def test_card_manager_sort(self) -> None:
        card_manager_1 = CardManager(self.card_list_for_testing(level=1))
        card_manager_2 = CardManager(self.card_list_for_testing(level=2))
        card_manager_3 = CardManager(self.card_list_for_testing(level=3))
        assert (sorted([card_manager_3, card_manager_2, card_manager_1]) ==
                [card_manager_1, card_manager_2, card_manager_3])

    def test_card_manager_fill_table_all(self) -> None:
        num_cards = 5
        card_list = self.card_list_for_testing(num_cards=num_cards)
        card_manager = CardManager(card_list)
        card_manager.fill_table()
        assert len(card_manager.deck) == num_cards - card_manager.table_size
        assert len(card_manager.table) == card_manager.table_size
        assert card_manager.num_cards_on_table() == card_manager.table_size

    def test_card_manager_fill_table_any(self) -> None:
        num_cards = 3
        card_list = self.card_list_for_testing(num_cards=num_cards)
        card_manager = CardManager(card_list)
        card_manager.fill_table()
        assert len(card_manager.deck) == max(num_cards -
                                             card_manager.table_size, 0)
        assert len(card_manager.table) == card_manager.table_size
        assert card_manager.num_cards_on_table() == num_cards

    def test_card_manager_fill_table_none(self) -> None:
        card_list = self.card_list_for_testing(num_cards=1)
        card_manager = CardManager(card_list)
        card_manager.deck.remove(card_list[0])
        card_manager.fill_table()
        assert len(card_manager.deck) == 0
        assert len(card_manager.table) == card_manager.table_size
        assert card_manager.num_cards_on_table() == 0

    def test_card_manager_remove_card_table_all(self) -> None:
        num_cards = 5
        card_list = self.card_list_for_testing(num_cards=num_cards)
        card_manager = CardManager(card_list)
        card_manager.fill_table()
        card_idx = 1
        card_to_remove = card_manager.table[card_idx]
        card_manager.remove_card_from_table(card_to_remove)
        assert len(card_manager.deck) == (num_cards -
                                          (card_manager.table_size + 1))
        assert len(card_manager.table) == card_manager.table_size
        assert card_manager.num_cards_on_table() == card_manager.table_size
        assert card_manager.table[card_idx] is not None

    def test_card_manager_remove_card_table_any(self) -> None:
        num_cards = 3
        card_list = self.card_list_for_testing(num_cards=num_cards)
        card_manager = CardManager(card_list)
        card_manager.fill_table()
        card_idx = 1
        card_to_remove = card_manager.table[card_idx]
        card_manager.remove_card_from_table(card_to_remove)
        assert len(card_manager.deck) == max((num_cards -
                                             (card_manager.table_size + 1)), 0)
        assert len(card_manager.table) == card_manager.table_size
        assert card_manager.num_cards_on_table() == num_cards - 1
        assert card_manager.table[card_idx] is None


class TestingCardManagerColletion:
    def test_card_manager_collection_initialization(self) -> None:
        assert False

    def test_card_manager_collection_get_manager(self) -> None:
        assert False

    def test_card_manager_collection_get_manager_error(self) -> None:
        assert False

    def test_card_manager_collection_get_deck(self) -> None:
        assert False

    def test_card_manager_collection_get_deck_error(self) -> None:
        assert False

    def test_card_manager_collection_get_table(self) -> None:
        assert False

    def test_card_manager_collection_get_table_error(self) -> None:
        assert False

    def test_card_manager_collection_get_all_decks(self) -> None:
        assert False

    def test_card_manager_collection_get_all_tables(self) -> None:
        assert False

    def test_card_manager_collection_get_all_cards_on_tables(self) -> None:
        assert False

    def test_card_manager_collection_is_card_in_tables_True(self) -> None:
        assert False

    def test_card_manager_collection_is_card_in_tables_False(self) -> None:
        assert False

    def test_card_manager_collection_shuffle_decks(self) -> None:
        # Copy of original deck & shuffled deck compare
        # same elements & not the same order
        assert False

    def test_card_manager_collection_fill_tables(self) -> None:
        # Check pre & post fill the len of the tables
        assert False


class TestingCardGenerator:
    def test_generate_from_csv(self) -> None:
        # Just check if it runs & type of output is correct
        assert False

    def test_generate_cards(self) -> None:
        # Check if the pkl file is made & correct type of output
        # If CardManagerColletion.shuffle_decks test works, don't test here
        assert False
