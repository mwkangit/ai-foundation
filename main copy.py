#!/usr/bin/env python3
"""
TableF product_category 컬럼 설명 작성 에이전트
LangGraph 기반 상태 기반 워크플로우로 구현된 컬럼 설명 생성 시스템
"""

import os
import sys
from typing import Dict, Any
from agent import run_column_description_agent
from database import MySQLDatabase
from config import OPENAI_API_KEY

def check_environment():
    """환경 설정을 확인합니다."""
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("환경 변수 또는 .env 파일에 OPENAI_API_KEY를 설정해주세요.")
        return False
    
    # 데이터베이스 연결 테스트
    db = MySQLDatabase()
    if not db.connect():
        print("❌ MySQL 데이터베이스 연결에 실패했습니다.")
        print("MySQL 서버가 실행 중이고 연결 정보가 올바른지 확인해주세요.")
        return False
    
    print("✅ 환경 설정이 완료되었습니다.")
    db.disconnect()
    return True

def interactive_mode():
    """대화형 모드로 에이전트를 실행합니다."""
    print("\n" + "="*60)
    print("TableF product_category 컬럼 설명 작성 에이전트")
    print("="*60)
    
    target_table = input("대상 테이블명을 입력하세요 (기본값: tableF): ").strip() or "tableF"
    target_column = input("대상 컬럼명을 입력하세요 (기본값: product_category): ").strip() or "product_category"
    
    print(f"\n📊 분석 시작: {target_table}.{target_column}")
    print("-" * 40)
    
    # 에이전트 실행
    result = run_column_description_agent(target_table, target_column)
    
    print("\n📝 분석 결과:")
    print("=" * 40)
    print(result["final_result"])
    
    # 사용자 검토 필요 여부 확인
    if result["needs_human_review"]:
        print("\n🤔 사용자 검토가 필요합니다.")
        feedback = input("피드백을 입력하세요 (선택사항): ").strip()
        
        if feedback:
            print("\n🔄 피드백을 반영하여 재분석 중...")
            updated_result = run_column_description_agent(target_table, target_column, feedback)
            print("\n📝 최종 결과:")
            print("=" * 40)
            print(updated_result["final_result"])

def batch_mode():
    """배치 모드로 에이전트를 실행합니다."""
    print("\n배치 모드 실행")
    print("tableF.product_category 컬럼에 대한 설명을 생성합니다.")
    
    result = run_column_description_agent("tableF", "product_category")
    
    print("\n📝 생성된 설명:")
    print("=" * 50)
    print(result["final_result"])
    
    # 결과를 파일로 저장
    with open("column_description_result.txt", "w", encoding="utf-8") as f:
        f.write(f"테이블: tableF\n")
        f.write(f"컬럼: product_category\n")
        f.write(f"생성된 설명:\n")
        f.write(f"{'='*50}\n")
        f.write(result["final_result"])
    
    print(f"\n💾 결과가 'column_description_result.txt' 파일에 저장되었습니다.")

def show_help():
    """도움말을 표시합니다."""
    print("""
TableF product_category 컬럼 설명 작성 에이전트

사용법:
    python main.py [옵션]

옵션:
    -i, --interactive    대화형 모드 (기본값)
    -b, --batch         배치 모드
    -h, --help          도움말 표시

환경 설정:
    1. .env 파일에 다음 설정이 필요합니다:
       - OPENAI_API_KEY=your_openai_api_key
       - MYSQL_PASSWORD=your_mysql_password
    
    2. MySQL 서버가 실행 중이어야 합니다.
    3. 필요한 데이터베이스와 테이블이 존재해야 합니다.

기능:
    - ETL 과정 추적을 통한 컬럼 계보 분석
    - 원천 테이블 및 컬럼 메타데이터 수집
    - LangGraph 기반 상태 기반 워크플로우
    - Human-in-the-loop 피드백 시스템
    - MySQL 데이터베이스 연동
    """)

def main():
    """메인 함수"""
    # 환경 설정 확인
    if not check_environment():
        sys.exit(1)
    
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['-h', '--help']:
            show_help()
        elif arg in ['-b', '--batch']:
            batch_mode()
        elif arg in ['-i', '--interactive']:
            interactive_mode()
        else:
            print(f"❌ 알 수 없는 옵션: {arg}")
            show_help()
    else:
        # 기본값: 대화형 모드
        interactive_mode()

if __name__ == "__main__":
    main()
