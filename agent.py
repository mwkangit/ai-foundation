import json
from typing import Dict, List, Any, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from tools import (
    get_table_lineage, 
    get_etl_query, 
    get_table_metadata, 
    get_column_metadata, 
    get_source_table_structure,
    analyze_column_lineage
)
from config import OPENAI_API_KEY

# 상태 정의
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "대화 메시지들"]
    current_step: Annotated[str, "현재 단계"]
    target_table: Annotated[str, "대상 테이블"]
    target_column: Annotated[str, "대상 컬럼"]
    lineage_data: Annotated[Dict, "계보 데이터"]
    etl_queries: Annotated[Dict, "ETL 쿼리들"]
    metadata_info: Annotated[Dict, "메타데이터 정보"]
    column_description: Annotated[str, "컬럼 설명"]
    human_feedback: Annotated[str, "사용자 피드백"]
    final_result: Annotated[str, "최종 결과"]
    needs_human_review: Annotated[bool, "사용자 검토 필요 여부"]

# LLM 모델 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    api_key=OPENAI_API_KEY
)

# 도구들
tools = [
    get_table_lineage,
    get_etl_query,
    get_table_metadata,
    get_column_metadata,
    get_source_table_structure,
    analyze_column_lineage
]

# 프롬프트 템플릿들
system_prompt = """당신은 데이터 계보 분석 전문가입니다. 
주어진 테이블과 컬럼에 대해 ETL 과정을 추적하고 상세한 설명을 작성해야 합니다.

작업 단계:
1. 테이블 계보 분석: ETL 과정에서 사용된 원천 테이블들을 파악
2. ETL 쿼리 분석: 테이블 생성에 사용된 쿼리 분석
3. 메타데이터 수집: 원천 테이블과 컬럼의 메타데이터 수집
4. 컬럼 계보 추적: 특정 컬럼이 어떤 원천 컬럼에서 왔는지 분석
5. 설명 작성: 수집된 정보를 바탕으로 상세한 설명 작성
6. 사용자 검토: 작성된 설명에 대해 사용자 피드백 요청

각 단계에서 필요한 도구를 사용하여 정보를 수집하고, 
최종적으로 명확하고 상세한 컬럼 설명을 작성하세요."""

analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", """
현재 상태: {current_step}
대상 테이블: {target_table}
대상 컬럼: {target_column}

다음 단계를 수행하세요:
{step_instructions}
""")
])

review_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 데이터 설명 검토 전문가입니다. 작성된 설명의 품질을 평가하고 개선점을 제안하세요."),
    MessagesPlaceholder(variable_name="messages"),
    ("human", """
작성된 컬럼 설명:
{column_description}

이 설명에 대해 검토하고 개선점을 제안해주세요.
""")
])

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "최종 컬럼 설명을 작성하세요. 사용자 피드백을 반영하여 완성도 높은 설명을 만들어주세요."),
    MessagesPlaceholder(variable_name="messages"),
    ("human", """
사용자 피드백: {human_feedback}
기존 설명: {column_description}

피드백을 반영하여 최종 설명을 작성해주세요.
""")
])

# 노드 함수들
def analysis_node(state: AgentState) -> AgentState:
    """분석 단계를 수행하는 노드"""
    current_step = state["current_step"]
    
    print(f"🔍 현재 단계: {current_step}")
    
    # 단계별 도구 호출
    if current_step == "lineage_analysis":
        print("📊 1단계: 테이블 계보 분석 중...")
        # 테이블 계보 분석
        lineage_result = get_table_lineage.invoke({"target_table": state["target_table"]})
        state["lineage_data"] = lineage_result
        state["messages"].append(SystemMessage(content=f"계보 분석 결과: {lineage_result}"))
        state["current_step"] = "etl_analysis"
        
    elif current_step == "etl_analysis":
        print("🔧 2단계: ETL 쿼리 분석 중...")
        # ETL 쿼리 분석
        lineage_info = state.get("lineage_data", {})
        if "프로그램 ID" in str(lineage_info):
            # 계보 정보에서 program_id 추출
            import re
            program_match = re.search(r'프로그램 ID: ([^\n]+)', str(lineage_info))
            if program_match:
                program_id = program_match.group(1).strip()
                etl_result = get_etl_query.invoke({
                    "program_id": program_id,
                    "job_seq": 1,
                    "query_seq": 1
                })
                state["etl_queries"] = etl_result
                state["messages"].append(SystemMessage(content=f"ETL 쿼리 분석 결과: {etl_result}"))
        state["current_step"] = "metadata_collection"
        
    elif current_step == "metadata_collection":
        print("📋 3단계: 메타데이터 수집 중...")
        # 메타데이터 수집
        metadata_result = get_table_metadata.invoke({"table_name": state["target_table"]})
        state["metadata_info"]["table"] = metadata_result
        state["messages"].append(SystemMessage(content=f"테이블 메타데이터: {metadata_result}"))
        
        column_metadata_result = get_column_metadata.invoke({
            "table_name": state["target_table"],
            "column_name": state["target_column"]
        })
        state["metadata_info"]["column"] = column_metadata_result
        state["messages"].append(SystemMessage(content=f"컬럼 메타데이터: {column_metadata_result}"))
        state["current_step"] = "column_tracking"
        
    elif current_step == "column_tracking":
        print("🔗 4단계: 컬럼 계보 추적 중...")
        # 컬럼 계보 추적
        lineage_result = analyze_column_lineage.invoke({
            "target_table": state["target_table"],
            "target_column": state["target_column"]
        })
        state["messages"].append(SystemMessage(content=f"컬럼 계보 분석: {lineage_result}"))
        
        # 원천 테이블들의 컬럼 메타데이터 수집
        lineage_info = state.get("lineage_data", {})
        if "소스 테이블들" in str(lineage_info):
            import re
            source_tables_match = re.search(r'소스 테이블들: ([^\n]+)', str(lineage_info))
            if source_tables_match:
                source_tables = source_tables_match.group(1).strip().split(', ')
                print(f"   원천 테이블들: {source_tables}")
                
                for source_table in source_tables:
                    source_table = source_table.strip()
                    if source_table:
                        # 원천 테이블의 컬럼 메타데이터 수집
                        source_columns = get_column_metadata.invoke({
                            "table_name": source_table,
                            "column_name": ""  # 모든 컬럼 조회
                        })
                        state["messages"].append(SystemMessage(content=f"원천 테이블 {source_table} 컬럼 정보: {source_columns}"))
                        
                        # target_column과 유사한 컬럼 찾기
                        if state["target_column"].lower() in str(source_columns).lower():
                            similar_columns = get_column_metadata.invoke({
                                "table_name": source_table,
                                "column_name": state["target_column"]
                            })
                            state["messages"].append(SystemMessage(content=f"원천 테이블 {source_table}의 {state['target_column']} 컬럼: {similar_columns}"))
        
        state["current_step"] = "description_writing"
        
    elif current_step == "description_writing":
        print("✍️ 5단계: 컬럼 설명 작성 중...")
        # 컬럼 설명 작성
        all_info = "\n".join([msg.content for msg in state["messages"] if hasattr(msg, 'content')])
        
        description_prompt = f"""
다음 정보를 바탕으로 {state['target_table']} 테이블의 {state['target_column']} 컬럼에 대한 상세하고 정확한 설명을 작성해주세요:

{all_info}

다음 구조로 상세하게 분석해주세요:

## 1. 컬럼의 목적과 의미
- 이 컬럼이 왜 존재하는지, 어떤 목적으로 사용되는지
- 비즈니스 관점에서의 핵심 역할과 가치

## 2. ETL 과정 분석
- 원천 테이블에서 어떤 컬럼들이 이 컬럼을 생성하는데 기여했는지
- ETL 쿼리에서 어떤 변환 과정을 거쳤는지 (JOIN, GROUP BY, 함수 적용 등)
- 데이터 변환의 구체적인 로직과 이유

## 3. 원천 데이터와의 관계
- 원천 컬럼들의 의미와 설명
- 원천 데이터에서 타겟 컬럼으로의 매핑 관계
- 데이터 품질과 일관성 보장 방법

## 4. 데이터 특성
- 데이터 타입과 형식
- 값의 범위와 패턴
- NULL 처리 방식

## 5. 비즈니스 컨텍스트
- 이 컬럼이 비즈니스 의사결정에 어떻게 활용되는지
- 분석이나 리포팅에서의 역할
- 마케팅, 운영, 전략적 관점에서의 중요성

## 6. 활용 방안
- 어떤 분석이나 쿼리에서 주로 사용되는지
- 다른 컬럼들과의 조합 활용 사례
- 향후 활용 가능성

각 섹션을 구체적이고 명확하게 작성하고, ETL 과정의 기술적 세부사항과 비즈니스적 의미를 모두 포함해주세요.
"""
        
        response = llm.invoke([SystemMessage(content=description_prompt)])
        state["column_description"] = response.content
        state["messages"].append(SystemMessage(content=f"작성된 설명: {response.content}"))
        state["current_step"] = "human_review"
    
    return state

def human_review_node(state: AgentState) -> AgentState:
    """사용자 검토 단계를 수행하는 노드"""
    print("👤 사용자 검토 단계")
    
    # 현재까지의 분석 결과를 요약
    summary = f"""
분석 완료:
- 대상 테이블: {state['target_table']}
- 대상 컬럼: {state['target_column']}
- 수집된 정보: {len(state['messages'])} 개의 메시지
"""
    
    # 사용자에게 검토 요청
    state["needs_human_review"] = True
    state["messages"].append(SystemMessage(content=summary))
    state["messages"].append(SystemMessage(content="사용자 검토가 필요합니다. 피드백을 제공해주세요."))
    
    # 피드백이 없으면 기본 피드백 설정 (배치 모드용)
    if not state.get("human_feedback"):
        state["human_feedback"] = "기본 피드백: 설명이 적절합니다."
        print("   → 기본 피드백 설정됨")
    
    return state

def final_description_node(state: AgentState) -> AgentState:
    """최종 설명 작성 노드"""
    if not state["human_feedback"]:
        # 피드백이 없는 경우 기본 설명 생성
        response = llm.invoke(
            final_prompt.format_messages(
                messages=state["messages"],
                human_feedback="피드백 없음",
                column_description=state.get("column_description", "")
            )
        )
    else:
        # 피드백을 반영한 최종 설명 생성
        response = llm.invoke(
            final_prompt.format_messages(
                messages=state["messages"],
                human_feedback=state["human_feedback"],
                column_description=state.get("column_description", "")
            )
        )
    
    state["final_result"] = response.content
    state["current_step"] = "completed"
    
    return state

def should_continue(state: AgentState) -> str:
    """다음 단계를 결정하는 라우터"""
    current_step = state["current_step"]
    
    print(f"🔀 라우터: 현재 단계 = {current_step}")
    
    if current_step == "human_review":
        if state.get("human_feedback"):
            print("   → final_description으로 이동")
            return "final_description"
        else:
            print("   → human_review에서 대기")
            return "human_review"
    elif current_step == "completed":
        print("   → 종료")
        return END
    else:
        print("   → analysis로 이동")
        return "analysis"

# 그래프 구성
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("analysis", analysis_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("final_description", final_description_node)

# 엣지 추가
workflow.add_conditional_edges("analysis", should_continue)
workflow.add_conditional_edges("human_review", should_continue)
workflow.add_edge("final_description", END)

# START 노드에서 첫 번째 노드로 가는 엣지 추가
workflow.set_entry_point("analysis")

# 체크포인트 설정
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def run_column_description_agent(target_table: str, target_column: str, human_feedback: str = None) -> Dict[str, Any]:
    """컬럼 설명 에이전트를 실행합니다."""
    
    # 초기 상태 설정
    initial_state = {
        "messages": [
            SystemMessage(content=f"테이블 {target_table}의 {target_column} 컬럼 설명 작성을 시작합니다.")
        ],
        "current_step": "lineage_analysis",
        "target_table": target_table,
        "target_column": target_column,
        "lineage_data": {},
        "etl_queries": {},
        "metadata_info": {},
        "column_description": "",
        "human_feedback": human_feedback or "",
        "final_result": "",
        "needs_human_review": False
    }
    
    # 에이전트 실행
    config = {"configurable": {"thread_id": f"thread_{target_table}_{target_column}"}}
    
    if human_feedback:
        # 피드백이 있는 경우 human_review 노드부터 시작
        initial_state["current_step"] = "human_review"
        initial_state["human_feedback"] = human_feedback
    
    result = app.invoke(initial_state, config)
    
    return {
        "target_table": target_table,
        "target_column": target_column,
        "final_result": result["final_result"],
        "messages": result["messages"],
        "needs_human_review": result["needs_human_review"]
    }

if __name__ == "__main__":
    # 테스트 실행
    result = run_column_description_agent("tableF", "product_category")
    print("최종 결과:")
    print(result["final_result"])
