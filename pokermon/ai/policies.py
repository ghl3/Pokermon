from pokermon.ai.human import Human
from pokermon.ai.random_policy import RandomPolicy

POLICIES = {'random': RandomPolicy(),
            'human': Human()}