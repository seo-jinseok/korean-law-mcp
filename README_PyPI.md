# Korean Law MCP Server (대한민국 법령/판례 검색 MCP 서버)

이 프로젝트는 국가법령정보센터(Open API)를 활용하여 대한민국 법령, 판례, 헌재결정례, 행정규칙, 자치법규를 검색하고 상세 내용을 조회할 수 있는 **MCP (Model Context Protocol) 서버**입니다.

## 🚀 주요 기능

- **법령 (Statutes)**: 현행 법령 검색 및 조문 조회
- **판례 (Precedents)**: 대법원 및 각급 법원 판례 검색 및 판시사항, 판결요지 조회
- **헌재결정례 (Constitutional Court Decisions)**: 헌법재판소 결정례 검색 및 전문 조회
- **자치법규 (Autonomous Laws)**: 각 지자체 조례/규칙 검색 및 조문 조회
- **행정규칙 (Administrative Rules)**: 중앙행정기관 훈령/예규/고시 검색 및 내용 조회

## 🚀 빠른 시작 (Quick Start)

이 패키지는 `uvx`를 사용하여 설치 없이 즉시 실행할 수 있습니다.

```bash
uvx korean-law-mcp
```

또는 `pip`로 설치할 수 있습니다:

```bash
pip install korean-law-mcp
```

### 필수 조건
* **국가법령정보센터 Open API ID**가 필요합니다. ([회원가입 및 신청](https://www.law.go.kr/))
* 실행 시 환경 변수 `OPEN_LAW_ID`를 설정해야 합니다.

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

## 🖥️ 사용 방법 (Claude Desktop 예시)

`claude_desktop_config.json` 파일에 다음과 같이 설정을 추가하여 사용할 수 있습니다.

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "uvx",
      "args": [
        "korean-law-mcp"
      ],
      "env": {
        "OPEN_LAW_ID": "your_actual_api_id"
      }
    }
  }
}
```

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


---

> **개발자 정보**: 소스 코드 확인 및 기여는 [GitHub 저장소](https://github.com/seo-jinseok/korean-law-mcp)를 참고하세요.
