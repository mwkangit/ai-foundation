#!/bin/bash

# TableF product_category 컬럼 설명 작성 에이전트 실행 스크립트

echo "🚀 TableF product_category 컬럼 설명 작성 에이전트 시작"
echo "=================================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Python 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source .venv/bin/activate
else
    echo "⚠️  가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다."
fi

# 의존성 설치 확인
echo "📋 의존성 확인 중..."
if ! python3 -c "import langchain, langgraph, pymysql" 2>/dev/null; then
    echo "📦 필요한 패키지 설치 중..."
    python3 -m pip install -r requirements.txt
fi

if ! python3 -c "import langchain, langgraph, pymysql" 2>/dev/null; then
    echo "아직도 없습니다."
fi

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. 환경 변수를 설정해주세요."
    echo "필요한 환경 변수:"
    echo "  - OPENAI_API_KEY=your_openai_api_key"
    echo "  - MYSQL_PASSWORD=your_mysql_password"
    echo ""
    echo ".env 파일을 생성하거나 환경 변수를 설정한 후 다시 실행해주세요."
    exit 1
fi

# MySQL 서버 연결 확인
echo "🔍 MySQL 서버 연결 확인 중..."
if ! python3 -c "
import pymysql
from config import MYSQL_CONFIG
try:
    conn = pymysql.connect(**MYSQL_CONFIG)
    conn.close()
    print('✅ MySQL 연결 성공')
except Exception as e:
    print(f'❌ MySQL 연결 실패: {e}')
    exit(1)
" ; then
    echo "❌ MySQL 서버 연결에 실패했습니다."
    echo "MySQL 서버가 실행 중이고 연결 정보가 올바른지 확인해주세요."
    exit 1
fi

# 에이전트 실행
echo ""
echo "🤖 에이전트 실행 중..."
echo ""

# 명령행 인수 처리
MODE="interactive"
TABLE=""
COLUMN=""
PYTHON_ARGS=""

# 인수 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        "batch"|"-b"|"--batch")
            MODE="batch"
            PYTHON_ARGS="$PYTHON_ARGS --batch"
            shift
            ;;
        "interactive"|"-i"|"--interactive")
            MODE="interactive"
            PYTHON_ARGS="$PYTHON_ARGS --interactive"
            shift
            ;;
        "--table"|"-t")
            TABLE="$2"
            PYTHON_ARGS="$PYTHON_ARGS --table $2"
            shift 2
            ;;
        "--column"|"-c")
            COLUMN="$2"
            PYTHON_ARGS="$PYTHON_ARGS --column $2"
            shift 2
            ;;
        "help"|"-h"|"--help")
            echo "사용법: $0 [모드] [옵션]"
            echo ""
            echo "모드:"
            echo "  batch, -b, --batch      배치 모드로 실행"
            echo "  interactive, -i, --interactive  대화형 모드로 실행 (기본값)"
            echo ""
            echo "옵션:"
            echo "  --table, -t TABLE       대상 테이블명 지정"
            echo "  --column, -c COLUMN     대상 컬럼명 지정"
            echo "  --help, -h              이 도움말 표시"
            echo ""
            echo "예시:"
            echo "  $0 batch --table tableF --column product_category"
            echo "  $0 --interactive -t tableD -c engagement_score"
            exit 0
            ;;
        *)
            echo "❌ 알 수 없는 인수: $1"
            echo "도움말을 보려면: $0 --help"
            exit 1
            ;;
    esac
done

# 기본 모드 설정
if [[ -z "$PYTHON_ARGS" ]]; then
    PYTHON_ARGS="--interactive"
fi

# 실행 정보 출력
case "$MODE" in
    "batch")
        echo "📊 배치 모드로 실행"
        ;;
    "interactive")
        echo "💬 대화형 모드로 실행"
        ;;
esac

if [[ -n "$TABLE" ]]; then
    echo "   대상 테이블: $TABLE"
fi

if [[ -n "$COLUMN" ]]; then
    echo "   대상 컬럼: $COLUMN"
fi

# Python 스크립트 실행
python3 main.py $PYTHON_ARGS

echo ""
echo "✅ 에이전트 실행 완료"
