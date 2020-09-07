from pokermon.poker.cards import mkhand
from pokermon.poker.odds import odds_vs_random_hand


def test_aces():

    res = odds_vs_random_hand(hand=(mkhand("AcAd")))
    assert res.win_rate() > 0.80 and res.win_rate() < 0.90

    res = odds_vs_random_hand(hand=(mkhand("AsKd")))
    assert res.win_rate() > 0.60 and res.win_rate() < 0.70

    res = odds_vs_random_hand(hand=(mkhand("5h5d")))
    assert res.win_rate() > 0.55 and res.win_rate() < 0.65
