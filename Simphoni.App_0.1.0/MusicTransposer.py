# music_transposer.py

import re

# Define note sequences
NOTE_SEQUENCE_SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F',
                        'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_SEQUENCE_FLATS  = ['C', 'Db', 'D', 'Eb', 'E', 'F',
                        'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

ENHARMONIC_EQUIVALENTS = {
    'C#': 'Db', 'Db': 'C#',
    'D#': 'Eb', 'Eb': 'D#',
    'F#': 'Gb', 'Gb': 'F#',
    'G#': 'Ab', 'Ab': 'G#',
    'A#': 'Bb', 'Bb': 'A#'
}

def get_note_sequence(key_signature):
    if 'b' in key_signature and key_signature != 'B':
        return NOTE_SEQUENCE_FLATS
    else:
        return NOTE_SEQUENCE_SHARPS

def note_to_index(note, note_sequence):
    if note in note_sequence:
        return note_sequence.index(note)
    elif note in ENHARMONIC_EQUIVALENTS:
        # Use the enharmonic equivalent
        equivalent_note = ENHARMONIC_EQUIVALENTS[note]
        return note_sequence.index(equivalent_note)
    else:
        return None

def index_to_note(index, note_sequence):
    return note_sequence[index % 12]

def parse_chord(chord):
    pattern = r'^([A-G][b#]?)(.*)$'
    match = re.match(pattern, chord)
    if match:
        root = match.group(1)
        quality = match.group(2)
        return root, quality
    else:
        return None, None

def transpose_chord(chord, steps, note_sequence):
    root, quality = parse_chord(chord)
    if root is None:
        return chord  # Return the chord as is if it cannot be parsed
    root_index = note_to_index(root, note_sequence)
    if root_index is None:
        return chord  # Return the chord as is if root note is unrecognized
    transposed_index = (root_index + steps) % 12
    transposed_root = index_to_note(transposed_index, note_sequence)
    return transposed_root + quality

def transpose_progression(progression, steps, note_sequence):
    chords = progression.split()
    transposed_chords = [transpose_chord(chord, steps, note_sequence) for chord in chords]
    return ' '.join(transposed_chords)

def main():
    print("Welcome to the Music Transposer Tool!")
    original_key = input("Enter the original key (e.g., C, G#, Eb): ").strip()
    target_key = input("Enter the target key (e.g., C#, F, Bb): ").strip()
    progression = input("Enter the chord progression (separate chords with spaces): ").strip()

    # Choose the appropriate note sequence based on the original key
    note_sequence = get_note_sequence(original_key)

    # Calculate the transposition steps
    original_index = note_to_index(original_key, note_sequence)
    target_index = note_to_index(target_key, note_sequence)

    if original_index is None or target_index is None:
        print("Error: Invalid key signature entered.")
        return

    steps = target_index - original_index

    transposed_progression = transpose_progression(progression, steps, note_sequence)
    print("\nTransposed Progression:")
    print(transposed_progression)

if __name__ == "__main__":
    main()
