# SAVA OS 설정 파일

import os
from savaos.model_paths import model_path as deployment_path
from savaos.server_config import load_config as load_server_config, internal_port_defaults, default_api_port

_server_settings = load_server_config()
# Import-time defaults must not reject an unused candidate: main/CLI validate
# the effective port combination after applying saved selections and overrides.
_server_ports = internal_port_defaults(default_api_port(_server_settings), _server_settings)


def _env_bool(name: str, default: bool) -> bool:
    raw_value = os.environ.get(name, str(default)).strip().lower()
    if raw_value in {"1", "true", "yes", "on"}:
        return True
    if raw_value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name}는 boolean 값이어야 합니다: {raw_value!r}")


def _env_choice(name: str, default: str, choices: set[str]) -> str:
    value = os.environ.get(name, default).strip().lower()
    if value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{name}는 다음 값 중 하나여야 합니다: {allowed}")
    return value


def _env_int(name: str, default: int, *, minimum: int) -> int:
    raw_value = os.environ.get(name, str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name}는 정수여야 합니다: {raw_value!r}") from exc
    if value < minimum:
        raise ValueError(f"{name}는 {minimum} 이상이어야 합니다: {value}")
    return value


class AppConfig:
    """서버 앱 메타 설정."""

    app_name = "SAVA OS"
    app_version = "1.0.12"
    api_version = "v1"

# 토큰 만료시간 (분)
ACCESS_TOKEN_EXPIRE_MINUTES = 600

# ALLOW IPs
IP_WHITELIST_ENABLED = False
ALLOWED_IPS = {"127.0.0.1", "10.80.76.168", "10.80.76.170"}  # LAB
ALLOWED_IPS.add("117.16.196.165")  # INU
ALLOWED_IPS.add("117.16.244.77")  # SAVA OS server self
ALLOWED_IPS.add("211.234.195.16")

# Default Table list
PAGE_OFFSET = 15
PAGE_MAX_OFFSET = 100


class Default:
    TBL_PRIFIX = "SAVA_"


class Service:
    _base_port = default_api_port(_server_settings)  # First candidate in SAVA_OS/server_config.json
    prod_port = str(_base_port)
    # test_port = "8001"

    # 내부 서버 포트 자동 할당: 800X → 80X0 (10포트 범위, 서버 추가 시 +1씩 확장)
    _internal_base = (_base_port // 100) * 100 + (_base_port % 10) * 10

    # WebSocket keepalive(ping/pong) 설정 — uvicorn.run 에 전달.
    # Workflow 도구 실행이 TA Electron 메인 프로세스에서 수행되는데, 무거운 도구(브라우저 조작 등)로
    # 일시 블로킹되면 pong 응답이 지연되어 uvicorn 기본 ping_timeout(20초)에 걸려 WS가 조기 종료된다.
    # ping 은 20초마다 계속 보내 죽은 연결은 감지하되, timeout 은 15분으로 늘려 긴 브라우저
    # 추출/검증 중 Electron 메인 이벤트 루프가 일시 정체되어도 정상 Workflow를 끊지 않는다.
    # 애플리케이션 heartbeat와 실제 송수신 실패가 죽은 연결을 별도로 감지한다.
    ws_ping_interval = float(os.environ.get("SAVAOS_WS_PING_INTERVAL", "20"))
    ws_ping_timeout = float(os.environ.get("SAVAOS_WS_PING_TIMEOUT", "900"))


class LLMConfig:
    """LLM 설정"""
    # 기본 모델 설정 (llama_cpp)
    # default_provider = "llama_cpp"
    default_provider = "llama_server"
    # default_provider = "vllm"
    default_model_path = deployment_path("llm")

    default_model_name = "gemma-4-12b-it-IQ4_NL"  # 모델 식별 이름
    
    default_n_ctx = _server_settings["llm_context_tokens"]
    
    # GPU 설정
    default_gpu_id = [str(_server_settings["available_gpu_ids"][0])]
    n_gpu_layers = -1  # -1이면 모든 레이어를 GPU에 로드
    
    
    # 생성 기본 파라미터 (개별 호출에서 명시적으로 지정하지 않을 때 사용)
    # 생성 길이 정책의 공통 기본값. 개별 API/에이전트가 명시하지 않을 때 사용한다.
    default_max_tokens = _server_settings["llm_max_output_tokens"]
    # Direct-vision final answers need enough room to describe dense screenshots
    # and document images after the response plan and evidence have been packed.
    multimodal_min_output_tokens = 4000
    # Conservative context reservation for llama-server vision inputs. TA sends
    # images with a maximum 2048px edge; reserving one token per 32x32 patch keeps
    # image input from being treated as the single textual token "[image]".
    multimodal_vision_patch_size = 32
    multimodal_image_token_overhead = 64
    multimodal_unknown_image_tokens = 2048
    # 자동 복구 시 프롬프트와 생성 결과가 슬롯별 context를 넘지 않도록 남겨둘 여유.
    continuation_context_reserve = 256
    # length 종료 후 자동 재호출/이어쓰기의 최대 횟수.
    max_length_recovery_attempts = 3
    default_temperature = 0.1
    default_top_p = 0.9
    
    # LLM 호출 타임아웃 (초) - HTTP 클라이언트, 서버 대기, WebSocket 등 모든 LLM 호출에 적용
    default_llm_timeout = 310


class OCRConfig:
    """OCR 모델 설정 (Multimodal Vision-Language Model)"""
    # OCR 모델 활성화 여부
    enabled = True
    
    # OCR 모델 경로 (Gemma4 multimodal GGUF)
    model_path = deployment_path("ocr")
    
    # Vision Projector 경로 (mmproj)
    mmproj_path = deployment_path("ocr_mmproj")
    
    # 모델 식별 이름
    model_name = "gemma-4-12b-it-IQ4_NL"

    # Vision chat handler. Gemma4 multimodal uses llama-cpp-python's Gemma4ChatHandler.
    chat_handler = "gemma4"
    
    # 컨텍스트 길이 (이미지 토큰 포함)
    n_ctx = 7000
    
    # GPU 설정
    gpu_id = "0"
    n_gpu_layers = -1
    
    # 생성 파라미터
    default_max_tokens = 2048
    default_description_max_tokens = 800
    default_temperature = 0.1


class SenseNovaImageConfig:
    """Manually loaded, GPU-isolated SenseNova generation and editing settings."""

    model_path = os.environ.get(
        "SAVAOS_SENSENOVA_IMAGE_MODEL_PATH",
        deployment_path("sensenova"),
    )
    model_name = os.environ.get(
        "SAVAOS_SENSENOVA_IMAGE_MODEL_NAME",
        "SenseNova-U1.5-8B-MoT",
    )
    runtime_python = os.environ.get(
        "SAVAOS_SENSENOVA_IMAGE_PYTHON",
        deployment_path("sensenova_python"),
    )
    enabled = bool(model_path and runtime_python) and _env_bool("SAVAOS_SENSENOVA_IMAGE_ENABLED", True)
    allowed_gpu_ids = tuple(map(str, _server_settings["available_gpu_ids"]))
    device = "cuda:0"
    dtype = _env_choice(
        "SAVAOS_SENSENOVA_IMAGE_DTYPE",
        "bfloat16",
        {"bfloat16", "float16", "float32"},
    )
    vram_mode = _env_choice(
        "SAVAOS_SENSENOVA_IMAGE_VRAM_MODE",
        "fast",
        {"full", "fast", "balanced", "low"},
    )
    cuda_allocator_conf = os.environ.get(
        "SAVAOS_SENSENOVA_IMAGE_CUDA_ALLOC_CONF",
        "expandable_segments:True",
    ).strip()
    default_height = 2048
    default_width = 2048
    default_num_inference_steps = _env_int(
        "SAVAOS_SENSENOVA_IMAGE_STEPS",
        50,
        minimum=1,
    )
    default_guidance_scale = float(
        os.environ.get(
            "SAVAOS_SENSENOVA_IMAGE_GUIDANCE_SCALE",
            "4.0",
        )
    )
    default_image_guidance_scale = float(
        os.environ.get("SAVAOS_SENSENOVA_IMAGE_GUIDANCE_SCALE", "1.0")
    )
    default_timestep_shift = float(
        os.environ.get("SAVAOS_SENSENOVA_TIMESTEP_SHIFT", "3.0")
    )
    max_reference_images = _env_int(
        "SAVAOS_SENSENOVA_MAX_REFERENCE_IMAGES",
        8,
        minimum=1,
    )
    min_dimension = 1152
    max_dimension = 3456
    output_sizes = {
        "1:1": (2048, 2048),
        "16:9": (2720, 1536),
        "9:16": (1536, 2720),
        "3:2": (2496, 1664),
        "2:3": (1664, 2496),
        "4:3": (2368, 1760),
        "3:4": (1760, 2368),
        "2:1": (2880, 1440),
        "1:2": (1440, 2880),
        "3:1": (3456, 1152),
        "1:3": (1152, 3456),
    }
    allowed_sizes = tuple(output_sizes.values())


class LTXVideoConfig:
    """LTX-2.5 POC video model settings."""

    model_root = os.environ.get(
        "SAVAOS_LTX_VIDEO_MODEL_ROOT",
        deployment_path("ltx"),
    )
    # Keep the highest-quality Dev + TwoStagesHQ pipeline, but use the measured
    # 896x512 A6000 default and 15 Res2s stage-1 steps for the POC. Jobs may
    # select another fixed output bucket below; 1080p is
    # intentionally not offered because it is several times slower.
    model_name = "LTX-2.5-Dev-TwoStagesHQ-POC"
    profile = "two-stages-hq-poc"
    output_width = _env_int("SAVAOS_LTX_VIDEO_WIDTH", 896, minimum=64)
    output_height = _env_int("SAVAOS_LTX_VIDEO_HEIGHT", 512, minimum=64)
    output_sizes = {
        "16:9": (896, 512),
        "3:2": (768, 512),
        "4:3": (704, 512),
        "1:1": (640, 640),
        "3:4": (512, 704),
        "2:3": (512, 768),
        "9:16": (512, 896),
    }
    allowed_sizes = tuple(output_sizes.values())
    num_inference_steps = _env_int("SAVAOS_LTX_VIDEO_STEPS", 15, minimum=1)
    max_batch_size = int(
        _env_choice(
            "SAVAOS_LTX_VIDEO_MAX_BATCH_SIZE",
            "4",
            {"1", "2", "3", "4"},
        )
    )
    frame_rate = 24
    quantization = "bf16"
    max_duration_seconds = 60
    max_reference_images = _env_int(
        "SAVAOS_LTX_VIDEO_MAX_REFERENCE_IMAGES",
        24,
        minimum=1,
    )
    # DiffVAE is lazy: its largest allocation happens while the returned frame
    # iterator is consumed, after both diffusion stages have completed.  Use a
    # conservative, deterministic memory budget instead of sizing tiles from
    # an earlier/free-memory snapshot.  The LTX runtime derives legal temporal
    # and spatial tiles (including DiffVAE's checkpoint-specific halo) for the
    # requested frame count from this budget.  24 GiB uses the measured A6000
    # headroom while leaving room for latents, weights and allocator overhead.
    vae_decode_budget_gib = _env_int(
        "SAVAOS_LTX_VIDEO_VAE_DECODE_BUDGET_GIB",
        24,
        minimum=8,
    )
    cuda_allocator_conf = os.environ.get(
        "SAVAOS_LTX_VIDEO_CUDA_ALLOC_CONF",
        "expandable_segments:True",
    ).strip()
    runtime_python = os.environ.get(
        "SAVAOS_LTX_VIDEO_PYTHON",
        deployment_path("ltx_python"),
    )
    offload_mode = _env_choice(
        "SAVAOS_LTX_VIDEO_OFFLOAD",
        "cpu",
        {"none", "cpu", "disk"},
    )
    allowed_gpu_ids = tuple(map(str, _server_settings["available_gpu_ids"]))
    component_paths = {
        name: os.path.relpath(deployment_path("ltx_" + name), deployment_path("ltx"))
        if deployment_path("ltx_" + name) and deployment_path("ltx") else ""
        for name in ("transformer", "text_encoder", "video_vae", "audio_vae", "distilled_lora", "spatial_upsampler")
    }
    enabled = bool(model_root and runtime_python and all(component_paths.values())) and _env_bool("SAVAOS_LTX_VIDEO_ENABLED", True)


class LlamaServerConfig:
    """llama-server (llama.cpp C++ 서버) 설정"""
    server_binary = deployment_path("llama_server")

    # 비전(멀티모달) 프로젝터 GGUF 경로. 설정하면 서버 기동 시 `--mmproj` 로 로드되어
    # /v1/chat/completions 의 image_url 입력(비주얼 Set-of-Marks 등)을 처리할 수 있다.
    # 비워두면(기본) 텍스트 전용으로 기동한다. gemma 모델과 짝이 맞는 mmproj 파일을 지정해야 한다.
    mmproj_path = deployment_path("llm_mmproj")

    default_host = "127.0.0.1"
    default_port = _server_ports["llama_server_port"]
    
    parallel_slots = _server_settings["llm_parallel_slots"]
    cont_batching = True
    
    default_n_ctx = LLMConfig.default_n_ctx
    default_n_gpu_layers = -1
    
    server_start_timeout = 120
    request_timeout = 300


class VLLMConfig:
    """vLLM 서버 설정"""
    server_command = "vllm"
    server_subcommand = "serve"

    default_host = "127.0.0.1"
    default_port = _server_ports["vllm_port"]

    default_model = ""  # 비어있으면 LLMConfig.default_model_path 사용
    default_tokenizer = ""  # 공식 문서에서는 GGUF 파일인 경우 별도 지정을 권장하지만, 대부분의 경우는 정상 동작함.

    tensor_parallel_size = 1
    max_model_len = 10000

    quantization = None  # "awq", "gptq", "fp8", None, 보통은 자동 감지가 되지만 안되는 경우를 위한 옵션

    gpu_memory_utilization = 0.80
    max_num_seqs = 8

    server_start_timeout = 300
    request_timeout = 600

    enable_prefix_caching = True
    dtype = "auto"


class WhisperConfig:
    """STT 설정 (faster-whisper + pyannote diarization + Gemma 후처리).

    배포 환경에서 바꾸는 값(모델 경로·GPU·언어)과 기능 on/off 토글만 둔다.
    세부 튜닝 상수(디코딩·VAD·화자 후처리·Gemma 임계값)는 각 로직이 사는 STT 모듈
    상단의 모듈 상수에서 수정한다.
    """
    enabled = True

    # 전사 모델
    model_path = deployment_path("whisper")
    model_name = "faster-whisper-large-v3"

    # 화자 분할(pyannote). 끄면 Whisper 전사만 수행한다.
    diarization_enabled = True
    # 화자 수는 요청값이 없으면 자동 추정한다.
    diarization_model_path = deployment_path("diarization")
    diarization_model_name = "speaker-diarization-community-1"

    # 화자 임베딩(centroid) 모델 경로. pyannote diarization 모델 내부 임베딩과 같은 가중치를 별도 Inference로 로드한다.
    # 화자 재라벨 세부 임계값은 agents/STT/speaker/speaker_centroid.py에서 관리한다.
    centroid_embedding_path = deployment_path("speaker_embedding")

    # GPU / 정밀도 / 언어
    # device: "auto"이면 LLMConfig.default_gpu_id를 따라가고, 명시 지정도 가능("0", "0,1", "cpu").
    device = "auto"
    device_index = 0
    compute_type = "float16"
    cpu_compute_type = "int8"
    language = None  # None이면 자동 감지, "ko"/"en" 등으로 고정 가능

    # 전사 텍스트를 대상으로 한 Gemma 후처리 기능 토글.
    gemma_refine_enabled = True           # 텍스트 정제(규칙 정제 + 필요 구간만 LLM)
    gemma_speaker_check_enabled = True    # 의심 구간 화자 경계 텍스트 재검토

    @classmethod
    def resolve_gpu_ids(cls) -> str:
        """실제 사용할 GPU ID 문자열을 반환 (CUDA_VISIBLE_DEVICES 형식)"""
        if cls.device == "auto":
            return ",".join(LLMConfig.default_gpu_id)
        return cls.device


class StreamingSTTConfig:
    """Streaming STT 배포 환경에서 조정하는 설정."""

    enabled = _env_bool("SAVAOS_STT_STREAMING_ENABLED", True)
    # 마지막 Streaming STT 세션이 끝나면 Whisper/pyannote/화자 임베딩을
    # 자동 해제한다. 다음 회의 시작 시 다시 로드되며, 상시 VRAM 점유를 피한다.
    auto_unload_after_session = _env_bool(
        "SAVAOS_STT_STREAMING_AUTO_UNLOAD_AFTER_SESSION",
        True,
    )
    model_mode = _env_choice(
        "SAVAOS_STT_STREAMING_MODEL_MODE",
        "shared",
        {"shared", "dedicated"},
    )
    model_path = os.environ.get(
        "SAVAOS_STT_STREAMING_MODEL_PATH",
        deployment_path("streaming_whisper"),
    )
    language = str(
        os.environ.get("SAVAOS_STT_STREAMING_LANGUAGE")
        or WhisperConfig.language
        or "ko"
    ).strip().lower()
    device = _env_choice(
        "SAVAOS_STT_STREAMING_DEVICE",
        "auto",
        {"auto", "cpu", "cuda"},
    )
    device_index = _env_int(
        "SAVAOS_STT_STREAMING_DEVICE_INDEX",
        0,
        minimum=0,
    )
    max_sessions = _env_int(
        "SAVAOS_STT_STREAMING_MAX_SESSIONS",
        4,
        minimum=1,
    )
    max_recording_seconds = _env_int(
        "SAVAOS_STT_STREAMING_MAX_RECORDING_SECONDS",
        14400,
        minimum=1,
    )


class EmbeddingConfig:
    """임베딩 모델 설정"""
    # E5 모델 경로 (로컬 경로 또는 HuggingFace 모델명)
    # 로컬 경로 예: "/data/LLM_model/e5/multilingual-e5-small"
    # HuggingFace 예: "intfloat/multilingual-e5-small"
    e5_model_path = deployment_path("e5")
    # 로컬 경로가 존재하지 않을 때 자동 다운로드할 HuggingFace 모델명 폴백
    e5_hf_fallback = "intfloat/multilingual-e5-small"
    e5_dimension = 384


class DenseEmbeddingConfig:
    """무상태 dense 임베딩(`/api/v1/ma/retrieve/dense-*`) 설정.

    device "auto"는 서버에 할당된 GPU(CUDA_VISIBLE_DEVICES 기준 cuda:0)를 쓰고, GPU가 없으면 cpu.
    dtype은 model_version에 포함되므로 바꾸면 클라이언트 캐시가 전부 재인코딩된다.
    """
    qwen3_enabled = _env_bool("SAVAOS_DENSE_QWEN3_ENABLED", True)
    qwen3_path = os.environ.get("SAVAOS_DENSE_QWEN3_PATH", deployment_path("qwen_embedding"))
    qwen3_device = os.environ.get("SAVAOS_DENSE_QWEN3_DEVICE", "auto").strip()
    qwen3_dtype = _env_choice("SAVAOS_DENSE_QWEN3_DTYPE", "fp32", {"fp32", "fp16", "bf16"})
    qwen3_doc_batch = _env_int("SAVAOS_DENSE_QWEN3_DOC_BATCH", 8, minimum=1)

    max_texts = 32
    max_body_bytes = 512 * 1024


class KiwiConfig:
    """Kiwi 형태소 분석기 설정 (문서검색 태그 인덱스 토크나이저)"""
    # KIWI_ARCH_TYPE 강제값. 빈 문자열이면 서브프로세스 프로브로 자동 결정
    # (일부 CPU에서 SIMD 자동감지가 Illegal instruction 크래시를 일으킴 — 예: Arrow Lake)
    kiwi_arch = ""


class ServerConfig:
    """다중 서버 설정 (벤치마크 병렬 처리용)"""
    # 기본 서버 설정: [{"url": "http://...", "workers": N}, ...]
    # None이면 --server_url과 --num_workers 사용
    default_server_config = None
    

    default_server_config = [
        {"url": f"http://localhost:{Service._base_port}", "workers": 2},
        {"url": f"http://117.16.244.157:{Service._base_port}", "workers": 2},
    ]

class BenchmarkRecoveryConfig:
    """GAIA/WideSearch의 새 실행에 적용할 Adaptive Recovery 기본 설정.

    변경 후 SAVA OS 서버를 재시작한다. 실행 중인 run은 시작 시 설정을 유지한다.
    명시적인 API 요청의 adaptive_recovery_enabled/recovery_mode/limits는 우선한다.
    """

    enabled = False  # True: enforce(능동 복구), False: off(기존 실행 정책)
    # OFF에도 같은 run 전체 예산을 적용한다. None은 해당 항목의 상한 없음.
    limits = {
        "max_model_calls": 160,
        "max_tool_calls": 80,
        "max_repair_actions": 24,
        "time_limit_seconds": 1800,
        "same_failure_recurrence": 4,
    }


class BrowserConfig:
    """에이전트 브라우저 조작 방식 설정.

    Workflow SEA가 에이전트(Agent) 인앱 브라우저를 조작할 때 어떤 도구/프롬프트를 사용할지 결정한다.
    - "som"    : 비주얼 Set-of-Marks. 스크린샷에 번호 배지를 오버레이해 멀티모달 LLM(gemma)이
                 화면을 보고 번호로 조작한다. 도구는 browser_agent_som 만 노출한다.
    - "legacy" : 기존 셀렉터 기반. browser_agent_open + browser_agent_action 을 노출한다.
    멀티모달 모델이 아니거나 스크린샷 전송이 불가한 환경에서는 "legacy" 로 둔다.
    """
    manipulation_mode = "som"  # "som" | "legacy"


class UsageConfig:
    """Chat usage 적재·조회 설정"""
    enabled = True
    db_path = "savaos/data/usage.db"
