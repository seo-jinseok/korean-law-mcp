# Korean Law MCP Server (대한민국 법령/판례 검색 MCP 서버)

국가법령정보센터(Open API)를 활용하여 대한민국 법령, 판례, 헌재결정례, 행정규칙, 자치법규를 검색하고 상세 내용을 조회할 수 있는 **MCP (Model Context Protocol) 서버**입니다.

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

## 🖥️ Claude Desktop 설정

`claude_desktop_config.json` 파일에 다음과 같이 추가하여 사용할 수 있습니다.

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

## 📚 제공 도구 (Tools)

| 도구 이름 | 설명 |
|---|---|
| `search_statute` | 법령(법률, 시행령 등) 검색 |
| `get_statute_detail` | 법령 조문 상세 조회 |
| `search_precedent` | 판례 검색 |
| `get_precedent_detail` | 판례 내용 상세 조회 |
| `search_prec_const` | 헌재결정례 검색 |
| `get_prec_const_detail` | 헌재결정례 상세 조회 |
| `search_autonomous_law` | 자치법규(조례) 검색 |
| `get_autonomous_law_detail`| 자치법규 상세 조회 |
| `search_admin_rule` | 행정규칙(고시) 검색 |
| `get_admin_rule_detail` | 행정규칙 상세 조회 |

---

> **개발자 정보**: 소스 코드 확인 및 기여는 [GitHub 저장소](https://github.com/seo-jinseok/korean-law-mcp)를 참고하세요.
