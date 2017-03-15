import poker
import time
import cProfile

n = 10000
hands = []
for i in range(n):
    hands.append(poker.make_random_hand())


def temp(hands):
    for hand in hands:
        poker.evaluate_hand(hand)


cProfile.run('temp(hands)')

cumtime = 0.0
for hand in hands:
    start = time.time()
    poker.evaluate_hand(hand)
    cumtime += time.time() - start
print('Time to evaluate 10000 hands: {}'.format(cumtime))
print('Evaluations per second: {}'.format(n / cumtime))
