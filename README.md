# 1. LLM·OCR 공용: Gemma 4 12B IQ4_NL + projector만 다운로드
huggingface-cli download unsloth/gemma-4-12b-it-GGUF --include "gemma-4-12b-it-IQ4_NL.gguf" --local-dir /home/joseph/sava/LLM_model/gemma4

huggingface-cli download unsloth/gemma-4-12b-it-GGUF mmproj-F16.gguf --local-dir /home/joseph/sava/LLM_model/gemma4

# 2. 음성 인식: Faster Whisper large-v3
huggingface-cli download Systran/faster-whisper-large-v3 \
  --local-dir /home/joseph/sava/LLM_model/faster-whisper-large-v3

# 3. 화자 분리 + 화자 임베딩
huggingface-cli download pyannote/speaker-diarization-community-1 \
  --local-dir /home/joseph/sava/LLM_model/speaker-diarization-community-1

# 4. 검색 임베딩: E5 Small
# 미사용 ONNX/OpenVINO와 중복 가중치 제외
huggingface-cli download intfloat/multilingual-e5-small \
  --local-dir /home/joseph/sava/LLM_model/e5 \
  --exclude "onnx/*" "openvino/*" "pytorch_model.bin" ".eval_results/*"

# 5. Dense 검색 임베딩: Qwen3 Embedding 0.6B
huggingface-cli download Qwen/Qwen3-Embedding-0.6B \
  --local-dir /home/joseph/sava/LLM_model/qwen3-embedding-0.6b


# ctl실행
"$SAVAOS_PYTHON" bin/savaosctl.pyc

# 라마서버 커밋: 86b94708f22478f900b76ca02e316f4f3418faff
https://drive.google.com/file/d/1Qu5183rt4gxs3chaLTtS__QTn2UBZz4Q/view?usp=sharing



# 방화벽 설정
New-NetFirewallRule -DisplayName "SAVA Allow TCP 8005" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8005
Test-NetConnection -ComputerName SERVER_IP -Port 8000

# config 파일 
https://drive.google.com/file/d/1Jdwm7n22eWqJtIC8b9yYiPFR0PqnmQtG/view?usp=sharing
