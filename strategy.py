import poker


class StrategyTreeNode:
    def __init__(self, pot_size=None, c=None, r=None, f=None):
        self.pot_size = pot_size
        self.c = c
        self.r = r
        self.f = f
        self.range = poker.Range()

    def __repr__(self):
        return 'StrategyTreeNode(pot_size=' + str(self.pot_size) + ')'


class StrategyTree:
    def __init__(self, board, starting_pot_size, stack_size, bet_size):
        self.board = board
        self.plans = []
        self.starting_pot_size = starting_pot_size
        self.root = self._generate_tree(starting_pot_size, stack_size, bet_size)

    def amount_gained(self, pot_size):
        return (pot_size + self.starting_pot_size) / 2

    def amount_lost(self, pot_size):
        return (pot_size - self.starting_pot_size) / 2

    def get_plans(self, player):
        if player == 'ip':
            return [p for p in self.plans if len(p) % 2 == 0]
        else:
            return [p for p in self.plans if len(p) % 2 == 1]

    def create_node(self, plan, pot_size):
        node = StrategyTreeNode(pot_size)
        if plan[-1] == 'r':
            try:
                self.plans.remove(plan[:-1])
            except ValueError:
                pass
        self.plans.append(plan)
        return node

    def _generate_tree(self, starting_pot_size, stack_size, bet_size):
        root = StrategyTreeNode(starting_pot_size)
        root.r = self.create_node('r', starting_pot_size)
        root.c = self.create_node('c', starting_pot_size)
        root.c.r = self.create_node('cr', starting_pot_size)
        root.c.c = self.create_node('cc', starting_pot_size)
        expandable_nodes = [(root.r, 'r'), (root.c.r, 'cr')]
        while expandable_nodes:
            current, path = expandable_nodes.pop()
            current_pot_size = current.pot_size
            new_pot_size = current_pot_size * (1 + 2 * bet_size)
            current.f = self.create_node(path + 'f', current_pot_size)
            if (new_pot_size - starting_pot_size) / 2 >= stack_size:
                current.c = self.create_node(path + 'c',
                                             2 * stack_size + starting_pot_size)
            else:
                current.c = self.create_node(path + 'c', new_pot_size)
                current.r = self.create_node(path + 'r', new_pot_size)
                expandable_nodes.append((current.r, path + 'r'))
        return root

    def clear_ranges(self):
        frontier = [self.root]
        while frontier:
            current = frontier.pop()
            current.range = poker.Range()
            if current.f is not None:
                frontier.append(current.f)
            if current.c is not None:
                frontier.append(current.c)
            if current.r is not None:
                frontier.append(current.r)

    def modify_nodes_by_plan(self, plan, plan_range):
        current_node = self.root
        for action in plan:
            current_node = getattr(current_node, action)
            current_node.range += plan_range

    def create_counter_strategy(self, player, hand_range):
        # TODO: Assert opponent plans are filled in
        total_ev = 0
        if player == 'ip':
            for hand, weight in hand_range.items():
                ev_r, plan_r = self.get_highest_ev_plan(player, hand, self.root.r, 'r')
                ev_c, plan_c = self.get_highest_ev_plan(player, hand, self.root.c, 'c')
                total_ev += weight * (ev_r + ev_c)
        elif player == 'oop':
            for hand, weight in hand_range.items():
                ev_r, plan_r = self.get_highest_ev_plan(player, hand, self.root.r, 'r')
                ev_c, plan_c = self.get_highest_ev_plan(player, hand, self.root.c, 'c')
                total_ev += weight * max(ev_r, ev_c)
        else:
            raise ValueError("Player must be 'ip' or 'oop'")
        return total_ev

    def get_highest_ev_plan(self, player, hand, node, start_path):
        if player == 'ip':
            modval = 0
        elif player == 'oop':
            modval = 1
        else:
            raise ValueError("Player must be 'ip' or 'oop'")
        ev = 0
        max_ev = -1
        max_plan = None
        frontier = [(node, start_path)]
        while frontier:
            current, path = frontier.pop()
            if (len(path) % 2 == modval):
                if current.f is not None:
                    ev += (current.f.range.size(remove=hand)
                           * self.amount_gained(current.pot_size))
                equity = poker.equity_hand_vs_range(hand, current.c.range, self.board)
                ev += (current.c.range.size(remove=hand)
                       * (equity * current.c.pot_size
                          - self.amount_lost(current.c.pot_size)))
            else:
                equity = poker.equity_hand_vs_range(hand, current.range, self.board)
                plan_ev = (ev
                           + current.range.size(remove=hand)
                           * (equity
                              * current.c.pot_size
                              - self.amount_lost(current.c.pot_size)))
                if plan_ev > max_ev:
                    max_ev = plan_ev
                    max_plan = path + 'c'
                plan_ev = (ev
                           - current.range.size(remove=hand)
                           * self.amount_lost(current.pot_size))
                if plan_ev > max_ev:
                    max_ev = plan_ev
                    max_plan = path + 'f'
            if current.r is not None:
                frontier.append((current.r, path + 'r'))
            elif ev > max_ev:
                max_ev = ev
                max_plan = path
        return (max_ev, max_plan)

    def __repr__(self):
        result = ''
        frontier = [(self.root, '')]
        while frontier:
            current, path = frontier.pop()
            result += path + ': ' + str(current.range) + '\n'
            if current.f is not None:
                frontier.append((current.f, path + 'f'))
            if current.c is not None:
                frontier.append((current.c, path + 'c'))
            if current.r is not None:
                frontier.append((current.r, path + 'r'))
        return result
