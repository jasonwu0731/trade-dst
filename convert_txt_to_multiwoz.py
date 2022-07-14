import glob
import json
import os
import re
from collections import OrderedDict

TRAIN = True
if TRAIN:
    FILE_PATH = './data/train.2022-06-17.txt'
    OUTPUT_FILE_PATH = "./data/train_multiwoz.json"
else:
    FILE_PATH = './data/dev-dstc11-tts-verbatim.2022-06-28.txt'
    OUTPUT_FILE_PATH = "./data/dev_multiwoz.json"

END_OF_DIALOG = 'END_OF_DIALOG'
regex = re.compile('[^:]*: [^ ]*')


tags = ['line_nr:', 'dialog_id:', 'turn_id:', 'text:', 'speaker:', 'state:']


def parse_state(state_str):
    services = []
    belief_state = []
    for item in state_str.split(';'):
        split_values = item.split('=')
        key = split_values[0].strip()
        value = split_values[1].strip()
        belief_state.append({'slots':[[key, value]]})
        service = key.split('-')[0]
        if service not in services:
            services.append(service)
    return belief_state, services

dialogs = []
dialog_id = ''
prev_dialog_id = ''
turn_idx = 0

with open(FILE_PATH) as f:
    lines = f.readlines()
    dialog = OrderedDict({'domains': [], 'dialogue': []})
    dialogue = OrderedDict({'system_transcript': ''})
    for line in lines:
        line = line.strip()
        if line == END_OF_DIALOG:
            prev_dialog_id = dialog_id
            dialogs.append(dialog)
            dialog = OrderedDict({'domains': [], 'dialogue': []})
            turn_idx = 0
            dialogue = OrderedDict({'system_transcript': ''})
            continue
        if line.find('user:') >= 0:
            tags[4] = 'user:'
            is_user_turn = True
        elif line.find('agent:') >= 0:
            value = line[line.find('agent:') + len('agent:') + 1:line.find('state:') - 1]
            dialogue = OrderedDict({'system_transcript': value})
            continue

        for idx, tag in enumerate(tags):
            value = ''
            if line.find(tag) >= 0:
                if idx < len(tags) - 1:
                    value = line[line.find(tag) + len(tag) + 1:line.find(tags[idx + 1])]
                else:
                    value = line[line.find(tag) + len(tag) + 1:]
                value = value.strip()

            if len(value) > 0:
                if tag == 'line_nr:' or tag == 'turn_id:':
                    pass
                elif tag == 'dialog_id:':
                    dialog_id = value
                    if prev_dialog_id == '':
                        prev_dialog_id = dialog_id
                    if dialog_id != prev_dialog_id:
                        prev_dialog_id = dialog_id
                        dialogs.append(dialog)
                        dialog = OrderedDict({'domains': [], 'dialogue': []})
                        turn_idx = 0
                        dialogue = OrderedDict({'system_transcript': ''})
                    dialog['dialogue_idx'] = value
                else:
                    if tag == 'user:':
                        dialogue['transcript'] = value
                    else:
                        if tag == 'state:':
                            state, domains = parse_state(value)
                            dialogue['belief_state'] = state
                            dialogue['domain'] = domains[-1]
                            for domain in domains:
                                if domain not in dialog['domains']:
                                    dialog['domains'].append(domain)
                        else:
                            dialogue[tag[:-1]] = value

            if idx == len(tags) - 1 and is_user_turn:
                dialogue['turn_idx'] = turn_idx
                dialog['dialogue'].append(dialogue)
                turn_idx = turn_idx + 1

with open(OUTPUT_FILE_PATH, "w") as outfile:
    outfile.write(json.dumps(dialogs, indent=4, sort_keys=True))