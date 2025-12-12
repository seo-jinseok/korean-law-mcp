# Korean Law MCP Server (대한민국 법령/판례 검색 MCP 서버)

이 프로젝트는 국가법령정보센터(Open API)를 활용하여 대한민국 법령, 판례, 헌재결정례, 행정규칙, 자치법규를 검색하고 상세 내용을 조회할 수 있는 **MCP (Model Context Protocol) 서버**입니다.

## 🚀 주요 기능

- **법령 (Statutes)**: 현행 법령 검색 및 조문 조회
- **판례 (Precedents)**: 대법원 및 각급 법원 판례 검색 및 판시사항, 판결요지 조회
- **헌재결정례 (Constitutional Court Decisions)**: 헌법재판소 결정례 검색 및 전문 조회
- **자치법규 (Autonomous Laws)**: 각 지자체 조례/규칙 검색 및 조문 조회
- **행정규칙 (Administrative Rules)**: 중앙행정기관 훈령/예규/고시 검색 및 내용 조회

## 🛠️ 설치 및 설정

### 1. 사전 요구사항
* Python 3.10 이상
* 국가법령정보센터 Open API ID 필요 ([회원가입 및 신청](https://www.law.go.kr/))

### 2. 설치
프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 의존성을 설치합니다.

```bash
# 가상환경 생성 (권장)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 패키지 설치
pip install -e .
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 Open API ID를 설정해야 합니다. (또는 실행 시 환경변수로 주입)

```bash
# .env 파일 생성 (예시)
cp .env.example .env
# .env 파일 편집하여 OPEN_LAW_ID 입력
```

## 📦 배포 및 쉬운 사용 방법 (Easy Usage)

이 프로젝트는 `uv` 또는 `Docker`를 통해 쉽게 실행할 수 있도록 구성되어 있습니다.

### 방법 1: `uv` 또는 `pip`를 이용한 직접 실행 (권장)
GitHub 저장소에서 직접 실행할 수 있습니다. (PyPI 배포 시 `uvx korean-law-mcp` 가능)

```bash
# 로컬에 설치된 상태에서 실행 (개발자용)
korean-law-mcp

# Claude Desktop 설정 (Git 저장소 직접 연결)
# uv가 설치되어 있어야 합니다.
```

**Claude Desktop Config (`claude_desktop_config.json`) 예시**:

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/korean-law-mcp",
        "run",
        "korean-law-mcp"
      ],
      "env": {
        "OPEN_LAW_ID": "your_actual_api_id"
      }
    }
  }
}
```

### 방법 2: Docker 실행
Python 환경 설정 없이 Docker 컨테이너로 실행할 수 있습니다.

```bash
# 이미지 빌드
docker build -t korean-law-mcp .

# 실행 (환경변수 주입 필요)
docker run -e OPEN_LAW_ID=your_api_id -i korean-law-mcp
```

### 방법 3: PyPI 설치 (권장)
PyPI에 배포된 패키지를 `uvx`로 바로 실행할 수 있습니다.

```bash
# 실행
uvx korean-law-mcp
```

또는 `pip`로 설치하여 실행할 수도 있습니다.

```bash
pip install korean-law-mcp
korean-law-mcp
```

## 📚 제공 도구 (Tools)

이 서버는 다음과 같은 MCP 도구를 제공합니다.

| 도구 이름 (Tool) | 설명 (Description) | 인자 (Arguments) |
|---|---|---|
| `search_statute` | 법령(법률, 시행령 등)을 검색합니다. | `query`: 검색어 (예: "건축법") |
| `get_statute_detail` | 특정 법령의 상세 내용(조문 등)을 조회합니다. | `law_id`: 법령 일련번호 (검색 결과의 ID) |
| `search_precedent` | 판례를 검색합니다. | `query`: 검색어 (예: "사기") |
| `get_precedent_detail` | 특정 판례의 상세 내용(판시사항, 전문 등)을 조회합니다. | `prec_id`: 판례 일련번호 |
| `search_prec_const` | 헌법재판소 결정례를 검색합니다. | `query`: 검색어 (예: "위헌") |
| `get_prec_const_detail` | 특정 헌재결정례의 상세 내용을 조회합니다. | `detc_id`: 헌재결정례 일련번호 |
| `search_autonomous_law` | 자치법규(조례, 규칙)를 검색합니다. | `query`: 검색어 (예: "서울시 주차") |
| `get_autonomous_law_detail`| 특정 자치법규의 상세 내용을 조회합니다. | `law_id`: 자치법규 일련번호 |
| `search_admin_rule` | 행정규칙(고시, 훈령)을 검색합니다. | `query`: 검색어 (예: "식품안전") |
| `get_admin_rule_detail` | 특정 행정규칙의 상세 내용을 조회합니다. | `adm_id`: 행정규칙 일련번호 |

## 🖥️ 사용 방법 (Claude Desktop 예시)

`claude_desktop_config.json` 파일에 다음과 같이 설정을 추가하여 사용할 수 있습니다.

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/korean-law-mcp",
        "run",
        "korean-law-mcp"
      ],
      "env": {
        "OPEN_LAW_ID": "your_actual_api_id"
      }
    }
  }
}
```

또는 직접 Python으로 실행할 경우:

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "python3",
      "args": [
        "/absolute/path/to/korean-law-mcp/src/main.py"
      ],
      "env": {
        "OPEN_LAW_ID": "your_actual_api_id"
      }
    }
  }
}
```
