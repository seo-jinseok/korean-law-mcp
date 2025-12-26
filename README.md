# ⚖️ 대한민국 법령/판례 검색기 (Korean Law MCP)

[![MCP Badge](https://lobehub.com/badge/mcp/seo-jinseok-korean-law-mcp)](https://lobehub.com/mcp/seo-jinseok-korean-law-mcp)


**"법률 정보를 누구나 쉽게."**

이 프로그램은 복잡한 대한민국 법령과 판례를 **채팅하듯이 쉽게 검색하고 찾아볼 수 있게 해주는 도구**입니다. Claude와 같은 AI와 연결하여 사용할 수 있습니다.

---

## 🚀 시작하기 (Quick Start)

가장 쉬운 사용 방법을 안내해 드립니다.

### 방법 1: `uv`를 이용한 자동 설치 (Mac/Linux/Windows 추천)
`uv`가 설치되어 있다면 가장 간편한 방법입니다. Claude 설정 파일에 아래 내용을 추가하세요. (Python 등을 직접 설치할 필요가 없습니다)

*   **설정 파일 경로**:
    *   MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "uvx",
      "args": [
        "korean-law-mcp"
      ],
      "env": {
        "OPEN_LAW_ID": "여기에_아이디를_넣으세요"
      }
    }
  }
}
```

### 방법 2: 윈도우 실행 파일 (설치 불필요)
`uv`나 Python 설정이 어려운 **윈도우(Windows) 사용자**를 위한 방법입니다.

1. [다운로드 페이지(Releases)](https://github.com/seo-jinseok/korean-law-mcp/releases)로 이동합니다.
2. 최신 버전의 **`korean-law-mcp.exe`** 파일을 다운로드합니다.
3. 다운로드한 파일의 경로를 복사해 둡니다. (예: `C:\Users\홍길동\Downloads\korean-law-mcp.exe`)
4. Claude Desktop 설정 파일(`claude_desktop_config.json`)을 열고 아래와 같이 적어주세요.

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "C:\\Users\\홍길동\\Downloads\\korean-law-mcp.exe",
      "env": {
        "OPEN_LAW_ID": "여기에_아이디를_넣으세요"
      }
    }
  }
}
```

---

## 🔑 필수 준비물: API 아이디
이 프로그램을 사용하려면 **국가법령정보센터 아이디**가 꼭 필요합니다.

1. [국가법령정보센터(law.go.kr)](https://www.law.go.kr/)에 접속하여 회원가입을 합니다.
2. [Open API 신청 페이지](https://www.law.go.kr/)에서 '사용 신청'을 합니다. (무료입니다)
3. 발급받은 아이디를 설정 파일의 `"OPEN_LAW_ID"` 부분에 넣어주세요.

---

## ✨ 주요 기능
이 도구로 할 수 있는 것들입니다.

*   **🔍 법령 검색**: "고등교육법 제20조 찾아줘"라고 물어보면 법 조항을 바로 보여줍니다.
*   **⚖️ 판례 찾기**: "학교폭력 관련 대법원 판례 찾아줘"라고 하면 관련 판례를 요약해 줍니다.
*   **📜 행정규칙/자치법규**: 훈령, 예규, 지자체 조례까지 모두 검색 가능합니다.
*   **📖 법령 용어**: "근로자가 뭐야?"라고 물으면 법적 정의를 정확히 알려줍니다.
*   **🤔 법령 해석례**: "이 법을 이렇게 해석해도 되나?" 궁금할 때 법제처의 유권해석 사례를 찾아줍니다.
*   **📎 서식/별표**: 법령에 첨부된 서식이나 표를 목록으로 보여줍니다.
*   **🔗 법률 그래프 탐색 (Deep Search)**: `explore_legal_chain` 도구를 사용하면 "고등교육법 제20조" 검색 시 **시행령/시행규칙** 등 위임된 하위 법령과 **참조된 내/외부 조문**까지 한 번에 찾아서 완벽한 보고서를 만들어줍니다.
*   **🤖 스마트 검색**: 법령 이름을 정확히 몰라도, "김영란법"처럼 흔히 부르는 이름으로 검색해도 알아서 찾아줍니다.

---

## 🛠️ 사용 가능한 도구 (Reference)

이 MCP 서버가 제공하는 주요 도구들의 상세 설명입니다.

| 도구 이름 | 설명 |
| :--- | :--- |
| `search_korean_law` | **(필수)** 법령, 판례, 행정규칙을 검색하는 가장 기본 도구입니다. "민법 제103조" 처럼 구체적으로 검색하면 바로 조문 내용을 보여줍니다. |
| `read_legal_resource` | `statute:12345`와 같은 **ID**를 사용하여 법령/판례의 **전문(Full Text)**을 가져옵니다. 긴 내용을 볼 때 사용합니다. |
| `explore_legal_chain` | **Deep Search**. 특정 조문과 연결된 하위 법령(시행령/규칙) 및 참조 조문을 한 번에 모두 찾아 분석합니다. |
| `get_statute_attachments` | 법령에 첨부된 **별표**나 **서식** 파일의 목록을 확인합니다. |
| `search_legal_terms` | 법률 용어의 정의를 찾아줍니다. |
| `search_statutory_interpretations` | 법제처의 법령 해석 사례를 검색합니다. |
| `get_external_links` | 🆕 법령/판례 ID로 **국가법령정보센터 공식 웹사이트 URL**을 생성합니다. 원본 출처 확인이나 공유용 링크가 필요할 때 사용합니다. |
| `get_article_history` | 🆕 법령의 **연혁 정보**(제개정구분, 시행일, 개정이유 등)를 조회합니다. "고등교육법 언제 개정됐어?"라고 물으면 사용합니다. |
| `compare_old_new` | 🆕 **신구조문대비**. 법령 개정 전후를 비교하여 어떤 조문이 어떻게 바뀌었는지 보여줍니다. |

---

## 🧠 AI 최적화 프롬프트 (System Prompt)

AI(Claude 등)가 이 도구를 더 똑똑하게 사용하도록 하려면, 아래 내용을 **시스템 프롬프트(System Prompt)**나 **Custom Instructions**에 추가해 주세요.

```text
## Role: Korean Law Expert (대한민국 법률 전문가)

You are an expert legal assistant with access to the 'Korean Law MCP' tools.
Always answer in Korean unless requested otherwise.

## Guidelines for Tool Usage:

1.  **Always Search First**: When asked a legal question, use 'search_korean_law' first.
    - If the user specifies an article (e.g., "민법 제103조"), search exactly for that.
    - If the query is broad (e.g., "학교폭력"), search for keywords.

2.  **ID-based Retrieval**:
    - The search result often provides Typed IDs (e.g., 'statute:12345').
    - To read the full content, MUST use 'read_legal_resource' with this ID.

3.  **Complex Analysis (Deep Search)**:
    - If the user asks for a comprehensive review of a specific provision (including its enforcement decrees/rules and references), USE 'explore_legal_chain'.
    - Example: "Analyze Article 20 of Higher Education Act strictly." -> 'explore_legal_chain("Higher Education Act Article 20")'

4.  **Formatting**:
    - Present legal texts clearly with blockquotes or code blocks if necessary.
    - Always cite the source (Law Name, Article Number).
```

---

## 👩‍💻 개발자 및 고급 사용자용 (Advanced)

소스 코드를 직접 수정하거나, PyPI에서 직접 설치하여 사용하고 싶은 경우의 안내입니다.

### 1. PyPI 설치 (pip)
`uv` 없이 일반 Python 환경에서 설치하려면:
```bash
pip install korean-law-mcp
```
설치 후에는 `claude_desktop_config.json`에서 `command`를 `"python", "-m", "korean_law_mcp"` 등으로 설정하여 연결합니다.

### 2. 로컬 개발 및 디버깅
이 레포지토리를 클론하여 개발하는 경우:

```bash
# 의존성 설치
uv sync

# 디버깅 (MCP Inspector 사용)
npx @modelcontextprotocol/inspector uv run korean-law-mcp
```

> **참고**: 이 프로그램은 단독 실행 시 아무런 반응이 없는 것이 정상입니다. (MCP 프로토콜 통신 대기 중)
> 반드시 **MCP Inspector**나 **Claude Desktop**을 통해 실행하세요.

---

> **문의 및 기여**: 버그 제보나 기능 제안은 [GitHub Issues](https://github.com/seo-jinseok/korean-law-mcp/issues)에 남겨주세요.
