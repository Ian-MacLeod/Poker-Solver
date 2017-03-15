from collections import Counter, defaultdict, namedtuple
from itertools import islice
import random

RankCount = namedtuple("Rankcount", ["count", "rank"])
Card = namedtuple("Card", ["rank", "suit"])

SUITS = "shdc"
RANKS = "23456789TJQKA"
DECK = tuple(Card(rank, suit) for rank in range(13) for suit in range(4))


def make_hand(cards_str):
    return [make_card(s) for s in cards_str.split()]


def make_random_hand(hand_size=7):
    return random.sample(DECK, hand_size)


def make_card(s):
    return Card(rank=RANKS.index(s[0]), suit=SUITS.index(s[1]))


def get_kickers(cards, ignore=()):
    """
    Returns a generator of card ranks from high to low excluding card(s) having rank equal
    to any in ignore. Ignore can be an iterable or an integer.
    """
    # Assumes cards are sorted by rank from high to low
    if type(ignore) is int:
        ignore = (ignore,)
    return (card.rank for card in cards if card.rank not in ignore)


def get_straight(cards):
    """
    Checks to see if cards include a five card straight. If they do, returns the rank of
    the highest card in the highest straight; otherwise returns None.
    """
    # Assumes cards are sorted by rank from high to low
    last_rank = -1
    count = 1
    for rank in (card.rank for card in cards):
        if rank == last_rank - 1:
            if count == 4:
                return rank + 4
            count += 1
        elif rank != last_rank:
            count = 1
        last_rank = rank
    if count == 4 and last_rank == 0 and cards[0].rank == 12:
        return 3


def get_flush(cards):
    """
    Checks to see if the cards include a flush. If they do, returns a tuple containing the
    ranks of the highest five card flush; otherwise returns None.
    """
    # Assumes cards are sorted by rank from high to low
    by_suit = defaultdict(list)
    for card in cards:
        by_suit[card.suit].append(card.rank)
        if len(by_suit[card.suit]) == 5:
            return tuple(by_suit[card.suit])


def get_straightflush(cards):
    """
    Checks to see if the cards include a straight flush. If they do, returns the rank of
    the highest card in the highest straight flush; otherwise returns None.
    """
    # Assumes cards are sorted by rank from high to low
    possible = []
    for card in cards:
        for start in possible:
            if (card.suit, card.rank) == (start[-1].suit, start[-1].rank - 1):
                if len(start) == 4:
                    return start[0].rank
                start.append(card)
                break
        else:
            possible.append([card])
    for start in possible:
        if len(start) == 4 and start[-1].rank == 0:
            if Card(rank=12, suit=start[-1].suit) in cards:
                return 3


def evaluate_hand(cards):
    """
    Takes a List containing between 5 and 7 cards. Returns a tuple in the form
    (hand rank, kickers). If one hand is stronger than another, its return value will be
    greater if they are compared.
    """
    if len(cards) < 5 or len(cards) > 7:
        raise ValueError('Hand must have between 5 and 7 cards')
    cards = sorted(cards, key=lambda x: x.rank, reverse=True)

    flush = get_flush(cards)
    straight = get_straight(cards)
    if flush and straight:
        straightflush = get_straightflush(cards)
    else:
        straightflush = None
    rank_counts = Counter(card.rank for card in cards)
    rank_counts = [RankCount(count, item) for item, count in rank_counts.items()]
    rank_counts.sort(reverse=True)
    primary = rank_counts[0]
    secondary = rank_counts[1]

    if straightflush:
        hand_rank = 8
        kicker = straightflush
    elif primary.count == 4:
        hand_rank = 7
        kicker = (rank_counts[0].rank, next(get_kickers(cards, ignore=primary.rank)))
    elif primary.count == 3 and secondary.count >= 2:
        hand_rank = 6
        kicker = (primary.rank, secondary.rank)
    elif flush:
        hand_rank = 5
        kicker = flush
    elif straight:
        hand_rank = 4
        kicker = straight
    elif primary.count == 3:
        hand_rank = 3
        kicker = (primary.rank, *islice(get_kickers(cards, ignore=primary.rank), 2))
    elif primary.count == secondary.count == 2:
        hand_rank = 2
        extra_kicker = next(get_kickers(cards, ignore=(primary.rank, secondary.rank)))
        kicker = (primary.rank, secondary.rank, extra_kicker)
    elif primary.count == 2:
        hand_rank = 1
        extra_kickers = islice(get_kickers(cards, ignore=primary.rank), 3)
        kicker = (primary.rank, *extra_kickers)
    else:
        hand_rank = 0
        kicker = tuple(islice(get_kickers(cards), 5))
    return (hand_rank, kicker)


def calculate_river_equity(hand, villain_range, board):
    """
    Calculates the equity of a single hand against a weighted range of hands assuming that
    there are no cards to come.
    """
    if not set(hand).isdisjoint(board):
        return None
    my_hand_value = evaluate_hand(board + hand)
    lose = 0.0
    win = 0.0
    for villain_hand, weight in villain_range.items():
        if set(hand).isdisjoint(villain_hand) and set(villain_hand).isdisjoint(board):
            villain_hand_value = evaluate_hand(list(villain_hand) + board)
            if my_hand_value > villain_hand_value:
                win += weight
            elif my_hand_value < villain_hand_value:
                lose += weight
            else:
                win += weight / 2
                lose += weight / 2
    return win / (lose + win)
