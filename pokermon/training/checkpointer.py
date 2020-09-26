import dataclasses

import tensorflow as tf


@dataclasses.dataclass
class Checkpointer:

    model: tf.Module

    optimizer: tf.keras.optimizers.Optimizer

    directory: str

    max_to_keep: int = 5

    def __post_init__(self):

        self.checkpoint = tf.train.Checkpoint(
            model=self.model, optimizer=self.optimizer
        )

        self.manager = tf.train.CheckpointManager(
            self.checkpoint, self.directory, max_to_keep=self.max_to_keep
        )

    def latest_checkpoint(self):
        return self.manager.latest_checkpoint

    def save(self):
        self.manager.save()

    def restore(self):
        latest_checkpoint = self.manager.latest_checkpoint
        self.checkpoint.restore(latest_checkpoint)
