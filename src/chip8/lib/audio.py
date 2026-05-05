import ctypes
import io
import math
import struct
import wave

import sdl2
import sdl2.sdlmixer as mix


SAMPLE_RATE = 44100
TONE_HZ = 440
TONE_SECONDS = 0.25
VOLUME = 0.25


def _square_wave_wav_bytes():
    """Generate an in-memory WAV file holding one period-aligned square-wave loop."""
    samples_per_cycle = SAMPLE_RATE / TONE_HZ
    total_samples = int(round(SAMPLE_RATE * TONE_SECONDS / samples_per_cycle) * samples_per_cycle)
    amp = int(32767 * VOLUME)

    frames = bytearray()
    for n in range(total_samples):
        sign = 1 if math.sin(2 * math.pi * TONE_HZ * n / SAMPLE_RATE) >= 0 else -1
        frames += struct.pack('<h', amp * sign)

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(bytes(frames))
    return buf.getvalue()


class Audio:

    def __init__(self):
        self.enabled = False
        self.chunk = None
        self.channel = -1
        self._wav_bytes = None
        self._wav_buf = None  # keep a reference so the underlying memory isn't freed

    def open(self):
        if sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_AUDIO) != 0:
            print(f"[audio] SDL audio init failed: {sdl2.SDL_GetError().decode()} — sound disabled")
            return

        if mix.Mix_OpenAudio(SAMPLE_RATE, mix.MIX_DEFAULT_FORMAT, 1, 512) != 0:
            print(f"[audio] Mix_OpenAudio failed: {mix.Mix_GetError().decode()} — sound disabled")
            return

        self._wav_bytes = _square_wave_wav_bytes()
        self._wav_buf = ctypes.create_string_buffer(self._wav_bytes, len(self._wav_bytes))
        rw = sdl2.SDL_RWFromMem(self._wav_buf, len(self._wav_bytes))
        if not rw:
            print(f"[audio] SDL_RWFromMem failed: {sdl2.SDL_GetError().decode()} — sound disabled")
            mix.Mix_CloseAudio()
            return

        self.chunk = mix.Mix_LoadWAV_RW(rw, 1)
        if not self.chunk:
            print(f"[audio] Mix_LoadWAV_RW failed: {mix.Mix_GetError().decode()} — sound disabled")
            mix.Mix_CloseAudio()
            return

        self.enabled = True

    def play(self):
        if not self.enabled:
            return
        if self.channel == -1 or mix.Mix_Playing(self.channel) == 0:
            self.channel = mix.Mix_PlayChannel(-1, self.chunk, -1)

    def stop(self):
        if not self.enabled or self.channel == -1:
            return
        mix.Mix_HaltChannel(self.channel)
        self.channel = -1

    def shutdown(self):
        if self.chunk:
            mix.Mix_FreeChunk(self.chunk)
            self.chunk = None
        if self.enabled:
            mix.Mix_CloseAudio()
            self.enabled = False
