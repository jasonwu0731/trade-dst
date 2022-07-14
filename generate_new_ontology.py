import json
import copy

f_train_multiwoz = open('./data/train_multiwoz.json')
train_multiwoz = json.load(f_train_multiwoz)

f_dev_multiwoz = open('./data/dev_multiwoz.json')
dev_multiwoz = json.load(f_dev_multiwoz)

dev_multiwoz = train_multiwoz + dev_multiwoz

google_key = ['hotel-name', 'restaurant-name', 'bus-departure', 'bus-destination', 'train-departure', 'train-destination']

f_ontology = open('./data/multi-woz/MULTIWOZ2 2/ontology.json')
ontology = json.load(f_ontology)

new_ontology = copy.deepcopy(ontology)
convert_key_list = {
    'hotel-price range': 'hotel-pricerange',
    'hotel-book people': 'hotel-people',
    'hotel-book day': 'hotel-day',
    'hotel-book stay': 'hotel-stay',
    'train-book people': 'train-people',
    'train-arrive by': 'train-arriveby',
    'train-leave at': 'train-leaveat',
    'restaurant-price range': 'restaurant-pricerange',
    'restaurant-book people': 'restaurant-people',
    'restaurant-book day': 'restaurant-day',
    'restaurant-book time': 'restaurant-time',
    'bus-leaveAt': 'bus-leaveat',

}

new_key_list = [
    'taxi-arriveby', 'taxi-leaveat', 'bus-arriveby'
]

for old_key, new_key in convert_key_list.items():
    new_ontology[new_key] = new_ontology[old_key]
    del new_ontology[old_key]

for new_key in new_key_list:
    new_ontology[new_key] = []

for dialog_multiwoz in dev_multiwoz:
    if 'dialogue_idx' not in dialog_multiwoz:
        continue
    dialog_multiwoz_idx = dialog_multiwoz['dialogue_idx']
    for dialogue_multiwoz in dialog_multiwoz['dialogue']:
        if 'belief_state' in dialogue_multiwoz:
            for belief_state in dialogue_multiwoz['belief_state']:
                key = belief_state['slots'][0][0]
                value = belief_state['slots'][0][1]
                if value not in new_ontology[key]:
                    new_ontology[key].append(value)


json.dump(new_ontology, open('./data/new_ontology.json', 'w'), indent=4)

f_train_multiwoz.close()
f_dev_multiwoz.close()
f_ontology.close()
