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
| `search_statute` | 법령(법률, 시행령 등)을 검색합니다. | `query`: 검색어 (예: "건축법") |
| `get_statute_detail` | 특정 법령의 상세 내용(조문 등)을 조회합니다. | `law_id`: 법령 일련번호 (검색 결과의 ID) |
| `get_statute_article` | 특정 법령의 특정 조문 내용을 조회합니다. | `law_id`: 법령 ID, `article_no`: 조문번호 (예: "20", "20-2") |
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
