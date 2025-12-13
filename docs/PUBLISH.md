# PyPI 배포 가이드 (Publishing to PyPI)

PyPI(Python Package Index)에 패키지를 배포하면 사용자들이 `pip install korean-law-mcp` 또는 `uvx korean-law-mcp` 명령어로 매우 쉽게 설치하고 실행할 수 있습니다.

## 0. 자동화 스크립트 사용 (권장)
`scripts/publish.py`를 사용하면 문서 동기화, 커밋, 태깅, 빌드, PyPI 업로드를 한 번에 처리할 수 있습니다.

```bash
# 버전이 자동으로 펌프되지는 않으므로 pyproject.toml 버전 수정 후 실행
python3 scripts/publish.py
```

## 1. 수동 배포: 사전 준비

### `pyproject.toml` 정보 수정
`pyproject.toml` 파일을 열어 다음 항목들을 **반드시** 본인의 정보에 맞게 수정해주세요.
- `authors`: 이름과 이메일
- `urls`: GitHub 저장소 주소
- `description`: 패키지 설명 (필요 시 수정)

### 배포 도구 설치
패키지 빌드 및 업로드를 위해 `build` 와 `twine`을 설치합니다.

```bash
pip install build twine
```

## 2. 패키지 빌드

다음 명령어로 배포용 파일(Wheel 및 Source Archive)을 생성합니다.

```bash
python3 -m build
```

명령어가 성공하면 `dist/` 디렉토리에 `.whl` 파일과 `.tar.gz` 파일이 생성됩니다.

## 3. PyPI 업로드

### 테스트 배포 (TestPyPI) - 권장
실제 PyPI에 올리기 전에 테스트 서버에 먼저 올려보는 것이 좋습니다.

```bash
python3 -m twine upload --repository testpypi dist/*
```

### 실전 배포 (Real PyPI)
준비가 완료되면 실제 PyPI에 배포합니다. (PyPI 계정이 필요합니다)

```bash
python3 -m twine upload dist/*
```

## 4. 사용자 안내
배포가 완료되면 `README.md`의 설치 방법을 다음과 같이 업데이트할 수 있습니다.

```bash
# 별도 설치 없이 실행 (uv 사용 시)
uvx korean-law-mcp

# 또는 pip 설치 후 실행
pip install korean-law-mcp
korean-law-mcp
```
