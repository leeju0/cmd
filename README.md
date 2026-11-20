네. **12B 기본 구성에 필요한 모델만** 아래처럼 받으면 됩니다. Gemma는 다른 양자화 버전 없이 **`IQ4_NL` 본체와 `mmproj-F16` 두 파일만** 다운로드합니다.

SAVA OS 가상환경에서 실행하세요. CLI가 없다면 먼저 설치합니다.

```bash
python -m pip install "huggingface-hub[cli]==0.36.2"
```

### 1. LLM·OCR 공용 — [Gemma 4 12B IQ4_NL](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/tree/main)

```bash
huggingface-cli download unsloth/gemma-4-12b-it-GGUF \
  gemma-4-12b-it-IQ4_NL.gguf \
  mmproj-F16.gguf \
  --local-dir /data/LLM_model/gemma4
```

### 2. 음성 인식 — [Faster Whisper large-v3](https://huggingface.co/Systran/faster-whisper-large-v3/tree/main)

```bash
huggingface-cli download Systran/faster-whisper-large-v3 \
  --local-dir /data/LLM_model/faster-whisper-large-v3
```

### 3. 화자 분리 — [Speaker Diarization Community 1](https://huggingface.co/pyannote/speaker-diarization-community-1)

**먼저 위 모델 페이지에서 이용 조건에 동의**하고, 같은 계정의 토큰으로 로그인해야 합니다. 내부 `embedding/`도 함께 받아지므로 화자 임베딩은 별도로 다운로드하지 않습니다.

```bash
huggingface-cli login

huggingface-cli download pyannote/speaker-diarization-community-1 \
  --local-dir /data/LLM_model/speaker-diarization-community-1
```

### 4. 검색 임베딩 — [Multilingual E5 Small](https://huggingface.co/intfloat/multilingual-e5-small/tree/main)

설정·토크나이저·Safetensors는 받고, 사용하지 않는 ONNX/OpenVINO와 중복 가중치는 제외합니다.

```bash
huggingface-cli download intfloat/multilingual-e5-small \
  --local-dir /data/LLM_model/e5 \
  --exclude "onnx/*" "openvino/*" "pytorch_model.bin" ".eval_results/*"
```

### 5. Dense 검색 임베딩 — [Qwen3 Embedding 0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/tree/main)

```bash
huggingface-cli download Qwen/Qwen3-Embedding-0.6B \
  --local-dir /data/LLM_model/qwen3-embedding-0.6b
```

이 경로들은 현재 `model_paths.json`의 **`model_root: "/data/LLM_model"`** 설정과 맞습니다.

- OCR은 12B 모델을 공유하므로 추가 다운로드가 없습니다.
- 31B·이미지·영상·LOBE는 이번 기본 구성에서 받지 않아도 됩니다.
- **`llama-server` 실행 파일은 별도 준비**해야 합니다.
- 납품용 모델 버전까지 고정하려면 각 명령에 `--revision 검증된커밋해시`를 추가하세요.

  cd /data/leezoo/SAVA/SAVA_OS/dist/SAVA_OS

export SAVAOS_PYTHON=/data/anaconda3/envs/SAVA/bin/python3
export SAVAOS_CTL_CONFIG="$HOME/.config/savaos/pyc-test.json"

"$SAVAOS_PYTHON" bin/savaosctl.pyc
