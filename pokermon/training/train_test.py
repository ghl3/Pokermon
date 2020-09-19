from pokermon.model import heads_up
from pokermon.training import train


def test_heads_up():
    models = [heads_up.HeadsUpModel("Foo"), heads_up.HeadsUpModel("Bar")]
    train.train_heads_up(models, 2)
