# Project Advanced Web Technologies WS 21/22 (Chatbot-Semantics: User Input Analysis)

[TOC]

## Setup

### Install the dependencies

In a Python3 virtual environment run:

```
pip3 install -r requirements.txt
```

### Download pre-trained models for custom components

Download the following files and place them in the `/notebooks/models/` folder:

| File                | Link                                                              |     Size |
| ------------------- | ----------------------------------------------------------------- | -------: |
| FastText Model      | https://drive.google.com/file/d/1Q3Zu2ddgXeLIbxM0WjjgQwIsXCW5NH7s | 114.5 MB |
| Vocabulary          | https://drive.google.com/file/d/1wkfO-so2vna0vg8uASUVaZHh88g0vNfE | 397.3 MB |
| Language Classifier | https://drive.google.com/file/d/1_0dCbLozOocyQDWzZLI3WGG-RBDkc7Y2 |  20.6 MB |

## Running the bot

### Development

start Rasa actions server:

```
python -m rasa_sdk.endpoint --actions actions
```

start Rasa X:

```
rasa x
```

### Production

start Rasa actions server:

```
python -m rasa_sdk.endpoint --actions actions
```

start Rasa server:

```
rasa run --enable-api --auth-token pass --cors "*"
```

open simple web GUI located in the following location:

```
/web/index.html
```

## Overview of the files

- `/actions/actions.py` - contains custom action/api code
- `/components/*` - contains custom NLU components (i.e. sentiment analysis & language detection)
- `/data/core/*` -  contains rules and stories training data
- `/data/nlu/*` - contains NLU training data
- `/notebooks/*` - contains standalone prototype code as jupyter notebooks
- `/notebooks/models/*` - contains models for custom NLU components
- `/config.yml` - training configurations for the NLU pipeline and policy ensemble
- `/domain.yml` - the domain file, including bot response templates
- `/web/*` - simple web frontend GUI
