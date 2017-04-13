import strategy
import poker
from scipy.optimize import minimize
import numpy as np


class Solver:
    def __init__(self, board, hero_range, villain_range, hero='ip', bet_size=1,
                 stack_size=1, starting_pot_size=1):
        self.hero = hero
        self.villain = 'ip' if hero == 'oop' else 'oop'
        self.hero_range = hero_range
        self.villain_range = villain_range
        self.strategy_tree = strategy.StrategyTree(board, starting_pot_size, stack_size,
                                                   bet_size)

    def create_optimal_strategy(self):
        plans = self.strategy_tree.get_plans(self.hero)
        num_plans = len(self.strategy_tree.get_plans(self.hero))
        num_hands = len(self.hero_range.hand_weights)
        num_args = num_plans * num_hands
        initial_guess = np.zeros(num_args)
        constraints = []

        def make_sum_constraint(num_hands, hand_num, desired_total, start=None,
                                stop=None):
            def constraint(arr):
                nonlocal start
                nonlocal stop
                if start is None:
                    start = 0
                if stop is None:
                    stop = len(arr)
                total = 0
                for i in range(start, stop):
                    if i % num_hands == hand_num:
                        total += arr[i]
                return desired_total - total
            return constraint

        if self.hero == 'oop':
            for i, weight in enumerate(self.hero_range.hand_weights.values()):
                for j in range(num_plans):
                    initial_guess[i + j * num_hands] = weight / num_plans
                constraints.append({'type': 'eq',
                                    'fun': make_sum_constraint(num_hands, i, weight)})
        elif self.hero == 'ip':
            num_bet_plans = len([p for p in plans if p[0] == 'r'])
            for i, weight in enumerate(self.hero_range.hand_weights.values()):
                for j in range(num_bet_plans):
                    initial_guess[i + j * num_hands] = weight / num_bet_plans
                for j in range(num_bet_plans, num_plans):
                    initial_guess[i + j * num_hands] = (weight
                                                        / (num_plans - num_bet_plans))
                constraints.append(
                    {'type': 'eq',
                     'fun': make_sum_constraint(num_hands, i, weight, 0,
                                                num_bet_plans * num_hands)})
                constraints.append(
                    {'type': 'eq',
                     'fun': make_sum_constraint(num_hands, i, weight,
                                                num_bet_plans * num_hands, num_args)})

        bounds = [(0, None) for _ in range(num_args)]
        return minimize(self.evaluate_strategy, initial_guess, method='SLSQP',
                        bounds=bounds, constraints=constraints)

    def evaluate_strategy(self, arr):
        self.strategy_tree.clear_ranges()
        plans = self.strategy_tree.get_plans(self.hero)
        idx = 0

        for plan in plans:
            plan_range = poker.Range()
            for hand in self.hero_range.hand_weights:
                plan_range.hand_weights[hand] = arr[idx]
                idx += 1
            self.strategy_tree.modify_nodes_by_plan(plan, plan_range)
        return self.strategy_tree.create_counter_strategy(self.villain,
                                                          self.villain_range.hand_weights)
