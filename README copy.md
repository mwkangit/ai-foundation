# TableF product_category 컬럼 설명 작성 에이전트

LangGraph 기반 상태 기반 워크플로우로 구현된 컬럼 설명 생성 시스템입니다. ETL 과정을 추적하여 테이블의 컬럼에 대한 상세한 설명을 자동으로 생성합니다.

## 🎯 주요 기능

- **ETL 과정 추적**: `pgm_qry_mst`, `pgm_qry_tbl_dtl` 테이블을 통한 계보 분석
- **메타데이터 수집**: `tbl_mst`, `col_mst` 테이블에서 원천 데이터 정보 수집
- **상태 기반 워크플로우**: LangGraph를 활용한 단계별 처리
- **Human-in-the-Loop**: 사용자 피드백을 통한 설명 품질 향상
- **MySQL 연동**: 원천 데이터베이스 직접 접근

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   사용자 입력   │───▶│  LangGraph      │───▶│  MySQL          │
│                 │    │  에이전트       │    │  데이터베이스   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  OpenAI LLM     │
                       │  (GPT-4o-mini)  │
                       └─────────────────┘
```

## 📁 프로젝트 구조

```
mvp2/
├── config.py              # 설정 파일 (MySQL, OpenAI API)
├── database.py            # MySQL 데이터베이스 연결 및 쿼리
├── tools.py               # LangGraph 도구들
├── agent.py               # LangGraph 에이전트 구현
├── main.py                # 메인 실행 파일
├── run_agent.sh           # 실행 스크립트
├── requirements.txt       # Python 의존성
└── README.md             # 프로젝트 문서
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd mvp2

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_PASSWORD=your_mysql_password_here
```

### 3. 실행

#### 쉘 스크립트 사용 (권장)
```bash
# 대화형 모드 (기본값)
./run_agent.sh

# 배치 모드
./run_agent.sh batch

# 도움말
./run_agent.sh help
```

#### Python 직접 실행
```bash
# 대화형 모드
python main.py --interactive

# 배치 모드
python main.py --batch

# 도움말
python main.py --help
```

## 🔧 데이터베이스 스키마

### ETL 관련 테이블 (pgm_qry 스키마)
- `pgm_qry_mst`: ETL 프로그램 내의 쿼리 정보
- `pgm_qry_tbl_dtl`: 테이블 레벨 계보 정보

### 메타데이터 테이블 (metadata 스키마)
- `tbl_mst`: 테이블 메타데이터 (한글명, 설명)
- `col_mst`: 컬럼 메타데이터 (한글명, 설명)

### 원천 테이블 (etl_tables 스키마)
- `tableA`: 고객 정보 테이블
- `tableB`: 구매 정보 테이블
- `tableC`: 상품 정보 테이블

## 🔄 워크플로우

1. **계보 분석** (`lineage_analysis`)
   - `pgm_qry_tbl_dtl`에서 tableF의 원천 테이블 조회
   - ETL 프로그램 정보 수집

2. **ETL 쿼리 분석** (`etl_analysis`)
   - `pgm_qry_mst`에서 실제 ETL 쿼리 조회
   - 테이블 생성 로직 분석

3. **메타데이터 수집** (`metadata_collection`)
   - 원천 테이블들의 메타데이터 수집
   - 컬럼 정보 및 설명 수집

4. **컬럼 계보 추적** (`column_tracking`)
   - product_category 컬럼의 원천 추적
   - 관련 컬럼들의 메타데이터 분석

5. **설명 작성** (`description_writing`)
   - 수집된 정보를 바탕으로 설명 생성
   - ETL 과정과 원천 데이터 정보 포함

6. **사용자 검토** (`human_review`)
   - 생성된 설명에 대한 사용자 피드백 수집
   - 필요시 재작성 요청

## 🛠️ 도구 (Tools)

### 데이터베이스 조회 도구
- `get_table_lineage()`: 테이블 계보 정보 조회
- `get_etl_query()`: ETL 쿼리 조회
- `get_table_metadata()`: 테이블 메타데이터 조회
- `get_column_metadata()`: 컬럼 메타데이터 조회
- `get_source_table_structure()`: 원천 테이블 구조 조회

### 분석 도구
- `analyze_column_lineage()`: 특정 컬럼의 계보 분석

## 📊 사용 예시

### 대화형 모드
```bash
$ ./run_agent.sh

🚀 TableF product_category 컬럼 설명 작성 에이전트 시작
==================================================

대상 테이블명을 입력하세요 (기본값: tableF): tableF
대상 컬럼명을 입력하세요 (기본값: product_category): product_category

📊 분석 시작: tableF.product_category
----------------------------------------

📝 분석 결과:
========================================
tableF의 product_category 컬럼은 ETL 과정을 통해 생성된 상품 카테고리 정보입니다.
원천 데이터는 tableB의 product_category 컬럼에서 추출되며, 
고객 구매 데이터의 상품 분류 정보를 정규화하여 저장합니다.
이 컬럼은 상품 분석 및 고객 행동 분석에 활용됩니다.
```

### 배치 모드
```bash
$ ./run_agent.sh batch

📊 배치 모드로 실행
tableF.product_category 컬럼에 대한 설명을 생성합니다.

📝 생성된 설명:
==================================================
[생성된 설명 내용]

💾 결과가 'column_description_result.txt' 파일에 저장되었습니다.
```

## 🔍 문제 해결

### MySQL 연결 오류
```bash
# MySQL 서버 상태 확인
sudo systemctl status mysql

# 연결 정보 확인
mysql -u root -p -h localhost
```

### OpenAI API 오류
```bash
# API 키 확인
echo $OPENAI_API_KEY

# .env 파일 확인
cat .env
```

### 의존성 오류
```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈를 통해 제출해주세요.

---

**개발자**: AI Foundation Team  
**버전**: 1.0.0  
**최종 업데이트**: 2024년 12월
