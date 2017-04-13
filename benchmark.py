import poker
import time
import cProfile

n = 10000
handlist = []
for i in range(n):
    handlist.append(poker.make_random_hand())


def temp(hands):
    for hand in hands:
        poker.evaluate_hand(hand)


cProfile.run('temp(handlist)')

cumtime = 0.0
for hand in handlist:
    start = time.time()
    poker.evaluate_hand(hand)
    cumtime += time.time() - start
print('Time to evaluate {} hands: {}'.format(n, cumtime))
print('Evaluations per second: {}'.format(n / cumtime))
