import os
import subprocess

import torchaudio
import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model, AutoTokenizer

from config import FFMPEG_PATH

# ── Load Seamless M4T STT model ────────────────────────────────────────────────
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model     = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
tokenizer = AutoTokenizer.from_pretrained("facebook/seamless-m4t-v2-large")

def convert_to_wav(ogg_path: str, wav_path: str) -> bool:
    """
    Use ffmpeg to convert .ogg to mono 16 kHz .wav.
    """
    cmd = [
        FFMPEG_PATH,
        "-i", ogg_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path,
        "-y"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode == 0

def transcribe_audio(wav_path: str) -> str:
    """
    Run the Seamless M4T model to get text from audio.
    """
    waveform, sr = torchaudio.load(wav_path)
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    inputs = processor(audios=waveform, sampling_rate=sr, return_tensors="pt")
    gen    = model.generate(**inputs, tgt_lang="eng", generate_speech=False,
                            return_dict_in_generate=True)
    token_ids = gen.sequences.squeeze().tolist()
    return tokenizer.decode(token_ids, skip_special_tokens=True)
