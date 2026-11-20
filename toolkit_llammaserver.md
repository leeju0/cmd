`sudo` 없이 기존 Conda `sava` 환경 안에 CUDA Toolkit 12.8을 설치하고, 같은 환경에서 `llama-server`를 빌드하는 방법입니다. 아래 명령은 각각 한 줄로 실행하면 됩니다.

### 1. Conda `sava` 환경 활성화

```bash
eval "$(conda shell.bash hook)" && conda activate sava
```

환경과 GPU 드라이버를 확인합니다.

```bash
python --version
```

```bash
nvidia-smi
```

`nvidia-smi`가 정상이어야 합니다. 여기서 표시되는 CUDA 12.8은 드라이버가 지원하는 CUDA 버전이며, `nvcc`가 없다면 Toolkit은 아직 없는 상태입니다.

### 2. CUDA Toolkit 12.8 설치

NVIDIA Conda 채널에서 Toolkit 12.8 전체를 `sava` 환경에 설치합니다.

```bash
conda install -y -c nvidia/label/cuda-12.8.0 cuda
```

`cmake`, `git`, C/C++ 컴파일러도 사용자 환경에 설치합니다.

```bash
conda install -y -c conda-forge cmake ninja git gcc_linux-64=12 gxx_linux-64=12
```

설치된 컴파일러 환경 변수를 적용하기 위해 환경을 다시 활성화합니다.

```bash
conda deactivate && conda activate sava
```

CUDA 컴파일러가 설치됐는지 확인합니다.

```bash
which nvcc
```

```bash
nvcc --version
```

다음과 같이 `release 12.8`이 나오면 정상입니다.

```text
Cuda compilation tools, release 12.8
```

### 3. llama.cpp 다운로드

먼저 설치 경로가 이미 존재하는지 확인합니다.

```bash
ls -ld /home/joseph/sava/LLM_model/llama.cpp
```

`No such file or directory`가 나온 경우에만 다음 명령을 실행합니다.

```bash
git clone https://github.com/ggml-org/llama.cpp.git /home/joseph/sava/LLM_model/llama.cpp
```

SAVA OS에서 사용하는 검증된 버전으로 고정합니다.

```bash
git -C /home/joseph/sava/LLM_model/llama.cpp checkout 86b94708f22478f900b76ca02e316f4f3418faff
```

### 4. Conda 컴파일러 설정

```bash
export CC="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cc" CXX="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-c++"
```

설정된 컴파일러를 확인합니다.

```bash
"$CC" --version
```

```bash
"$CXX" --version
```

### 5. CUDA용 llama-server 빌드 설정

Conda 환경 안의 `nvcc`와 CUDA 라이브러리를 사용하도록 설정합니다.

```bash
cmake -S /home/joseph/sava/LLM_model/llama.cpp -B /home/joseph/sava/LLM_model/llama.cpp/build -G Ninja -DGGML_CUDA=ON -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF -DCUDAToolkit_ROOT="$CONDA_PREFIX" -DCMAKE_CUDA_COMPILER="$CONDA_PREFIX/bin/nvcc" -DCMAKE_CUDA_HOST_COMPILER="$CXX" -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" -DCMAKE_BUILD_RPATH="${CONDA_PREFIX}/lib;${CONDA_PREFIX}/targets/x86_64-linux/lib"
```

오류 없이 설정이 끝나면 `llama-server`를 빌드합니다.

```bash
cmake --build /home/joseph/sava/LLM_model/llama.cpp/build --target llama-server -j 2
```

### 6. 실행에 필요한 CUDA 라이브러리 경로 설정

```bash
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
```

빌드된 `llama-server`를 확인합니다.

```bash
/home/joseph/sava/LLM_model/llama.cpp/build/bin/llama-server --version
```

라이브러리 누락 여부도 확인합니다.

```bash
ldd /home/joseph/sava/LLM_model/llama.cpp/build/bin/llama-server | grep "not found"
```

아무것도 출력되지 않으면 정상입니다.

### 7. CUDA 경로 영구 저장

Conda `sava` 환경을 활성화할 때 CUDA 경로가 자동으로 설정되게 합니다.

```bash
conda env config vars set CUDA_HOME="$CONDA_PREFIX" CUDA_PATH="$CONDA_PREFIX" LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/targets/x86_64-linux/lib"
```

설정을 적용합니다.

```bash
conda deactivate && conda activate sava
```

다시 확인합니다.

```bash
echo "$CUDA_HOME"
```

```bash
nvcc --version
```

### 8. SAVA OS 경로 설정

`model_paths.json`은 다음과 같이 설정합니다.

```json
{
  "required": {
    "model_root": "/home/joseph/sava/LLM_model",
    "server_python": "/home/joseph/anaconda3/envs/sava/bin/python",
    "llama_server": "${model_root}/llama.cpp/build/bin/llama-server"
  }
}
```

실제 Python 경로가 다를 수 있으므로 아래 결과를 `server_python`에 넣는 것이 정확합니다.

```bash
which python
```

마지막으로 SAVA OS를 실행할 때도 `sava` 환경을 활성화합니다.

```bash
conda activate sava
```

```bash
cd /home/joseph/sava/SAVA_OS
```

```bash
python bin/savaosctl.pyc
```
