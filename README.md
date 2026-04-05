# dopamaine

Audio/video transcription tool using faster-whisper.

## Requirements

- Python 3.11+
- ffmpeg (system package)
- NVIDIA GPU with CUDA (optional, CPU fallback supported)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Extract audio from videos
```bash
python video_to_audio.py <input_folder> [output_folder]
```

### Transcribe audio/video to text
```bash
python process.py <input_folder>
```

Transcripts are saved in a `transcript/` subfolder next to each media file.

## Supported Formats

- Video: mp4, mkv, avi, mov, flv, wmv
- Audio: mp3, m4a, wav, flac
