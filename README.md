# Project Advanced Web Technologies WS 21/22 (Chatbot-Semantics: User Input Analysis)

[TOC]

## Setup

### Install the dependencies

In a new Python 3.7.X virtual environment run:

```bash
# upgrade pip to newer version
pip install -U pip
# make sure wheel and setuptools is installed and updated
pip install -U setuptools wheel
# install all other dependencies
# note: this file does not contain all necessary dependencies to run the notebooks
pip install -r requirements.txt
```

Another requirement for the NLU pipeline is Docker. Reference for Docker installation: <https://docs.docker.com/get-docker/>

### Download trained models for custom NLU components

Download the following files and place them in the `/notebooks/models/` folder:

| File                | Link                                                              |     Size |
| ------------------- | ----------------------------------------------------------------- | -------: |
| FastText Model      | <https://drive.google.com/file/d/1Q3Zu2ddgXeLIbxM0WjjgQwIsXCW5NH7s> | 114.5 MB |
| Vocabulary          | <https://drive.google.com/file/d/1wkfO-so2vna0vg8uASUVaZHh88g0vNfE> | 397.3 MB |
| Language Classifier | <https://drive.google.com/file/d/1_0dCbLozOocyQDWzZLI3WGG-RBDkc7Y2> |  20.6 MB |

## Running the bot

### Important: Training

For the initial startup / after each change, it is required to (re-)train Rasa. This can be initialized from within `rasa x` or by using the following command:

```bash
rasa train
```

### Development

Use the following commands to start Rasa X:

```python
# Rasa Actions Server on port 5055
python -m rasa_sdk.endpoint --actions actions
# Custom NLG Server on port 5054
python nlg/server.py
# Duckling entity extraction server on port 8000
docker run -p 8000:8000 rasa/duckling
# start Rasa X when every other service started successfully
rasa x
```

Instead of `rasa x`, `rasa shell --debug` can also be used for some more insight but with less overview. `rasa interactive` can also be used instead of `rasa x` for interactive learning.

> Note: Entities are only mapped internally to categorical slots, meaning they are still represented as their original found value in `rasa interactive` mode as well as `rasa x` mode. For reference see: <https://github.com/RasaHQ/rasa/issues/8755>

### Production

Use the following commands to start the Rasa server:

```python
# Rasa Actions Server on port 5055
python -m rasa_sdk.endpoint --actions actions
# Custom NLG Server on port 5054
python nlg/server.py
# Duckling entity extraction server on port 8000
docker run -p 8000:8000 rasa/duckling
# start Rasa server when every other service started successfully
rasa run --cors "*"
```

After the rasa server is up and running, open the simple web GUI located in the following location (only tested on Google Chrome):

```python
/web/index.html
```

## Overview of the files

- `/actions/*` - contains custom action/api code
- `/components/*` - contains custom NLU components (i.e. sentiment analysis & language detection)
- `/data/core/*` - contains rules and stories training data
- `/data/nlu/*` - contains NLU training data
- `/nlg/` - contains code of custom NLG server
- `/nlg/docs/*` - contains documents used by the NLG server
- `/notebooks/*` - contains standalone prototype code as jupyter notebooks
- `/notebooks/models/*` - contains models for custom NLU components
- `/config.yml` - training configurations for the NLU pipeline and policy ensemble
- `/domain.yml` - the domain file, including bot response templates
- `/web/*` - simple web frontend GUI

## How to add more service topics to the bot?

### The following naming convention must be followed

- Intents for different service topics must begin with `topic_[short-name]`, e.g. `topic_wohnung_anmelden`
- Q&A documents in the `/nlg/docs/` directory must to be named `[short-name].txt`

#### To add new supported service topics

##### Add new service topic for q&a

1. create new `.yml` file in the `/data/nlu/` directory
2. add intent name to the `/domain.yml` file
3. add responses to the `/domain.yml` file
4. get service text from <https://service.berlin.de/dienstleistungen/> and place it in `/nlg/docs/` directory
5. create story for new service by modifying the `/data/core/stories.yml` file
6. add `[short-name]`: `[long-name]` mapping to the `ActionSetTopic` class in the `/actions/actions.py` file
7. add `topic_[short-name]`: `[long-name]` mapping to the `/actions/intent_description_mapping.csv`file

> `[long-name]` can be an arbitrary string and will only be used to replace slot placeholders in responses, i.e. `{topic} ist Ihr gewähltes Thema.` -> `[long-name] ist Ihr gewähltes Thema`.

##### Add new service topic to appointment booking process

> Have a look at the `/actions/db.sqlite3` database to get a better overview. A simple web based SQLite viewer can be found here: <https://inloop.github.io/sqlite-viewer/>

- insert service into `services` table with `[long-name]` as its `name` attribute
- to make a service available for bookings, appointments must be created
- insert new appointments into the `appointments` table with a `date`, an `office` id and a `service` id as attributes
- `date` in `appointments` table must follow *ISO 8601* standard
- offices with its ids can be found in the `offices` table
