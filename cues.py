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
    last_character = ''
    last_line = ''
    for n, line in enumerate(lines, 1):
        print(n, line)

        if not line[0]:
            continue

        # Create group
        character = line[0]
        group = i.send_and_receive('/new', 'group')['data']

        i.client.send('/cue/selected/number', n)
        cleaned_last_line_fragment = last_n(last_line).replace('\n', '')
        i.client.send(
            '/cue/selected/name', f'{last_character}: ... {cleaned_last_line_fragment}'
        )
        i.client.send('/cue/selected/notes', last_line)

        # unmute character
        q_id = i.send_and_receive('/new', 'midi')['data']
        i.client.send('/cue/selected/name', f'unmute {character}')
        i.client.send(f'/move/{q_id}', [1, group])

        if last_character:
            # mute last character
            q_id = i.send_and_receive('/new', 'midi')['data']
            i.client.send('/cue/selected/name', f'mute {last_character}')
            i.client.send(f'/move/{q_id}', [2, group])

        last_line = line[1]
        last_character = character


def first_n(text, n=5):
    words = text.split(' ')
    return ' '.join(words[:n])


def last_n(text, n=5):
    words = text.split(' ')
    return ' '.join(words[-n:])
