from pydub import AudioSegment
from datetime import datetime
import os
import re

def loop_audio_to_length(audio: AudioSegment, target_duration: int) -> AudioSegment:
    """Loops audio to reach a specific duration."""
    looped = AudioSegment.empty()
    while len(looped) < target_duration:
        looped += audio
    return looped[:target_duration]

# === PARAMETERS ===
AUDIO_DIR = r"H:\My Drive\Client Work\2025-05 Reichl Kolstad Orthodontics\2025-05-12 - Recordings"
BACKGROUND_FILENAME = "Background_Music.mp3"
VOICE_PATTERN = r"^\d+_.*\.mp3$"  # Matches files like 01_Referrals.mp3

INTRO_DELAY_MS = 1000             # Silence before first clip
OUTRO_DELAY_MS = 6000             # Background buffer after each voice clip
FINAL_BACKGROUND_MS = 5000        # Final background music at end

BACKGROUND_VOLUME_DUCK_DB = -13   # Volume reduction under voice
FADE_IN_VOICE_MS = 700            # Background fade-in under voice
FADE_OUT_VOICE_MS = 1000          # Background fade-out after voice

# === LOAD AUDIO FILES ===
background = AudioSegment.from_file(os.path.join(AUDIO_DIR, BACKGROUND_FILENAME))

voice_files = sorted([
    f for f in os.listdir(AUDIO_DIR)
    if re.match(VOICE_PATTERN, f)
], key=lambda x: int(x.split("_")[0]))

voice_clips = [AudioSegment.from_file(os.path.join(AUDIO_DIR, f)) for f in voice_files]

# === ESTIMATE DURATION AND LOOP BACKGROUND MUSIC ===
estimated_duration = (
    INTRO_DELAY_MS +
    sum(len(c) + OUTRO_DELAY_MS for c in voice_clips) +
    FINAL_BACKGROUND_MS
)
looped_background = loop_audio_to_length(background, estimated_duration)

# === BUILD TIMELINE ===
timeline = AudioSegment.silent(duration=INTRO_DELAY_MS)
bg_cursor = INTRO_DELAY_MS  # Start after intro silence

for clip in voice_clips:
    # Full-volume background before clip
    bg_segment = looped_background[bg_cursor:bg_cursor + OUTRO_DELAY_MS]
    timeline += bg_segment.fade_in(FADE_IN_VOICE_MS).fade_out(FADE_OUT_VOICE_MS)
    bg_cursor += OUTRO_DELAY_MS

    # Ducked background under voice
    voice_len = len(clip)
    fade_in_time = min(FADE_IN_VOICE_MS, voice_len // 3)
    fade_out_time = min(FADE_OUT_VOICE_MS, voice_len // 2)

    ducked_bg = looped_background[bg_cursor:bg_cursor + voice_len].apply_gain(BACKGROUND_VOLUME_DUCK_DB)
    ducked_bg = ducked_bg.fade_in(fade_in_time).fade_out(fade_out_time)

    mixed = ducked_bg.overlay(clip)
    timeline += mixed
    bg_cursor += voice_len

# === FINAL TRAILING BACKGROUND MUSIC ===
final_bg = looped_background[bg_cursor:bg_cursor + FINAL_BACKGROUND_MS]
final_bg = final_bg.fade_in(FADE_IN_VOICE_MS).fade_out(FADE_OUT_VOICE_MS)
timeline += final_bg

# === EXPORT ===
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"Hold_Message_{timestamp}.mp3"
output_path = os.path.join(AUDIO_DIR, filename)

timeline.export(output_path, format="mp3")
print(f"Exported final mix to: {output_path}")
