import os
import typing
from typing import Any, Dict, List, Optional, Text, Type

import joblib
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class MyComponent(Component):
    """A new component"""

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        return []

    defaults = {}
    supported_language_list = None
    not_supported_language_list = None
    
    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../notebooks/models/langdetect.pkl')
        self.model = joblib.load(filename)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def process(self, message: Message, **kwargs: Any) -> None:
        text = message.get('text')
        if text is not None:
            confidence = self.model.predict_proba([text]).flatten()[1]
            message.set('is_german_confidence', confidence, add_to_output=True)            

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""
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
        """Load this component from file."""
        if cached_component:
            return cached_component
        else:
            return cls(meta)
