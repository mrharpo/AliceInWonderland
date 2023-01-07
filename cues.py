from qlab import Interface

from csv import reader
from pydantic import BaseModel


class Cue(BaseModel):
    pass


def get_lighting_cues(file, page_offset=9):
    with open(file) as f:
        cues = []
        r = reader(f)
        for n, row in enumerate(r):
            if n != 0 and row[2]:
                print(row)
                cues.append(
                    {
                        'q': int(row[2]),
                        'name': row[3],
                        'page': int(row[0]) + page_offset,
                    }
                )
    return cues


def lighting_to_qlab(cues):
    i = Interface()
    for cue in cues:
        i.send(f'/new', 'network')
        i.send(f'/cue/selected/number', cue['q'])
        i.send(f'/cue/selected/name', cue['name'])
        i.send(f'/cue/selected/customString', f'/eos/cue/{cue["q"]}/fire')
        i.send(f'/cue/selected/notes', f'p{cue["page"]}')


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

        i.send('/cue/selected/number', n)
        cleaned_last_line_fragment = last_n(last_line).replace('\n', '')
        i.send(
            '/cue/selected/name', f'{last_character}: ... {cleaned_last_line_fragment}'
        )
        i.send('/cue/selected/notes', last_line)

        # unmute character
        q_id = i.send_and_receive('/new', 'midi')['data']
        i.send('/cue/selected/name', f'unmute {character}')
        i.send(f'/move/{q_id}', [1, group])

        if last_character:
            # mute last character
            q_id = i.send_and_receive('/new', 'midi')['data']
            i.send('/cue/selected/name', f'mute {last_character}')
            i.send(f'/move/{q_id}', [2, group])

        last_line = line[1]
        last_character = character


def mute_sheet_for_character(lines, character):
    mute_state = None
    mutes = []
    for l, line in enumerate(lines):
        # if character has line and we are muted
        if line[0] == character and mute_state == None:
            # unmute
            mute_state = 0
            mutes.append([l + 1, character, mute_state, lines[l - 1]])

        # if we are unmuted and not speaking
        if mute_state == 0 and line[0] != character:
            # If more than 3 lines away, mute
            if character_next_speaks(lines[l + 1 : l + 5], character) == None:
                # mute
                mute_state = None
                mutes.append([l + 1, character, mute_state, lines[l - 1]])
    return mutes


def character_list(lines):
    return set([line[0] for line in lines if line[0]])


def character_next_speaks(lines, character):
    for l, line in enumerate(lines):
        if line[0] == character:
            return l


def first_n(text, n=5):
    words = text.replace('\n', '').split(' ')
    return ' '.join(words[:n])


def last_n(text, n=5):
    words = text.replace('\n', '').split(' ')
    return ' '.join(words[-n:])


def auto_mute_sheet(lines):
    # {line_no: mute_group[mute_sheet], ...}

    mute_sheet = []
    for character in character_list(lines):
        mute_sheet += mute_sheet_for_character(lines, character)
    mute_sheet = sorted(mute_sheet, key=lambda l: l[0])
    grouped_mute_sheet = {}
    for m in mute_sheet:
        if grouped_mute_sheet.get(m[0]):
            grouped_mute_sheet[m[0]].append(m[1:])
        else:
            grouped_mute_sheet[m[0]] = [m[1:]]
    return grouped_mute_sheet


def auto_mute_sheet_to_qlab(mute_sheet):
    # {line_no: mute_group[mute_sheet], ...}
    i = Interface()

    for line_no, mute_group in mute_sheet.items():
        # create group
        group_id = i.send_and_receive('/new', 'group')['data']
        i.send('/cue/selected/number', line_no)
        last_line = mute_group[0][2]
        i.send(
            '/cue/selected/name',
            last_line[0] + ': ... ' + last_n(last_line[1]),
        )
        i.send('/cue/selected/notes', last_line[1])
        for mute_cue in mute_group:
            # send mute cue
            q_id = i.send_and_receive('/new', 'midi')['data']
            i.send(
                '/cue/selected/name',
                f"{'un' if mute_cue[1] == 0 else ''}mute {mute_cue[0]}",
            )
            i.send(f'/move/{q_id}', [1, group_id])


if __name__ == '__main__':
    from pprint import pp

    lines = get_lines('penzance.csv')
    mutes = auto_mute_sheet(lines)

    pp(mutes)
    auto_mute_sheet_to_qlab(mutes)
