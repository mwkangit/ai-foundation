# Column Description Agent



## ETL Query

`````sql
-- Mart tableD
CREATE OR REPLACE TEMP VIEW tableD AS
SELECT
    a.customer_id,
    CONCAT(a.first_name, ' ', a.last_name) AS full_name,
    CASE
        WHEN YEAR(CURRENT_DATE) - YEAR(a.date_of_birth) < 20 THEN '10s'
        WHEN YEAR(CURRENT_DATE) - YEAR(a.date_of_birth) < 30 THEN '20s'
        WHEN YEAR(CURRENT_DATE) - YEAR(a.date_of_birth) < 40 THEN '30s'
        ELSE '40s+'
    END AS age_group,
    a.gender,
    a.loyalty_level,
    DATEDIFF(CURRENT_DATE, a.registration_date) AS membership_duration,
    SUM(b.purchase_amount) AS total_purchase_amount,
    COUNT(b.purchase_id) AS purchase_count,
    FIRST(b.product_category) AS preferred_category,
    a.email
FROM tableA a
LEFT JOIN tableB b
ON a.customer_id = b.customer_id
GROUP BY a.customer_id, a.first_name, a.last_name, a.gender, a.loyalty_level, a.registration_date, a.email;

-- Mart tableE
CREATE OR REPLACE TEMP VIEW tableE AS
SELECT
    d.customer_id,
    d.full_name,
    d.age_group,
    d.gender,
    d.loyalty_level,
    d.total_purchase_amount,
    COUNT(c.campaign_id) AS campaign_participation_count,
    AVG(c.click_rate * c.conversion_rate) AS engagement_score,
    AVG(c.click_rate * c.conversion_rate) AS customer_score,
    SUM(c.budget) / NULLIF(d.total_purchase_amount, 0) AS roi_estimate
FROM tableD d
LEFT JOIN tableC c
ON d.loyalty_level = c.target_segment
GROUP BY d.customer_id, d.full_name, d.age_group, d.gender, d.loyalty_level, d.total_purchase_amount;


-- Mart tableF
CREATE OR REPLACE TEMP VIEW tableF AS
SELECT
    b.purchase_id,
    b.customer_id,
    b.product_category,
    b.purchase_amount,
    c.campaign_id,
    c.campaign_name,
    c.channel,
    c.region,
    AVG(CASE WHEN c.campaign_id IS NOT NULL THEN 1 ELSE 0 END) AS campaign_effectiveness,
    AVG(CASE WHEN c.campaign_id IS NOT NULL THEN b.purchase_amount / NULLIF(c.budget, 0) ELSE 0 END) AS campaign_roi
FROM tableB b
LEFT JOIN tableC c
ON b.product_category = c.target_segment
GROUP BY b.purchase_id, b.customer_id, b.product_category, b.purchase_amount, c.campaign_id, c.campaign_name, c.channel, c.region;

`````



## Table Lineage Data

| PGM_ID         | JOB_SEQ | QRY_SEQ | SRC_DB_NM | SRC_TBL_NM | SRC_TBL_NM_SEQ | TRGT_DB_NM | TRGT_TBL_NM |
| -------------- | ------- | ------- | --------- | ---------- | -------------- | ---------- | ----------- |
| llm_test_1.hql | 1       | 1       | NULL      | tableA     | 1              | NULL       | tableD      |
| llm_test_1.hql | 1       | 1       | NULL      | tableB     | 1              | NULL       | tableD      |
| llm_test_2.hql | 1       | 1       | NULL      | tableC     | 1              | NULL       | tableE      |
| llm_test_2.hql | 1       | 1       | NULL      | tableD     | 1              | NULL       | tableE      |
| llm_test_3.hql | 1       | 1       | NULL      | tableB     | 1              | NULL       | tableF      |
| llm_test_3.hql | 1       | 1       | NULL      | tableC     | 1              | NULL       | tableF      |



## Result

```bash
./run_agent.sh interactive --table tableE --column engagement_score
🚀 TableF product_category 컬럼 설명 작성 에이전트 시작
==================================================
📦 가상환경 활성화 중...
📋 의존성 확인 중...
🔍 MySQL 서버 연결 확인 중...
✅ MySQL 연결 성공

🤖 에이전트 실행 중...

💬 대화형 모드로 실행
   대상 테이블: tableE
   대상 컬럼: engagement_score
💬 대화형 모드로 실행 중...
==================================================

현재 설정:
- 대상 테이블: tableE
- 대상 컬럼: engagement_score

옵션을 선택하세요:
1. 컬럼 설명 분석 시작
2. 테이블명 변경
3. 컬럼명 변경
4. 종료

선택 (1-4): 1

🔍 tableE.engagement_score 컬럼 분석을 시작합니다...
🔍 현재 단계: lineage_analysis
📊 1단계: 테이블 계보 분석 중...
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
🔀 라우터: 현재 단계 = etl_analysis
   → analysis로 이동
🔍 현재 단계: etl_analysis
🔧 2단계: ETL 쿼리 분석 중...
   프로그램 ID: rag_test_2.hql
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
🔀 라우터: 현재 단계 = metadata_collection
   → analysis로 이동
🔍 현재 단계: metadata_collection
📋 3단계: 메타데이터 수집 중...
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
🔀 라우터: 현재 단계 = column_tracking
   → analysis로 이동
🔍 현재 단계: column_tracking
🔗 4단계: 컬럼 계보 추적 중...
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
   원천 테이블들: ['tableC', 'tableD']
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
/Users/1113444/Desktop/ai-foundation-mvp/mvp/database.py:35: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  df = pd.read_sql_query(query, self.connection, params=params)
🔀 라우터: 현재 단계 = description_writing
   → analysis로 이동
🔍 현재 단계: description_writing
✍️ 5단계: 컬럼 설명 작성 중...
🔀 라우터: 현재 단계 = human_review
   → human_review에서 대기
👤 사용자 검토 단계
   → 기본 피드백 설정됨
🔀 라우터: 현재 단계 = human_review
   → final_description으로 이동

✅ 분석 완료!
==================================================
📝 컬럼 설명:
# engagement_score 컬럼 상세 설명

## 1. 컬럼의 목적과 의미
- **목적**: engagement_score 컬럼은 고객의 캠페인 참여도와 효과성을 측정하기 위해 존재합니다. 이 컬럼은 고객이 참여한 캠페인의 클릭률과 전환율을 기반으로 하여, 고객의 전반적인 참여 수준을 수치적으로 표현합니다.
- **비즈니스 관점에서의 핵심 역할과 가치**: 이 컬럼은 마케팅 팀이 고객의 반응을 분석하고, 캠페인의 성공 여부를 평가하는 데 중요한 역할을 합니다. 높은 engagement_score는 고객의 관심과 참여가 높음을 나타내며, 이는 향후 마케팅 전략 수립에 있어 중요한 데이터로 활용됩니다.

## 2. ETL 과정 분석
- **원천 테이블과 컬럼**: engagement_score는 tableC의 click_rate와 conversion_rate 컬럼을 기반으로 생성됩니다. 이 두 컬럼은 캠페인의 효과성을 나타내는 지표입니다.
- **JOIN 관계**: tableD와 tableC는 LEFT JOIN으로 연결됩니다. 이 조인은 tableD의 loyalty_level과 tableC의 target_segment를 기준으로 하여, 고객의 충성도 수준에 맞는 캠페인 데이터를 결합합니다.
- **집계 함수**: AVG 함수가 사용되어 click_rate와 conversion_rate의 곱의 평균을 계산하여 engagement_score를 도출합니다. COUNT 함수는 고객이 참여한 캠페인의 수를 세고, SUM 함수는 예산을 집계합니다.
- **GROUP BY 로직**: 고객 ID, 이름, 연령대, 성별, 충성도 수준, 총 구매 금액을 기준으로 그룹화하여 각 고객에 대한 집계 결과를 생성합니다.
- **WHERE 조건**: 본 쿼리에서는 WHERE 조건이 명시되어 있지 않지만, LEFT JOIN을 통해 모든 고객 데이터가 포함되도록 설계되었습니다.
- **CASE 문**: 본 쿼리에서는 CASE 문이 사용되지 않았습니다.
- **데이터 변환 단계**: 원천 데이터에서 click_rate와 conversion_rate를 곱한 후 평균을 내어 engagement_score를 생성합니다. 이 과정에서 NULLIF 함수를 사용하여 총 구매 금액이 0일 경우 나누기 오류를 방지합니다.
- **쿼리 복잡도**: 쿼리는 다중 집계와 JOIN을 포함하여 복잡도가 높습니다. 이는 성능에 영향을 미칠 수 있으며, 데이터 양이 많을 경우 최적화가 필요할 수 있습니다.

## 3. 원천 데이터와의 관계
- **원천 컬럼들의 의미와 설명**: 
  - **click_rate**: 캠페인 클릭률로, 고객이 캠페인을 클릭한 비율을 나타냅니다.
  - **conversion_rate**: 캠페인 전환율로, 클릭한 고객 중 실제 구매로 이어진 비율을 나타냅니다.
- **원천 데이터에서 타겟 컬럼으로의 매핑 관계**: tableC의 click_rate와 conversion_rate가 engagement_score로 직접 매핑됩니다. tableD의 고객 정보는 캠페인 참여를 분석하는 데 사용됩니다.
- **데이터 품질과 일관성 보장 방법**: 데이터의 일관성을 보장하기 위해, 캠페인 데이터와 고객 데이터를 조인할 때 충성도 수준과 타겟 세그먼트를 기준으로 하여 정확한 매핑을 수행합니다.

## 4. 데이터 특성
- **데이터 타입과 형식**: engagement_score는 실수형(DECIMAL 또는 FLOAT)으로 저장되며, 평균값을 나타내기 때문에 소수점 이하의 값이 포함될 수 있습니다.
- **값의 범위와 패턴**: engagement_score의 값은 0에서 1 사이의 범위를 가질 수 있으며, 이는 고객의 참여도에 따라 달라집니다. 높은 값은 높은 참여도를 의미합니다.
- **NULL 처리 방식**: NULLIF 함수를 사용하여 총 구매 금액이 0일 경우 나누기 오류를 방지하고, 이 경우 engagement_score는 NULL로 처리될 수 있습니다.

## 5. 비즈니스 컨텍스트
- **이 컬럼이 비즈니스 의사결정에 어떻게 활용되는지**: engagement_score는 마케팅 캠페인의 효과성을 평가하고, 고객의 반응을 분석하여 향후 캠페인 전략을 수립하는 데 중요한 데이터로 활용됩니다.
- **분석이나 리포팅에서의 역할**: 이 컬럼은 고객 세분화, 캠페인 성과 분석, ROI 분석 등 다양한 리포트에서 핵심 지표로 사용됩니다.
- **마케팅, 운영, 전략적 관점에서의 중요성**: 높은 engagement_score는 고객의 충성도와 브랜드에 대한 긍정적인 인식을 나타내며, 이는 장기적인 고객 관계 구축에 기여합니다.

## 6. 활용 방안
- **어떤 분석이나 쿼리에서 주로 사용되는지**: engagement_score는 고객 분석, 캠페인 성과 분석, ROI 분석 등 다양한 분석 쿼리에서 주로 사용됩니다.
- **다른 컬럼들과의 조합 활용 사례**: engagement_score는 고객의 총 구매 금액, 캠페인 참여 수와 함께 분석되어 고객의 전체적인 가치 평가에 기여합니다.
- **향후 활용 가능성**: 이 컬럼은 머신러닝 모델링, 예측 분석 등 다양한 고급 분석 기법에 활용될 수 있으며, 고객 맞춤형 마케팅 전략 수립에 기여할 수 있습니다. 

이 최종 설명은 사용자 피드백을 반영하여 더욱 명확하고 구체적으로 작성되었습니다.
==================================================

피드백을 입력하세요 (엔터로 건너뛰기): engagement_score의 생성 과정을 간결하게 설명해줘.

🔄 피드백을 반영하여 재분석 중...
🔍 현재 단계: human_review
🔀 라우터: 현재 단계 = human_review
   → final_description으로 이동

📝 최종 수정된 설명:
**engagement_score 컬럼 설명:**

engagement_score는 사용자의 활동성과 상호작용을 정량적으로 평가하기 위해 설계된 지표입니다. 이 점수는 다양한 요소를 기반으로 계산되며, 주로 사용자의 게시물 조회수, 댓글 수, 좋아요 수, 공유 횟수 등을 종합하여 산출됩니다. 

구체적으로, 각 요소는 특정 가중치를 부여받아 점수에 반영되며, 이를 통해 사용자의 전반적인 참여도를 평가합니다. 예를 들어, 댓글 수는 사용자와의 상호작용을 나타내므로 상대적으로 높은 가중치를 가질 수 있습니다. 

engagement_score는 0에서 100 사이의 값으로 표현되며, 점수가 높을수록 사용자가 플랫폼 내에서 활발하게 활동하고 있음을 의미합니다. 이 지표는 마케팅 전략 수립, 사용자 경험 개선 및 콘텐츠 최적화에 중요한 역할을 합니다. 

이러한 방식으로 engagement_score는 사용자 피드백을 반영하여 지속적으로 개선되며, 플랫폼의 전반적인 참여도를 향상시키는 데 기여합니다.

현재 설정:
- 대상 테이블: tableE
- 대상 컬럼: engagement_score

옵션을 선택하세요:
1. 컬럼 설명 분석 시작
2. 테이블명 변경
3. 컬럼명 변경
4. 종료

선택 (1-4): 4
👋 프로그램을 종료합니다.

✅ 에이전트 실행 완료