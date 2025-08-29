# 컬럼 설명 작성 에이전트 플로우 다이어그램

## 전체 시스템 플로우

```mermaid
graph TD
    A[프로그램 시작] --> B{실행 모드 선택}
    
    B -->|배치 모드| C[배치 모드 실행]
    B -->|대화형 모드| D[대화형 모드 실행]
    B -->|기본 모드| E[기본 대화형 모드]
    
    C --> F[에이전트 실행]
    D --> F
    E --> F
    
    F --> G[초기 상태 설정]
    G --> H[LangGraph 워크플로우 시작]
    
    H --> I[analysis 노드]
    
    I --> J{현재 단계 확인}
    
    J -->|lineage_analysis| K[📊 1단계: 테이블 계보 분석]
    J -->|etl_analysis| L[🔧 2단계: ETL 쿼리 분석]
    J -->|metadata_collection| M[📋 3단계: 메타데이터 수집]
    J -->|column_tracking| N[🔗 4단계: 컬럼 계보 추적]
    J -->|description_writing| O[✍️ 5단계: 컬럼 설명 작성]
    
    K --> P[get_table_lineage 도구 호출]
    P --> Q[계보 데이터 저장]
    Q --> R[다음 단계: etl_analysis]
    
    L --> S[get_etl_query 도구 호출]
    S --> T[ETL 쿼리 데이터 저장]
    T --> U[다음 단계: metadata_collection]
    
    M --> V[get_table_metadata 도구 호출]
    V --> W[get_column_metadata 도구 호출]
    W --> X[메타데이터 저장]
    X --> Y[다음 단계: column_tracking]
    
    N --> Z[analyze_column_lineage 도구 호출]
    Z --> AA[원천 테이블 컬럼 메타데이터 수집]
    AA --> BB[다음 단계: description_writing]
    
    O --> CC[LLM을 통한 설명 작성]
    CC --> DD[다음 단계: human_review]
    
    R --> I
    U --> I
    Y --> I
    BB --> I
    DD --> I
    
    I --> EE[라우터: should_continue]
    
    EE -->|human_review| FF[human_review 노드]
    EE -->|completed| GG[프로그램 종료]
    EE -->|기타| I
    
    FF --> HH{피드백 확인}
    HH -->|피드백 있음| II[final_description 노드]
    HH -->|피드백 없음| JJ[기본 피드백 설정]
    JJ --> FF
    
    II --> KK[LLM을 통한 최종 설명 생성]
    KK --> LL[최종 결과 저장]
    LL --> GG
    
    GG --> MM[결과 반환]
```

## 상세 분석 노드 플로우

```mermaid
graph TD
    A[analysis_node 시작] --> B[현재 단계 확인]
    
    B --> C{단계별 분기}
    
    C -->|lineage_analysis| D[📊 테이블 계보 분석]
    C -->|etl_analysis| E[🔧 ETL 쿼리 분석]
    C -->|metadata_collection| F[📋 메타데이터 수집]
    C -->|column_tracking| G[🔗 컬럼 계보 추적]
    C -->|description_writing| H[✍️ 컬럼 설명 작성]
    
    D --> D1[get_table_lineage 도구 호출]
    D1 --> D2[계보 데이터 저장]
    D2 --> D3[다음 단계: etl_analysis]
    
    E --> E1[프로그램 ID 추출]
    E1 --> E2[get_etl_query 도구 호출]
    E2 --> E3[ETL 쿼리 데이터 저장]
    E3 --> E4[다음 단계: metadata_collection]
    
    F --> F1[get_table_metadata 호출]
    F1 --> F2[get_column_metadata 호출]
    F2 --> F3[메타데이터 저장]
    F3 --> F4[다음 단계: column_tracking]
    
    G --> G1[analyze_column_lineage 호출]
    G1 --> G2[원천 테이블 목록 추출]
    G2 --> G3[원천 테이블 컬럼 메타데이터 수집]
    G3 --> G4[유사 컬럼 검색]
    G4 --> G5[다음 단계: description_writing]
    
    H --> H1[수집된 정보 통합]
    H1 --> H2[LLM 프롬프트 생성]
    H2 --> H3[LLM 호출]
    H3 --> H4[설명 저장]
    H4 --> H5[다음 단계: human_review]
    
    D3 --> I[상태 반환]
    E4 --> I
    F4 --> I
    G5 --> I
    H5 --> I
```

## 사용자 상호작용 플로우

```mermaid
graph TD
    A[사용자 입력] --> B{입력 타입}
    
    B -->|배치 모드| C[자동 실행]
    B -->|대화형 모드| D[메뉴 선택]
    B -->|테이블명 변경| E[새 테이블명 입력]
    B -->|컬럼명 변경| F[새 컬럼명 입력]
    B -->|분석 시작| G[분석 프로세스 시작]
    B -->|피드백 입력| H[피드백 처리]
    B -->|종료| I[프로그램 종료]
    
    C --> J[에이전트 실행]
    D --> K[메뉴 표시]
    E --> L[테이블명 업데이트]
    F --> M[컬럼명 업데이트]
    G --> N[분석 워크플로우]
    H --> O[피드백 반영 재분석]
    
    K --> P{메뉴 선택}
    P -->|1| G
    P -->|2| E
    P -->|3| F
    P -->|4| I
    
    J --> Q[결과 출력]
    L --> K
    M --> K
    N --> R[결과 및 피드백 요청]
    O --> S[개선된 결과 출력]
    
    R --> T{피드백 입력 여부}
    T -->|있음| H
    T -->|없음| U[분석 완료]
    
    Q --> U
    S --> U
    U --> V[프로그램 종료]
```

## 도구 호출 플로우

```mermaid
graph TD
    A[도구 호출 시작] --> B{도구 타입}
    
    B -->|get_table_lineage| C[테이블 계보 조회]
    B -->|get_etl_query| D[ETL 쿼리 조회]
    B -->|get_table_metadata| E[테이블 메타데이터 조회]
    B -->|get_column_metadata| F[컬럼 메타데이터 조회]
    B -->|get_source_table_structure| G[원천 테이블 구조 조회]
    B -->|analyze_column_lineage| H[컬럼 계보 분석]
    
    C --> C1[데이터베이스 연결]
    C1 --> C2[계보 정보 쿼리]
    C2 --> C3[결과 반환]
    
    D --> D1[프로그램 ID 기반 쿼리]
    D1 --> D2[ETL 쿼리 정보 조회]
    D2 --> D3[결과 반환]
    
    E --> E1[테이블 정보 쿼리]
    E1 --> E2[테이블 구조 조회]
    E2 --> E3[결과 반환]
    
    F --> F1[컬럼 정보 쿼리]
    F1 --> F2[컬럼 상세 정보 조회]
    F2 --> F3[결과 반환]
    
    G --> G1[원천 테이블 목록 조회]
    G1 --> G2[테이블 구조 분석]
    G2 --> G3[결과 반환]
    
    H --> H1[컬럼 계보 추적]
    H1 --> H2[원천 컬럼 매핑]
    H2 --> H3[결과 반환]
    
    C3 --> I[상태 업데이트]
    D3 --> I
    E3 --> I
    F3 --> I
    G3 --> I
    H3 --> I
    
    I --> J[다음 단계 진행]
```

## 라우터 로직 플로우

```mermaid
graph TD
    A[should_continue 라우터] --> B[현재 단계 확인]
    
    B --> C{단계별 분기}
    
    C -->|human_review| D{피드백 존재 여부}
    C -->|completed| E[END - 종료]
    C -->|기타| F[analysis 노드로 이동]
    
    D -->|피드백 있음| G[final_description 노드로 이동]
    D -->|피드백 없음| H[human_review 노드에서 대기]
    
    F --> I[분석 계속]
    G --> J[최종 설명 생성]
    H --> K[사용자 입력 대기]
    
    I --> L[다음 분석 단계]
    J --> M[결과 저장 및 종료]
    K --> N[피드백 입력 대기]
    
    L --> O[라우터 재호출]
    M --> P[프로그램 완료]
    N --> O
```

## 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "사용자 인터페이스"
        A[main.py]
        B[run_agent.sh]
    end
    
    subgraph "에이전트 엔진"
        C[agent.py]
        D[LangGraph 워크플로우]
        E[LLM (GPT-4o-mini)]
    end
    
    subgraph "도구 모듈"
        F[tools.py]
        G[데이터베이스 연결]
    end
    
    subgraph "설정 및 유틸리티"
        H[config.py]
        I[database.py]
    end
    
    subgraph "데이터 소스"
        J[MySQL 데이터베이스]
        K[테이블 메타데이터]
        L[ETL 쿼리 정보]
    end
    
    A --> C
    B --> A
    C --> D
    D --> E
    D --> F
    F --> G
    G --> I
    I --> H
    I --> J
    J --> K
    J --> L
```

이 다이어그램들은 컬럼 설명 작성 에이전트의 전체적인 플로우와 각 구성 요소 간의 상호작용을 보여줍니다.
