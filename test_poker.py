import poker
import unittest


class TestPoker(unittest.TestCase):
    def setUp(self):
        self.straight_flush = poker.make_hand('4h 7h 6h 5h Ah 8h 9h')
        self.steel_wheel = poker.make_hand('2s As 3s 4s 5s 2h 2d')
        self.quads = poker.make_hand('5h 8h 8d 8c 8s 4d 4s')
        self.full_house = poker.make_hand('9d 8c 9c 2d Kc 2s 2c')
        self.extra_full_house = poker.make_hand('4c 5c 5d 5s Qc Qh Qs')
        self.flush = poker.make_hand('4s 5s 6s 8s Qc Qh Qs')
        self.straight = poker.make_hand('Ac Kc Qd 2h 6d Jc Tc')
        self.wheel = poker.make_hand('3h 7h Ad 2h Ac 4d 5d')
        self.trips = poker.make_hand('8h 7h 8d 2h 8c 4d 5d')
        self.two_pair = poker.make_hand('Jh Jd 8c 8s 2d 2c Kc')
        self.one_pair = poker.make_hand('Tc Td Qh Js 5d 4d 3d')
        self.high_card = poker.make_hand('3h Kd 5d 6s 9c Th 2c')
        self.five_cards_trips = poker.make_hand('Ac Ad As 4d 8c')
        self.four_cards = poker.make_hand('5h Th Tc As')
        self.eight_cards = poker.make_hand('5h Th Tc As 8d 8s 7c Kc')

        self.range1 = {tuple(poker.make_hand('As Ac')): 1,
                       tuple(poker.make_hand('5s 6s')): 2,
                       tuple(poker.make_hand('2s 2d')): 3}
        self.pocket_kings = poker.make_hand('Kc Kd')
        self.pocket_fives = poker.make_hand('5s 5d')
        self.board1 = poker.make_hand('3c 4c 7c Ks Td')

    def test_evaluate_hand(self):
        self.assertEqual(poker.evaluate_hand(self.straight_flush), (8, 7))
        self.assertEqual(poker.evaluate_hand(self.steel_wheel), (8, 3))
        self.assertEqual(poker.evaluate_hand(self.quads), (7, (6, 3)))
        self.assertEqual(poker.evaluate_hand(self.full_house), (6, (0, 7)))
        self.assertEqual(poker.evaluate_hand(self.extra_full_house), (6, (10, 3)))
        self.assertEqual(poker.evaluate_hand(self.flush), (5, (10, 6, 4, 3, 2)))
        self.assertEqual(poker.evaluate_hand(self.straight), (4, 12))
        self.assertEqual(poker.evaluate_hand(self.wheel), (4, 3))
        self.assertEqual(poker.evaluate_hand(self.trips), (3, (6, 5, 3)))
        self.assertEqual(poker.evaluate_hand(self.two_pair), (2, (9, 6, 11)))
        self.assertEqual(poker.evaluate_hand(self.one_pair), (1, (8, 10, 9, 3)))
        self.assertEqual(poker.evaluate_hand(self.high_card), (0, (11, 8, 7, 4, 3)))
        self.assertEqual(poker.evaluate_hand(self.five_cards_trips), (3, (12, 6, 2)))
        with self.assertRaises(ValueError):
            poker.evaluate_hand(self.four_cards)
        with self.assertRaises(ValueError):
            poker.evaluate_hand(self.eight_cards)

    def test_calculate_river_equity(self):
        equity = poker.calculate_river_equity(self.pocket_kings,
                                              self.range1,
                                              self.board1)
        self.assertEqual(equity, 2/3)

        equity = poker.calculate_river_equity(self.pocket_fives,
                                              self.range1,
                                              self.board1)
        self.assertEqual(equity, 3/4)


if __name__ == '__main__':
    unittest.main()
