사진을 보면 **SAVA OS는 정상 실행됐고, LibreOffice만 인식하지 못하는 상태**야.

문제가 되는 로그는 다음이야.

```
WARNING LibreOffice 미설치
/api/v1/convert/pdf 비활성
(문서 → PDF 변환 불가)
```

기존에 말한 것처럼 `sudo`**&#x20;없이&#x20;**`sava`**&#x20;Conda 가상환경에서 해결**하는 방법으로 알려줄게.

## **1. 먼저 LibreOffice 설치 여부 확인**

SAVA OS를 `Ctrl+C`로 종료한 다음 실행해.

```
conda activate sava

echo "$CONDA_PREFIX"

which libreoffice
which soffice

libreoffice --version
```

- 버전이 나오면: 설치는 되어 있으므로 SAVA OS의 실행 경로 문제일 가능성이 있어.
- `command not found`가 나오면: LibreOffice 실행 파일이 PATH에 없거나 실제로 설치되지 않은 상태야.

설치 파일이 다른 위치에 있는지도 확인해 봐.

```
find "$CONDA_PREFIX" "$HOME" /opt -name soffice 2>/dev/null | head
```

경로가 나온다면 새로 설치하지 않아도 돼.

## **2. 설치 파일이 없다면 sudo 없이 설치**

공식 LibreOffice 배포 파일을 Conda 환경 내부에 직접 압축 해제하는 방식이야. 아래 명령어는 Ubuntu 계열 x86_64 서버 기준이야.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://download.documentfoundation.org\&sz=32)

download.documentfoundation.org



```
conda activate sava

mkdir -p "$CONDA_PREFIX/lo-install"
mkdir -p "$CONDA_PREFIX/lo-root"

cd "$CONDA_PREFIX/lo-install"

wget -O libreoffice.tar.gz \
"https://download.documentfoundation.org/libreoffice/stable/26.8.3/deb/x86_64/LibreOffice_26.8.3_Linux_x86-64_deb.tar.gz"

tar -xzf libreoffice.tar.gz

for deb in LibreOffice_*/DEBS/*.deb; do
    dpkg-deb -x "$deb" "$CONDA_PREFIX/lo-root"
done
```

이 방법은 시스템에 설치하는 것이 아니라 Conda 환경 아래에 파일을 풀기 때문에 `sudo` 권한이 필요하지 않아. 다만 서버에 필요한 시스템 라이브러리가 없다면 추가 조치가 필요할 수 있어.

## **3. LibreOffice 실행 경로 연결**

```
LO_BIN=$(find "$CONDA_PREFIX/lo-root/opt" \
  -path '*/program/soffice' -print -quit)

echo "$LO_BIN"
```

실행 파일 경로가 출력되면 이어서 실행해.

```
printf '#!/bin/sh\nexec "%s" "$@"\n' "$LO_BIN" \
  > "$CONDA_PREFIX/bin/libreoffice"

chmod +x "$CONDA_PREFIX/bin/libreoffice"

ln -sf libreoffice "$CONDA_PREFIX/bin/soffice"

export PATH="$CONDA_PREFIX/bin:$PATH"

hash -r

libreoffice --version
```

정상이라면 LibreOffice 버전이 나와야 해.

## **4. SAVA OS 재실행**

기존에 SAVA OS를 실행했던 프로젝트 디렉터리로 이동해서 실행해.

```
export PATH="$CONDA_PREFIX/bin:$PATH"
export SAVAOS_PYTHON="$CONDA_PREFIX/bin/python"

"$SAVAOS_PYTHON" bin/savaosctl.pyc
```

이때 `bin/savaosctl.pyc`가 있는 디렉터리에서 실행해야 해.

**중요:** LibreOffice가 설치되어 있어도 SAVA OS 프로세스가 해당 실행 파일을 찾지 못하면 경고가 계속 발생할 수 있어. 따라서 `which libreoffice`와 `libreoffice --version`이 정상 동작하는 상태에서 재실행하는 게 핵심이야.

우선 **1번 명령어 결과부터 확인**하는 걸 추천해. 이미 설치되어 있다면 211MB 파일을 다시 다운로드할 필요 없이 경로 연결만으로 해결할 수 있어.
