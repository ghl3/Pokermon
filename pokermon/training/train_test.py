from pokermon.model import heads_up
from pokermon.training import train


def test_heads_up():
    models = {"foo": heads_up.HeadsUpModel("Foo"), "bar": heads_up.HeadsUpModel("Bar")}
    train.train_heads_up(models, 2)
