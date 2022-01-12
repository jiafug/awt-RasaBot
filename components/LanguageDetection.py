import os
import typing
from typing import Any, Dict, List, Optional, Text, Type

import joblib
import numpy as np
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

    def __init__(self,
                 component_config: Optional[Dict[Text, Any]] = None) -> None:
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
            pred = self.model.predict_proba([text]).flatten()
            language, confidence = MyComponent.get_info(pred)
            entity = [{
                'value': language,
                'confidence': float(confidence),
                'entity': 'language',
                'extractor:': 'language_extractor'
            }]
            message.set('entities',
                        message.get('entities', []) + entity,
                        add_to_output=True)

    @staticmethod
    def get_info(pred):
        _CLASSES = [
            "cdo", "glk", "jam", "lug", "san", "rue", "wol", "new", "mwl",
            "bre", "ara", "hye", "xmf", "ext", "cor", "yor", "div", "asm",
            "lat", "cym", "hif", "ace", "kbd", "tgk", "rus", "nso", "mya",
            "msa", "ava", "cbk", "urd", "deu", "swa", "pus", "bxr", "udm",
            "csb", "yid", "vro", "por", "pdc", "eng", "tha", "hat", "lmo",
            "pag", "jav", "chv", "nan", "sco", "kat", "bho", "bos", "kok",
            "oss", "mri", "fry", "cat", "azb", "kin", "hin", "sna", "dan",
            "egl", "mkd", "ron", "bul", "hrv", "som", "pam", "nav", "ksh",
            "nci", "khm", "sgs", "srn", "bar", "cos", "ckb", "pfl", "arz",
            "roa-tara", "fra", "mai", "zh-yue", "guj", "fin", "kir", "vol",
            "hau", "afr", "uig", "lao", "swe", "slv", "kor", "szl", "srp",
            "dty", "nrm", "dsb", "ind", "wln", "pnb", "ukr", "bpy", "vie",
            "tur", "aym", "lit", "zea", "pol", "est", "scn", "vls", "stq",
            "gag", "grn", "kaz", "ben", "pcd", "bjn", "krc", "amh", "diq",
            "ltz", "ita", "kab", "bel", "ang", "mhr", "che", "koi", "glv",
            "ido", "fao", "bak", "isl", "bcl", "tet", "jpn", "kur", "map-bms",
            "tyv", "olo", "arg", "ori", "lim", "tel", "lin", "roh", "sqi",
            "xho", "mlg", "fas", "hbs", "tam", "aze", "lad", "nob", "sin",
            "gla", "nap", "snd", "ast", "mal", "mdf", "tsn", "nds", "tgl",
            "nno", "sun", "lzh", "jbo", "crh", "pap", "oci", "hak", "uzb",
            "zho", "hsb", "sme", "mlt", "vep", "lez", "nld", "nds-nl", "mrj",
            "spa", "ceb", "ina", "heb", "hun", "que", "kaa", "mar", "vec",
            "frp", "ell", "sah", "eus", "ces", "slk", "chr", "lij", "nep",
            "srd", "ilo", "be-tarask", "bod", "orm", "war", "glg", "mon",
            "gle", "min", "ibo", "ile", "epo", "lav", "lrc", "als", "mzn",
            "rup", "fur", "tat", "myv", "pan", "ton", "kom", "wuu", "tcy",
            "tuk", "kan", "ltg"
        ]
        LABELS_STOI = {k: v for k, v in enumerate(_CLASSES)}
        LABELS_IOST = {v: k for k, v in enumerate(_CLASSES)}
        supported_lang = [
            "bos", "bul", "ces", "dan", "deu", "ell", "eng", "fra", "hrv",
            "ita", "lav", "nld", "pol", "por", "ron", "rus", "slk", "slv",
            "spa", "srp", "swe", "tur"
        ]
        lang_label = [LABELS_IOST[lang] for lang in supported_lang]
        lang_label.sort()
        idx_of_max = np.argmax(pred)
        val_of_max = np.amax(pred)
        language = LABELS_STOI[lang_label[idx_of_max]]
        confidence = val_of_max
        return language, confidence

    def persist(self, file_name: Text,
                model_dir: Text) -> Optional[Dict[Text, Any]]:
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
