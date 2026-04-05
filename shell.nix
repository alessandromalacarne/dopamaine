{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    ffmpeg
    zlib
    stdenv.cc.cc.lib
    # Adicionando as bibliotecas do CUDA 12 explicitamente
    cudaPackages.cudatoolkit
    cudaPackages.libcublas
    cudaPackages.cudnn
  ];

  shellHook = ''
    # Mapeando todas as bibliotecas necessárias para o ambiente virtual
    export LD_LIBRARY_PATH="${pkgs.zlib}/lib:${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.cudaPackages.cudatoolkit}/lib:${pkgs.cudaPackages.libcublas}/lib:${pkgs.cudaPackages.cudnn}/lib:/run/opengl-driver/lib:$LD_LIBRARY_PATH"
    
    echo "Ambiente NixOS com suporte CUDA 12 e libcublas pronto!"
    
    if [ -d ".venv" ]; then
       source .venv/bin/activate
    fi
  '';
}
