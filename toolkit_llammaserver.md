`sudo`가 없어도 가능합니다. 이미 `nvidia-smi`가 정상이고 CUDA 지원 버전이 12.8이라면, **Anaconda 환경 안에 CUDA Toolkit 12.8과 빌드 도구를 설치**하면 됩니다. 다만 GPU 드라이버 자체는 사용자 권한으로 설치할 수 없습니다.

아래에서는 Conda 환경 이름을 `SAVA`라고 가정합니다.

### 1. SAVA Conda 환경 활성화

```bash
eval "$(conda shell.bash hook)"
conda activate sava

python --version
nvidia-smi
```

### 2. CUDA Toolkit 12.8 사용자 설치

NVIDIA 공식 Conda 채널에서 정확히 12.8로 고정합니다. [NVIDIA 공식 Conda 설치 안내](https://docs.nvidia.com/cuda/archive/12.8.0/cuda-installation-guide-linux/index.html#conda-installation)

```bash
conda install -y \
  -c nvidia/label/cuda-12.8.0 \
  cuda
```

컴파일 도구도 Conda 환경에 설치합니다.

```bash
conda install -y \
  -c conda-forge \
  cmake \
  ninja \
  git \
  gcc_linux-64=12 \
  gxx_linux-64=12
```

설치 후 환경을 다시 활성화합니다.

```bash
conda deactivate
conda activate sava
```

확인:

```bash
which nvcc
nvcc --version

echo "$CONDA_PREFIX"
echo "$CC"
echo "$CXX"
```

`nvcc --version`에 `release 12.8`이 나오면 정상입니다.

### 3. llama.cpp 다운로드

아래 경로가 없어야 합니다.

```bash
ls -ld /home/joseph/sava/LLM_model/llama.cpp
```

없다면:

```bash
git clone https://github.com/ggml-org/llama.cpp.git \
  /home/joseph/sava/LLM_model/llama.cpp

git -C /home/joseph/sava/LLM_model/llama.cpp checkout \
  86b94708f22478f900b76ca02e316f4f3418faff
```

### 4. Conda CUDA로 llama-server 빌드

```bash
export CC="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cc"
export CXX="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-c++"

cmake \
  -S /home/joseph/sava/LLM_model/llama.cpp \
  -B /home/joseph/sava/LLM_model/llama.cpp/build \
  -G Ninja \
  -DGGML_CUDA=ON \
  -DCUDAToolkit_ROOT="$CONDA_PREFIX" \
  -DCMAKE_CUDA_COMPILER="$CONDA_PREFIX/bin/nvcc" \
  -DCMAKE_CUDA_HOST_COMPILER="$CXX" \
  -DCMAKE_C_COMPILER="$CC" \
  -DCMAKE_CXX_COMPILER="$CXX" \
  -DCMAKE_BUILD_RPATH="$CONDA_PREFIX/lib;$CONDA_PREFIX/targets/x86_64-linux/lib"

cmake \
  --build /home/joseph/sava/LLM_model/llama.cpp/build \
  --target llama-server \
  -j 2
```

### 5. 실행 확인

```bash
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

/home/joseph/sava/LLM_model/llama.cpp/build/bin/llama-server --version
```

라이브러리 누락 여부도 확인합니다.

```bash
ldd /home/joseph/sava/LLM_model/llama.cpp/build/bin/llama-server \
  | grep "not found"
```

아무것도 출력되지 않으면 정상입니다.

### 6. CUDA 경로를 Conda 환경에 영구 저장

```bash
conda env config vars set \
  CUDA_HOME="$CONDA_PREFIX" \
  CUDA_PATH="$CONDA_PREFIX" \
  LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/targets/x86_64-linux/lib"

conda deactivate
conda activate sava
```

마지막으로 `model_paths.json`:

```json
"model_root": "/home/joseph/sava/LLM_model",
"llama_server": "${model_root}/llama.cpp/build/bin/llama-server"
```

이 방법은 `/usr/local/cuda`나 시스템 패키지를 건드리지 않으며 `sudo`가 필요 없습니다. 단, `nvidia-smi` 자체가 실패한다면 드라이버 문제라서 서버 관리자 권한이 필요합니다.
