현재 서버 환경 기준으로 **LibreOffice TAR.GZ 파일을&#x20;**`/home/joseph/sava/`**에 두고**, 기존 Conda `sava` 환경에 `sudo` 없이 설치하면 돼.

https://drive.google.com/file/d/1Oh8LpTjYPRZ4rJgGp9wzwcUR_3tqj5R_/view?usp=sharing

## **1. TAR.GZ 파일 위치**

Google Drive에서 받은 `libreoffice.tar.gz` 파일을 서버의 다음 경로에 넣어.

```
/home/joseph/sava/libreoffice.tar.gz
```

즉, 기존 프로젝트 구조는 다음과 같아.

```
/home/joseph/sava/
├── libreoffice.tar.gz
├── LLM_model/
│   └── llama.cpp/
└── SAVA_OS/
```

서버에서 Google Drive 파일을 직접 다운로드할 거라면 다음 명령어로 진행해.

```
eval "$(conda shell.bash hook)" && conda activate sava
```

```
python -m pip install gdown
```

```
gdown "https://drive.google.com/file/d/1Oh8LpTjYPRZ4rJgGp9wzwcUR_3tqj5R_/view?usp=sharing" -O /home/joseph/sava/libreoffice.tar.gz
```

## **2. Conda sava 환경에 LibreOffice 설치**

**① 설치 디렉터리 생성**

```
mkdir -p "$CONDA_PREFIX/lo-install" "$CONDA_PREFIX/lo-root"
```

**② TAR.GZ 압축 해제**

```
tar -xzf /home/joseph/sava/libreoffice.tar.gz -C "$CONDA_PREFIX/lo-install"
```

**③ LibreOffice DEB 패키지 추출**

```
for deb in "$CONDA_PREFIX"/lo-install/LibreOffice_*/DEBS/*.deb; do dpkg-deb -x "$deb" "$CONDA_PREFIX/lo-root"; done
```

## **3. LibreOffice 실행 파일 연결**

**① 실행 파일 위치 확인**

```
LO_BIN=$(find "$CONDA_PREFIX/lo-root/opt" -path '*/program/soffice' -print -quit)
```

```
echo "$LO_BIN"
```

**② Conda 실행 경로에 연결**

```
printf '#!/bin/sh\nexec "%s" "$@"\n' "$LO_BIN" > "$CONDA_PREFIX/bin/libreoffice"
```

```
chmod +x "$CONDA_PREFIX/bin/libreoffice"
```

```
ln -sf libreoffice "$CONDA_PREFIX/bin/soffice"
```

## **4. 정상 설치 확인**

```
libreoffice --version
```

```
which libreoffice
```

예상 경로:

```
/home/joseph/anaconda3/envs/sava/bin/libreoffice
```

버전이 출력되면 실행 파일은 정상적으로 연결된 거야.

## **5. SAVA OS 실행**

```
cd /home/joseph/sava/SAVA_OS
```

```
python bin/savaosctl.pyc
```

이후 SAVA OS 로그에서 `LibreOffice 미설치` 경고가 사라지는지 확인하면 돼.

**참고:** TAR.GZ 안에는 Linux x86-64용 LibreOffice `.deb` 파일들이 들어 있어야 해. 시스템 라이브러리가 부족하면 실행 오류가 발생할 수 있지만, 기존 CUDA 12.8 및 llama-server 빌드 설정을 수정할 필요는 없어.
