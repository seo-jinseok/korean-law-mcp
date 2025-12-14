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

### 4. Agentic Prompts (Workflows) 🧠
Pre-defined templates for complex legal tasks.

- **`summarize_law`**
  - **Input**: Law ID (e.g., `265307`)
  - **Action**: Fetches full text and asks for a structured summary (key provisions, purpose).
- **`explain_legal_term`**
  - **Input**: Term (e.g., "선의의 제3자")
  - **Action**: Searches relevant laws/cases and explains the term's context.
- **`compare_laws`**
  - **Input**: Law ID 1, Law ID 2
  - **Action**: Fetches both and asks for a comparative analysis.
  
### 5. Knowledge Graph (Relationships) 🕸️
When viewing a Precedent (판례), related resources are automatically linked:
- **Referenced Articles (참조조문)**: The specific laws cited by the court.
- **Referenced Cases (참조판례)**: Other judicial precedents cited in the judgment.

These appear as a structured list at the bottom of the resource output, allowing easy navigation.

### 6. Client Usage (Claude Desktop etc.)
Configure your client to use `uv run korean-law-mcp`.
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
| `search_korean_law` | 통합 법률 검색 도구입니다. 상황에 따라 스마트하게 동작합니다.<br>1. **특정 조문 검색**: "고등교육법 제20조" -> 해당 조문의 전문을 즉시 반환합니다.<br>2. **통합 검색**: "학교폭력" -> 법령, 판례, 행정규칙을 아우르는 검색 결과를 요약하여 반환합니다. | `query`: 검색어 또는 찾고 싶은 법령/조문명 |
| `read_legal_resource` | 법적 리소스(법령 전체, 판례 전문 등)의 상세 내용을 읽어옵니다. 검색 결과에서 확인한 **Typed ID**를 사용합니다.<br>자동으로 리소스 내의 타 법령 참조(예: "제5조 참조")를 감지하여 함께 보여줍니다. | `resource_id`: 리소스 ID (예: `statute:12345`, `prec:67890`) |

- **한영 자동 변환**: "Civil Act Article 103"와 같이 영문으로 검색해도 자동으로 "민법 제103조"로 변환하여 검색합니다. (지원: Civil Act, Criminal Act, Commercial Act 등 주요 법령)

### Typed ID 시스템
이 서버는 리소스를 고유하게 식별하기 위해 `type:id` 포맷을 사용합니다.
- `statute:12345`: 법령 (Statutes)
- `prec:67890`: 판례 (Precedents)
- `admrul:54321`: 행정규칙 (Administrative Rules)
- `const:...`: 헌재결정례
- `ordin:...`: 자치법규

또는 `pipx`를 사용하는 경우:
```bash
pipx run korean-law-mcp
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
