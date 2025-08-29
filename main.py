import argparse
import sys
from agent import run_column_description_agent

def main():
    parser = argparse.ArgumentParser(description='TableF product_category 컬럼 설명 작성 에이전트')
    parser.add_argument('--batch', '-b', action='store_true', help='배치 모드로 실행')
    parser.add_argument('--interactive', '-i', action='store_true', help='대화형 모드로 실행')
    parser.add_argument('--table', '-t', default='tableD', help='대상 테이블명 (기본값: tableD)')
    parser.add_argument('--column', '-c', default='engagement_score', help='대상 컬럼명 (기본값: engagement_score)')
    
    args = parser.parse_args()
    
    # 기본값 설정
    target_table = args.table
    target_column = args.column
    
    if args.batch:
        print("📊 배치 모드로 실행 중...")
        print(f"대상 테이블: {target_table}")
        print(f"대상 컬럼: {target_column}")
        print("=" * 50)
        
        try:
            result = run_column_description_agent(target_table, target_column)
            print("\n✅ 분석 완료!")
            print("=" * 50)
            print("📝 최종 컬럼 설명:")
            print(result["final_result"])
            print("=" * 50)
            
            if result["needs_human_review"]:
                print("\n⚠️  사용자 검토가 필요합니다.")
                feedback = input("피드백을 입력하세요 (엔터로 건너뛰기): ").strip()
                if feedback:
                    print("\n🔄 피드백을 반영하여 재분석 중...")
                    final_result = run_column_description_agent(target_table, target_column, feedback)
                    print("\n📝 최종 수정된 설명:")
                    print(final_result["final_result"])
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            sys.exit(1)
            
    elif args.interactive:
        print("💬 대화형 모드로 실행 중...")
        print("=" * 50)
        
        while True:
            print(f"\n현재 설정:")
            print(f"- 대상 테이블: {target_table}")
            print(f"- 대상 컬럼: {target_column}")
            print("\n옵션을 선택하세요:")
            print("1. 컬럼 설명 분석 시작")
            print("2. 테이블명 변경")
            print("3. 컬럼명 변경")
            print("4. 종료")
            
            choice = input("\n선택 (1-4): ").strip()
            
            if choice == "1":
                print(f"\n🔍 {target_table}.{target_column} 컬럼 분석을 시작합니다...")
                try:
                    result = run_column_description_agent(target_table, target_column)
                    print("\n✅ 분석 완료!")
                    print("=" * 50)
                    print("📝 컬럼 설명:")
                    print(result["final_result"])
                    print("=" * 50)
                    
                    if result["needs_human_review"]:
                        feedback = input("\n피드백을 입력하세요 (엔터로 건너뛰기): ").strip()
                        if feedback:
                            print("\n🔄 피드백을 반영하여 재분석 중...")
                            final_result = run_column_description_agent(target_table, target_column, feedback)
                            print("\n📝 최종 수정된 설명:")
                            print(final_result["final_result"])
                            
                except Exception as e:
                    print(f"❌ 오류 발생: {e}")
                    
            elif choice == "2":
                new_table = input(f"새로운 테이블명을 입력하세요 (현재: {target_table}): ").strip()
                if new_table:
                    target_table = new_table
                    print(f"✅ 테이블명이 {target_table}로 변경되었습니다.")
                    
            elif choice == "3":
                new_column = input(f"새로운 컬럼명을 입력하세요 (현재: {target_column}): ").strip()
                if new_column:
                    target_column = new_column
                    print(f"✅ 컬럼명이 {target_column}로 변경되었습니다.")
                    
            elif choice == "4":
                print("👋 프로그램을 종료합니다.")
                break
                
            else:
                print("❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")
                
    else:
        # 기본 대화형 모드
        print("💬 기본 대화형 모드로 실행 중...")
        print("=" * 50)
        
        print(f"대상 테이블: {target_table}")
        print(f"대상 컬럼: {target_column}")
        print("\n분석을 시작하시겠습니까? (y/n): ", end="")
        
        if input().lower().startswith('y'):
            try:
                result = run_column_description_agent(target_table, target_column)
                print("\n✅ 분석 완료!")
                print("=" * 50)
                print("📝 컬럼 설명:")
                print(result["final_result"])
                print("=" * 50)
                
                if result["needs_human_review"]:
                    feedback = input("\n피드백을 입력하세요 (엔터로 건너뛰기): ").strip()
                    if feedback:
                        print("\n🔄 피드백을 반영하여 재분석 중...")
                        final_result = run_column_description_agent(target_table, target_column, feedback)
                        print("\n📝 최종 수정된 설명:")
                        print(final_result["final_result"])
                        
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                sys.exit(1)
        else:
            print("👋 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
