import sys
import subprocess
import time
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def extract_audio(video_path, audio_output_path):
    try:
        command = [
            'ffmpeg',
            '-y',
            '-i', str(video_path),
            '-vn',
            '-acodec', 'libmp3lame',
            '-q:a', '4', 
            str(audio_output_path)
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"      {Colors.RED}✗ FFmpeg error:{Colors.ENDC} {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.BOLD}Usage:{Colors.ENDC} python video_to_audio.py <input_folder> [output_folder]")
        return

    input_path = Path(sys.argv[1]).resolve()
    custom_output = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    
    print(f"{Colors.BLUE}🔎 Mapping videos...{Colors.ENDC}")
    
    queue = []
    if input_path.is_file():
        if input_path.suffix.lower() in video_extensions:
            queue.append(input_path)
    else:
        queue = [f for f in input_path.rglob('*') if f.suffix.lower() in video_extensions]
    
    queue.sort()
    total = len(queue)

    if total == 0:
        print(f"{Colors.RED}No compatible videos found in {input_path}.{Colors.ENDC}")
        return

    if custom_output:
        custom_output.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.YELLOW}[CENTRALIZED MODE]{Colors.ENDC} Output: {custom_output}")
    else:
        print(f"{Colors.BLUE}[LOCAL MODE]{Colors.ENDC} Output: Individual 'audio_extracted' folders")

    print(f"{Colors.GREEN}Ready! {total} videos to convert.{Colors.ENDC}\n")

    start_global = time.time()

    for i, video_file in enumerate(queue, 1):
        if custom_output:
            audio_output = custom_output / f"{video_file.stem}.mp3"
        else:
            audio_dir = video_file.parent / "audio_extracted"
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_output = audio_dir / f"{video_file.stem}.mp3"
        
        percent = (i / total) * 100
        prefix = f"{Colors.BLUE}[{i}/{total} - {percent:.1f}%]{Colors.ENDC}"

        if audio_output.exists() and audio_output.stat().st_size > 0:
            print(f"{prefix} {Colors.YELLOW}Skipping:{Colors.ENDC} {video_file.name}")
            continue

        print(f"{prefix} {Colors.BOLD}Extracting:{Colors.ENDC} {video_file.name}")
        
        if extract_audio(video_file, audio_output):
            print(f"      {Colors.GREEN}✓ Success{Colors.ENDC}")
        else:
            if audio_output.exists(): audio_output.unlink()

    total_time = (time.time() - start_global) / 60
    print(f"\n{Colors.HEADER}--- EXTRACTION COMPLETE ---{Colors.ENDC}")
    print(f"Total time: {total_time:.2f} minutes")

if __name__ == "__main__":
    main()
