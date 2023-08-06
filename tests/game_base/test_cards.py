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
    @staticmethod
    def card_list_for_testing(level: int = 1,
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
    @staticmethod
    def card_collection_for_testing() -> tuple[list[Card],
                                               list[Card],
                                               list[Card],
                                               CardManagerCollection]:
        cards_1 = TestingCardManager.card_list_for_testing(level=1)
        cards_2 = TestingCardManager.card_list_for_testing(level=2)
        cards_3 = TestingCardManager.card_list_for_testing(level=3)
        return (cards_1, cards_2, cards_3,
                CardManagerCollection(cards_1 + cards_2 + cards_3))

    def test_card_manager_collection_initialization(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        assert card_collection.managers == [CardManager(cards_1),
                                            CardManager(cards_2),
                                            CardManager(cards_3)]

    def test_card_manager_collection_get_manager(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        assert card_collection.get_manager(1) == CardManager(cards_1)
        assert card_collection.get_manager(2) == CardManager(cards_2)
        assert card_collection.get_manager(3) == CardManager(cards_3)

    def test_card_manager_collection_get_manager_error(self) -> None:
        _, _, _, card_collection = self.card_collection_for_testing()
        with pytest.raises(ValueError) as e:
            card_collection.get_manager(4)

    def test_card_manager_collection_get_deck(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        assert card_collection.get_deck(1) == cards_1
        assert card_collection.get_deck(2) == cards_2
        assert card_collection.get_deck(3) == cards_3

    def test_card_manager_collection_get_deck_error(self) -> None:
        _, _, _, card_collection = self.card_collection_for_testing()
        with pytest.raises(ValueError) as e:
            card_collection.get_deck(4)

    def test_card_manager_collection_get_table(self) -> None:
        _, _, _, card_collection = self.card_collection_for_testing()
        for i in range(1, 4):
            assert (card_collection.get_table(i) ==
                    [None] * card_collection.get_manager(i).table_size)
        assert card_collection.get_table(1) is not card_collection.get_table(2)
        assert card_collection.get_table(1) is not card_collection.get_table(3)
        assert card_collection.get_table(2) is not card_collection.get_table(3)

    def test_card_manager_collection_get_table_error(self) -> None:
        _, _, _, card_collection = self.card_collection_for_testing()
        with pytest.raises(ValueError) as e:
            card_collection.get_table(4)

    def test_card_manager_collection_get_all_decks(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        assert card_collection.get_all_decks() == [cards_1, cards_2, cards_3]

    def test_card_manager_collection_fill_tables(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        # Pre-fill asserts
        for i in range(1, 4):
            assert (card_collection.get_table(i) ==
                    [None] * card_collection.get_manager(i).table_size)
        assert card_collection.get_table(1) is not card_collection.get_table(2)
        assert card_collection.get_table(1) is not card_collection.get_table(3)
        assert card_collection.get_table(2) is not card_collection.get_table(3)
        card_collection.fill_tables()
        # Post-fill asserts
        # Do the same asserts for each table as in
        # TestingCardManager.test_card_manager_fill_table_all
        assert (len(card_collection.get_deck(1)) ==
                len(cards_1) - card_collection.get_manager(1).table_size)
        assert (len(card_collection.get_deck(2)) ==
                len(cards_2) - card_collection.get_manager(2).table_size)
        assert (len(card_collection.get_deck(3)) ==
                len(cards_3) - card_collection.get_manager(3).table_size)
        for i in range(1, 4):
            assert (len(card_collection.get_table(i)) ==
                    card_collection.get_manager(i).table_size)
            assert (card_collection.get_manager(i).num_cards_on_table() ==
                    card_collection.get_manager(i).table_size)
        # Assert the cards on the table are taken from the deck
        table_cards_1 = cards_1[-card_collection.get_manager(1).table_size:]
        table_cards_1.reverse()
        table_cards_2 = cards_2[-card_collection.get_manager(2).table_size:]
        table_cards_2.reverse()
        table_cards_3 = cards_3[-card_collection.get_manager(3).table_size:]
        table_cards_3.reverse()
        assert (card_collection.get_table(1) == table_cards_1)
        assert (card_collection.get_table(2) == table_cards_2)
        assert (card_collection.get_table(3) == table_cards_3)

    def test_card_manager_collection_get_all_tables(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        card_collection.fill_tables()
        table_cards_1 = cards_1[-card_collection.get_manager(1).table_size:]
        table_cards_1.reverse()
        table_cards_2 = cards_2[-card_collection.get_manager(2).table_size:]
        table_cards_2.reverse()
        table_cards_3 = cards_3[-card_collection.get_manager(3).table_size:]
        table_cards_3.reverse()
        assert (card_collection.get_all_tables() ==
                [table_cards_1, table_cards_2, table_cards_3])

    def test_card_manager_collection_get_all_cards_on_tables(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        card_collection.fill_tables()
        table_cards_1 = cards_1[-card_collection.get_manager(1).table_size:]
        table_cards_1.reverse()
        table_cards_2 = cards_2[-card_collection.get_manager(2).table_size:]
        table_cards_2.reverse()
        table_cards_3 = cards_3[-card_collection.get_manager(3).table_size:]
        table_cards_3.reverse()
        assert (card_collection.get_all_cards_on_tables() ==
                table_cards_1 + table_cards_2 + table_cards_3)

    def test_card_manager_collection_is_card_in_tables_True(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        card_collection.fill_tables()
        table_cards_1 = cards_1[-card_collection.get_manager(1).table_size:]
        table_cards_2 = cards_2[-card_collection.get_manager(2).table_size:]
        table_cards_3 = cards_3[-card_collection.get_manager(3).table_size:]
        for card in table_cards_1 + table_cards_2 + table_cards_3:
            assert card_collection.is_card_in_tables(card) == True

    def test_card_manager_collection_is_card_in_tables_False(self) -> None:
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        card_collection.fill_tables()
        deck_cards_1 = cards_1[:-card_collection.get_manager(1).table_size]
        deck_cards_2 = cards_2[:-card_collection.get_manager(2).table_size]
        deck_cards_3 = cards_3[:-card_collection.get_manager(3).table_size]
        for card in deck_cards_1 + deck_cards_2 + deck_cards_3:
            assert card_collection.is_card_in_tables(card) == False

    def test_card_manager_collection_shuffle_decks(self) -> None:
        # For each deck assert the same elements & not the same order
        (cards_1, cards_2, cards_3,
         card_collection) = self.card_collection_for_testing()
        card_collection.shuffle_decks()
        assert all(card in card_collection.get_deck(1) for card in cards_1)
        assert all(card in card_collection.get_deck(2) for card in cards_2)
        assert all(card in card_collection.get_deck(3) for card in cards_3)
        assert cards_1 != card_collection.get_deck(1)
        assert cards_2 != card_collection.get_deck(2)
        assert cards_3 != card_collection.get_deck(3)


class TestingCardGenerator:
    def test_generate_from_csv(self) -> None:
        # Just check if it runs & type of output is correct
        assert False

    def test_generate_cards(self) -> None:
        # Check if the pkl file is made & correct type of output
        # If CardManagerColletion.shuffle_decks test works, don't test here
        assert False
