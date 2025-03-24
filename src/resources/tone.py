import constants
if constants.TONE:
    import pygame
    import numpy as np
    from scipy.io import wavfile
    from resources import path

    pygame.init()
    pygame.mixer.init(44100, -16, 2, 2048)

    note_files = {
        'piano': 'assets/sounds/piano_c5.wav',
        'flute': 'assets/sounds/flute_c5.wav',
        'trumpet': 'assets/sounds/trumpet_c5.wav',
        'snare': 'assets/sounds/snare_c5.wav',
        'bell': 'assets/sounds/bell_c5.wav',
        'oboe': 'assets/sounds/oboe_c5.wav'
    }

    datas: dict[str, tuple[int, np.ndarray]] = {

    }

    tones: dict[tuple[str, float, float]: pygame.mixer.Sound] = {

    }

    freq: dict[str, float] = {

    }

    def note_to_frequency(note_name):
        if note_name in freq.keys():
            return freq[note_name]
        note_frequencies = {
            'C': 261.63,
            'C#': 277.18,
            'D': 293.66,
            'D#': 311.13,
            'E': 329.63,

            'F': 349.23,
            'F#': 369.99,
            'G': 392.00,
            'G#': 415.30,
            'A': 440.00,
            'A#': 466.16,
            'B': 493.88,
        }
        fir = note_name[:-1]
        if fir in note_frequencies.keys():
            f = note_frequencies[fir] * 2 ** (int(note_name[-1]) - 5)
            freq[note_name] = f
            return f
        else:
            return None

    def change_pitch(audio_data, new_frequency, original_frequency, sample_rate):
        new_length = int(len(audio_data) * (original_frequency / new_frequency))
        t_new = np.linspace(0, len(audio_data) - 1, new_length, False)
        new_audio_data = np.interp(t_new, np.arange(len(audio_data)), audio_data)
        return new_audio_data

    def load_audio_file(file_path):
        if file_path in datas.keys():
            return datas[file_path]
        sample_rate, audio_data = wavfile.read(path.get_path(file_path))
        if audio_data.ndim == 1:
            audio_data = np.stack((audio_data, audio_data), axis=-1)  # 将单声道转换为立体声
        datas[file_path] = (sample_rate, audio_data)
        return sample_rate, audio_data

    # 函数：播放音符
    def play_note(instrument, new_frequency, duration, auto_play=True):
        if (instrument, new_frequency, duration) in tones.keys():
            if auto_play:
                tones[(instrument, new_frequency, duration)].play()
            return tones[(instrument, new_frequency, duration)]
        file_path = note_files.get(instrument, None)
        if file_path is not None:
            sample_rate, audio_data = load_audio_file(file_path)
            original_frequency = note_to_frequency('C5')

            if original_frequency is not None:
                if audio_data.ndim == 2:  # 立体声
                    left_channel = change_pitch(audio_data[:, 0], new_frequency, original_frequency, sample_rate)
                    right_channel = change_pitch(audio_data[:, 1], new_frequency, original_frequency, sample_rate)
                    new_audio_data = np.stack((left_channel, right_channel), axis=-1)
                else:
                    new_audio_data = change_pitch(audio_data, new_frequency, original_frequency, sample_rate)

                target_length = int(sample_rate * duration)
                if len(new_audio_data) > target_length:
                    new_audio_data = new_audio_data[:target_length]
                else:
                    new_audio_data = np.pad(new_audio_data, ((0, target_length - len(new_audio_data)), (0, 0)), 'constant')

                if new_audio_data.dtype != np.int16:
                    new_audio_data = np.int16(new_audio_data * 32767 / np.max(np.abs(new_audio_data)))

                sound = pygame.sndarray.make_sound(new_audio_data)
                if auto_play:
                    sound.play()
                tones[(instrument, new_frequency, duration)] = sound
                return sound
            else:
                print(f"Frequency for note C5 not found in the frequency mapping.")
                return None
        else:
            print(f"Instrument {instrument} not found in the file mapping.")
            return None

    def play_notes(instrument, data: tuple[str, float]):
        snd = []
        for note, duration in data:
            s = play_note(instrument, note_to_frequency(note), duration, auto_play=False)
            if s is not None:
                snd.append(s)
        if len(snd) > 0:
            for s in snd:
                s.play()
            return True
        else:
            return False
else:
    def play_note(*args, **kwargs):
        pass

    def play_notes(*args, **kwargs):
        pass