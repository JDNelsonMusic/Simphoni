import py_midicsv as pm
import sys
import os
import argparse
import logging
from collections import defaultdict
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

# Map MIDI note numbers to note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_note_to_name(midi_note_number):
    octave = (midi_note_number // 12) - 1
    note = NOTE_NAMES[midi_note_number % 12]
    return f"{note}{octave}"

class MIDIParser:
    def __init__(self, ppq=480):
        self.ppq = ppq
        self.tempo = 120  # Default tempo
        self.time_signatures = []
        self.tracks = defaultdict(list)
        self.current_time = defaultdict(int)
        self.active_notes = defaultdict(dict)  # For calculating note durations

    def parse_csv(self, csv_data, filters=None):
        """
        Parse MIDI CSV data and extract events.

        :param csv_data: List of CSV lines from the MIDI file.
        :param filters: Dictionary with filter options.
        """
        for line in csv_data:
            parts = [part.strip() for part in line.split(',')]
            if len(parts) < 5:
                continue  # Skip lines that don't have enough data

            track = int(parts[0])
            time = int(parts[1])
            event_type = parts[2]
            args = parts[3:]

            # Update current time for the track
            delta_time = time - self.current_time[track]
            self.current_time[track] = time

            if event_type == 'Header':
                format_type = int(args[0])
                num_tracks = int(args[1])
                self.ppq = int(args[2])
            elif event_type == 'Tempo':
                self.tempo = 60000000 / int(args[0])  # Convert microseconds per quarter note to BPM
            elif event_type == 'Time_signature':
                numerator = int(args[0])
                denominator = 2 ** int(args[1])
                self.time_signatures.append({
                    'time': time,
                    'numerator': numerator,
                    'denominator': denominator
                })
            elif event_type in ['Note_on_c', 'Note_off_c']:
                channel = int(args[0])
                note_number = int(args[1])
                velocity = int(args[2])

                note_name = midi_note_to_name(note_number)

                if filters:
                    if 'channels' in filters and channel not in filters['channels']:
                        continue
                    if 'tracks' in filters and track not in filters['tracks']:
                        continue

                event = {
                    'time': time,
                    'event': 'Note On' if event_type == 'Note_on_c' else 'Note Off',
                    'note': note_name,
                    'note_number': note_number,
                    'velocity': velocity,
                    'channel': channel,
                    'track': track
                }

                if event['event'] == 'Note On' and velocity > 0:
                    # Start of a note
                    self.active_notes[(track, channel, note_number)] = {
                        'start_time': time,
                        'velocity': velocity,
                        'note_name': note_name
                    }
                else:
                    # End of a note
                    active_note = self.active_notes.get((track, channel, note_number))
                    if active_note:
                        duration = time - active_note['start_time']
                        note_event = {
                            'start_time': active_note['start_time'],
                            'end_time': time,
                            'duration': duration,
                            'note': active_note['note_name'],
                            'velocity': active_note['velocity'],
                            'channel': channel,
                            'track': track
                        }
                        self.tracks[track].append(note_event)
                        del self.active_notes[(track, channel, note_number)]
            elif event_type in ['Control_c', 'Program_c', 'Pitch_bend_c']:
                channel = int(args[0])
                if filters:
                    if 'channels' in filters and channel not in filters['channels']:
                        continue
                    if 'tracks' in filters and track not in filters['tracks']:
                        continue
                event = {
                    'time': time,
                    'event': event_type,
                    'channel': channel,
                    'args': args[1:],
                    'track': track
                }
                self.tracks[track].append(event)
            # Handle other MIDI events as needed

    def get_parsed_data(self):
        return {
            'ppq': self.ppq,
            'tempo': self.tempo,
            'time_signatures': self.time_signatures,
            'tracks': self.tracks
        }

class MIDIConverter:
    def __init__(self, input_file, output_file, output_format='text', filters=None, log_level=logging.INFO):
        self.input_file = input_file
        self.output_file = output_file
        self.output_format = output_format
        self.filters = filters
        logging.basicConfig(level=log_level, format='%(levelname)s:%(message)s')

    def convert(self):
        # Convert MIDI to CSV
        try:
            logging.info(f"Reading MIDI file: {self.input_file}")
            csv_data = pm.midi_to_csv(self.input_file)
        except Exception as e:
            logging.error(f"Error reading MIDI file: {e}")
            sys.exit(1)

        # Parse CSV data
        parser = MIDIParser()
        parser.parse_csv(csv_data, filters=self.filters)
        parsed_data = parser.get_parsed_data()

        # Format parsed data
        if self.output_format == 'text':
            formatted_output = self.format_parsed_data_text(parsed_data)
        elif self.output_format == 'json':
            formatted_output = self.format_parsed_data_json(parsed_data)
        else:
            logging.error(f"Unsupported output format: {self.output_format}")
            sys.exit(1)

        # Write to output file
        try:
            logging.info(f"Writing output to: {self.output_file}")
            with open(self.output_file, 'w') as f:
                f.write(formatted_output)
            logging.info("Conversion complete.")
        except Exception as e:
            logging.error(f"Error writing to output file: {e}")
            sys.exit(1)

    def format_parsed_data_text(self, parsed_data):
        formatted_data = []
        formatted_data.append(f"PPQ (Ticks Per Quarter Note): {parsed_data['ppq']}")
        formatted_data.append(f"Tempo (BPM): {parsed_data['tempo']}")
        formatted_data.append("Time Signatures:")
        for ts in parsed_data['time_signatures']:
            formatted_data.append(f"  - Time {ts['time']}: {ts['numerator']}/{ts['denominator']}")

        formatted_data.append("\nTracks:")
        for track_num, events in parsed_data['tracks'].items():
            formatted_data.append(f"\nTrack {track_num}:")
            for event in events:
                if 'duration' in event:
                    start_time = event['start_time']
                    end_time = event['end_time']
                    duration = event['duration']
                    formatted_data.append(
                        f"  Time {start_time}-{end_time} (Duration: {duration}): "
                        f"Note {event['note']} (Velocity: {event['velocity']}, Channel: {event['channel']})"
                    )
                else:
                    formatted_data.append(
                        f"  Time {event['time']}: {event['event']} "
                        f"(Channel: {event['channel']}, Args: {event.get('args', '')})"
                    )
        return '\n'.join(formatted_data)

    def format_parsed_data_json(self, parsed_data):
        # Convert parsed data to JSON format
        # We need to convert the defaultdict to a regular dict for JSON serialization
        parsed_data['tracks'] = {track: events for track, events in parsed_data['tracks'].items()}
        return json.dumps(parsed_data, indent=4)

# GUI Implementation
class MIDIConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIDI to Readable Converter")
        self.create_widgets()

    def create_widgets(self):
        self.input_label = tk.Label(self.root, text="Input MIDI File:")
        self.input_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.input_entry = tk.Entry(self.root, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        self.input_button = tk.Button(self.root, text="Browse", command=self.browse_input_file)
        self.input_button.grid(row=0, column=2, padx=5, pady=5)

        self.output_label = tk.Label(self.root, text="Output File:")
        self.output_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.output_entry = tk.Entry(self.root, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        self.output_button = tk.Button(self.root, text="Browse", command=self.browse_output_file)
        self.output_button.grid(row=1, column=2, padx=5, pady=5)

        self.format_label = tk.Label(self.root, text="Output Format:")
        self.format_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.format_var = tk.StringVar(value='text')
        self.format_text_radio = tk.Radiobutton(self.root, text='Text', variable=self.format_var, value='text')
        self.format_text_radio.grid(row=2, column=1, sticky='w')
        self.format_json_radio = tk.Radiobutton(self.root, text='JSON', variable=self.format_var, value='json')
        self.format_json_radio.grid(row=2, column=1)

        self.filter_label = tk.Label(self.root, text="Filters:")
        self.filter_label.grid(row=3, column=0, padx=5, pady=5, sticky='ne')
        self.channels_label = tk.Label(self.root, text="Channels (comma-separated):")
        self.channels_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.channels_entry = tk.Entry(self.root, width=20)
        self.channels_entry.grid(row=3, column=1, padx=5, pady=5, sticky='e')
        self.tracks_label = tk.Label(self.root, text="Tracks (comma-separated):")
        self.tracks_label.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        self.tracks_entry = tk.Entry(self.root, width=20)
        self.tracks_entry.grid(row=4, column=1, padx=5, pady=5, sticky='e')

        self.convert_button = tk.Button(self.root, text="Convert", command=self.start_conversion)
        self.convert_button.grid(row=5, column=1, padx=5, pady=15)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")]
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)

    def start_conversion(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        output_format = self.format_var.get()
        channels = self.channels_entry.get()
        tracks = self.tracks_entry.get()

        filters = {}
        if channels:
            filters['channels'] = [int(ch.strip()) for ch in channels.split(',') if ch.strip().isdigit()]
        if tracks:
            filters['tracks'] = [int(tr.strip()) for tr in tracks.split(',') if tr.strip().isdigit()]

        if not input_file or not output_file:
            messagebox.showerror("Error", "Please specify input and output files.")
            return

        converter = MIDIConverter(
            input_file=input_file,
            output_file=output_file,
            output_format=output_format,
            filters=filters
        )
        threading.Thread(target=converter.convert).start()
        messagebox.showinfo("Success", "Conversion started. Check logs for progress.")

    def run(self):
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(
        description='Convert MIDI files to a readable syntax for analysis.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_midi', nargs='?', help='Input MIDI file (.mid)')
    parser.add_argument('output_file', nargs='?', help='Output file (text or JSON)')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                        help='Output format')
    parser.add_argument('-c', '--channels', type=str,
                        help='Comma-separated list of channels to include')
    parser.add_argument('-t', '--tracks', type=str,
                        help='Comma-separated list of tracks to include')
    parser.add_argument('-l', '--log-level', type=str, default='INFO',
                        help='Logging level (DEBUG, INFO, WARNING, ERROR)')
    parser.add_argument('-g', '--gui', action='store_true',
                        help='Launch the GUI version')
    args = parser.parse_args()

    if args.gui:
        app = MIDIConverterGUI()
        app.run()
    else:
        # Check if input and output files are provided
        if not args.input_midi or not args.output_file:
            parser.print_help()
            sys.exit(1)

        # Check if input file exists
        if not os.path.isfile(args.input_midi):
            print(f"Error: File {args.input_midi} does not exist.")
            sys.exit(1)

        # Set up filters
        filters = {}
        if args.channels:
            filters['channels'] = [int(ch.strip()) for ch in args.channels.split(',') if ch.strip().isdigit()]
        if args.tracks:
            filters['tracks'] = [int(tr.strip()) for tr in args.tracks.split(',') if tr.strip().isdigit()]

        # Set up logging level
        log_level = getattr(logging, args.log_level.upper(), logging.INFO)

        # Perform conversion
        converter = MIDIConverter(
            input_file=args.input_midi,
            output_file=args.output_file,
            output_format=args.format,
            filters=filters,
            log_level=log_level
        )
        converter.convert()

if __name__ == '__main__':
    main()
