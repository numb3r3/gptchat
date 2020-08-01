import os
import numpy as np
import random
import tensorflow as tf
import tensorflow.keras as keras
from envyaml import EnvYAML
from fastapi import FastAPI
from pydantic import BaseModel
import typing


def set_seed(seed):
    os.environ['PYTHONHASHSEED'] = '0'
    np.random.seed(seed)
    random.seed(seed)
    tf.random.set_seed(seed)


def load_yaml(path):
    """
    Args:
        path (str): File path of yaml configuration file
    Returns:
        Dict[str, Any]:
    """
    return EnvYAML(path, include_environment=False).export()


class WarmupScheduler(keras.callbacks.Callback):
    def __init__(self, warmup_steps, learning_rate):
        super().__init__()

        self._warmup_steps = warmup_steps
        self._learning_rate = learning_rate

        # The argument passed to on_train_batch_begin
        # is resetted every epoch.
        # self._total_steps is used to keep total step
        self._total_steps = 0

    def on_train_batch_begin(self, step, logs=None):
        self._total_steps += 1
        step = self._total_steps

        if step > self._warmup_steps:
            return

        # Get the current learning rate from model's optimizer.
        lr = float(keras.backend.get_value(self.model.optimizer.lr))
        # Call schedule function to get the scheduled learning rate.
        scheduled_lr = self._learning_rate * (step / self._warmup_steps)
        # Set the value back to the optimizer before this epoch starts
        keras.backend.set_value(self.model.optimizer.lr, scheduled_lr)
        #print('\nStep {}: lr is schedulerd {:.4e} -> {:.4e}]'.format(step, lr, float(tf.keras.backend.get_value(self.model.optimizer.lr))))


class Request(BaseModel):
    context: str
    response: str = None


class ModelInfo(BaseModel):
    output: typing.Any


class Response(BaseModel):
    response: str
    request: Request
    model_info: ModelInfo


def build_api(handler):
    app = FastAPI(
        title="GPTChat",
        description="",
        version="0.0.0",

    )
    app.add_api_route("/generate", handler.generate, methods=["POST"])
    return app

