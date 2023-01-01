from qlab import Interface
from time import sleep

from csv import reader
from pydantic import BaseModel


class Cue(BaseModel):
    pass


def get_cues():
    with open('cues.csv') as f:
        cues = []
        r = reader(f)
        for n, row in enumerate(r):
            if n != 0 and row[2]:
                print(row)
                cues.append({'q': int(row[2]), 'name': row[3], 'page': int(row[0]) + 9})
    return cues


def cues_to_qlab(cues):
    i = Interface()
    for cue in cues:
        i.client.send(f'/new', 'network')
        i.client.send(f'/cue/selected/number', cue['q'])
        i.client.send(f'/cue/selected/name', cue['name'])
        i.client.send(f'/cue/selected/customString', f'/eos/cue/{cue["q"]}/fire')
        i.client.send(f'/cue/selected/notes', f'p{cue["page"]}')
        sleep(0.01)


def moments_to_qlab():
    i = Interface()
    with open('moments.csv') as f:
        moments = []
        r = reader(f)
        for row in r:
            moments.append((int(row[0]), row[1]))
    for moment in moments:
        i.client.send('/new', 'group')
        i.client.send('/cue/selected/number', f'm{moment[0]}')
        i.client.send('/cue/selected/name', f'{moment[0]} - {moment[1]}')
        sleep(0.01)


def get_lines(file):
    with open(file) as f:
        lines = []
        r = reader(f)
        for row in r:
            lines.append(row)
        return lines


def lines_to_mutes(lines):
    i = Interface()
    character = ''
    for n, line in enumerate(lines):

        print(n, line)
        # i.client.send('/new', 'group')
        # i.client.send('/cue/selected/number', n)
        if not line[0]:
            continue

        # mute last character
        i.client.send('/new', 'midi')
        i.client.send('/cue/selected/name', f'mute {character}')

        # unmute character
        character = line[0]
        i.client.send('/new', 'midi')
        i.client.send('/cue/selected/name', f'unmute {character}')
        i.client.send('/cue/selected/notes', line[1])
        i.client.send('/cue/selected/continueMode', 1)

        sleep(0.01)
