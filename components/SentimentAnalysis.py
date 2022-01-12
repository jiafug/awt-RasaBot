import os
import typing
from typing import Any, Dict, List, Optional, Text, Type

import numpy as np
import torch
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

from .FastText import FastText

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class MyComponent(Component):

    defaults = {}
    supported_language_list = None
    not_supported_language_list = None

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        return []

    def __init__(self,
                 component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        dirname = os.path.dirname(__file__)
        model_path = os.path.join(
            dirname, '../notebooks/models/fasttext-v2-model-100.pt')
        vocab_path = os.path.join(
            dirname, '../notebooks/models/fasttext-v2-vocab-100.pt')
        self.vocab = torch.load(vocab_path)
        self.model = FastText(3, 100002, 300, 10, 1)
        self.model.load_state_dict(
            torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def process(self, message: Message, **kwargs: Any) -> None:
        text = message.get('text_tokens')
        if text is not None:
            tok_list = []
            for tok in text:
                tok_list.append(tok.text)
            pred = self.model.predict_sentiment(self.model, self.vocab,
                                                tok_list)
            np_array = pred.flatten().detach().numpy()
            val_of_max = np.amax(np_array)
            idx_of_max = np.argmax(np_array)
            if idx_of_max == 0:
                senti = "positive"
            elif idx_of_max == 1:
                senti = "negative"
            else:
                senti = "neutral"
            entity = [{
                'value': senti,
                'confidence': str(val_of_max),
                'entity': 'sentiment',
                'extractor:': 'sentiment_extractor'
            }]
            message.set('entities',
                        message.get('entities', []) + entity,
                        add_to_output=True)

    def persist(self, file_name: Text,
                model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        if cached_component:
            return cached_component
        else:
            return cls(meta)
