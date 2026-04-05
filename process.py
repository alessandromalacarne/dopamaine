import os
import sys
import time
from pathlib import Path
from faster_whisper import WhisperModel

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

class Transcriber:
    def __init__(self):
        self.model_name = "medium"
        self.prompt_text = self._load_prompt()
        
        print(f"{Colors.HEADER}--- Motor Estável: {self.model_name} ---{Colors.ENDC}")
        if self.prompt_text:
            print(f"{Colors.BLUE}[Contexto]{Colors.ENDC} Prompt carregado ({len(self.prompt_text)} caracteres)")
        
        try:
            self.model = WhisperModel(self.model_name, device="cuda", compute_type="float16")
            print(f"{Colors.GREEN}[OK]{Colors.ENDC} GPU CUDA pronta para a maratona.")
        except Exception as e:
            print(f"{Colors.YELLOW}[Aviso]{Colors.ENDC} Erro GPU: {e}. Usando CPU (int8)...")
            self.model = WhisperModel(self.model_name, device="cpu", compute_type="int8")

    def _load_prompt(self):
        prompt_file = Path("prompt.txt")
        if prompt_file.exists():
            try:
                return prompt_file.read_text(encoding="utf-8").strip()
            except Exception as e:
                print(f"{Colors.RED}Erro ao ler prompt.txt: {e}{Colors.ENDC}")
        return None

    def show_progress(self, current_sec, total_sec):
        if total_sec <= 0: return
        percent = min(current_sec / total_sec, 1.0)
        bar_len = 25
        filled = int(bar_len * percent)
        bar = '█' * filled + '░' * (bar_len - filled)
        sys.stdout.write(f'\r      {Colors.BLUE}Progresso: |{bar}| {percent*100:.1f}%{Colors.ENDC}')
        sys.stdout.flush()

    def is_valid(self, path):
        return path.exists() and path.stat().st_size > 0

    def process_file(self, input_path, output_path, current, total_files):
        overall_percent = (current / total_files) * 100
        prefix = f"{Colors.BLUE}[{current}/{total_files} - {overall_percent:.1f}%]{Colors.ENDC}"

        if self.is_valid(output_path):
            print(f"{prefix} {Colors.YELLOW}Pulando:{Colors.ENDC} {input_path.name}")
            return True

        print(f"{prefix} {Colors.BOLD}Processando:{Colors.ENDC} {input_path.name}")
        start_time = time.time()
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            segments, info = self.model.transcribe(
                str(input_path), 
                beam_size=2, 
                language="pt",
                initial_prompt=self.prompt_text,
                vad_filter=True,
                condition_on_previous_text=False
            )

            results = []
            for segment in segments:
                self.show_progress(segment.end, info.duration)
                text = segment.text.strip()
                if text:
                    results.append(f"[{segment.start:.2f}s] {text}\n")
            
            sys.stdout.write('\n')
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(results)
            
            elapsed = (time.time() - start_time) / 60
            speed = (info.duration / 60) / elapsed if elapsed > 0 else 0
            print(f"      {Colors.GREEN}✓ Sucesso{Colors.ENDC} em {elapsed:.2f}min ({speed:.1f}x real)")
            return True

        except Exception as e:
            sys.stdout.write('\n')
            print(f"      {Colors.RED}✗ Erro:{Colors.ENDC} {str(e)}")
            return False

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Erro: Você precisa passar o caminho de uma pasta ou arquivo.{Colors.ENDC}")
        print(f"Exemplo: python process.py ./meus_videos")
        return

    # O join trata casos onde o shell do Nix pode estar desmembrando caminhos com espaços
    raw_path = " ".join(sys.argv[1:])
    root_path = Path(raw_path).resolve()
    
    extensions = {".mp4", ".mkv", ".avi", ".mov", ".mp3", ".m4a", ".wav", ".flac"}
    
    print(f"{Colors.BLUE}🔎 Analisando: {root_path}{Colors.ENDC}")
    
    queue = []
    if root_path.is_file():
        if root_path.suffix.lower() in extensions:
            queue.append(root_path)
    elif root_path.is_dir():
        # rglob('*') busca tudo recursivamente
        queue = [f for f in root_path.rglob('*') if f.suffix.lower() in extensions]
    
    queue.sort() 
    total = len(queue)

    if total == 0:
        print(f"{Colors.YELLOW}Nenhum arquivo de mídia encontrado.{Colors.ENDC}")
        print(f"Caminho verificado: {root_path}")
        print(f"Formatos aceitos: {', '.join(extensions)}")
        return

    print(f"{Colors.GREEN}Pronto! {total} arquivos detectados.{Colors.ENDC}\n")
    
    worker = Transcriber()
    for i, file_path in enumerate(queue, 1):
        # Define a pasta 'transcript' relativa ao arquivo de mídia encontrado
        transcript_dir = file_path.parent / "transcript"
        output_file = transcript_dir / f"{file_path.name}.txt"
        worker.process_file(file_path, output_file, i, total)

if __name__ == "__main__":
    main()
