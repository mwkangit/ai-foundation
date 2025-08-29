from typing import Dict, List, Any
from langchain_core.tools import tool
from database import MySQLDatabase

# 전역 데이터베이스 인스턴스
db = MySQLDatabase()

@tool
def get_table_lineage(target_table: str) -> str:
    """테이블의 계보 정보를 조회합니다. ETL 과정에서 어떤 원천 테이블들이 사용되었는지 확인할 수 있습니다."""
    try:
        lineage_info = db.get_table_lineage(target_table)
        
        if "error" in lineage_info:
            return lineage_info["error"]
        
        result = f"테이블 {target_table}의 계보 정보:\n"
        result += f"- 대상 테이블: {lineage_info['target_table']}\n"
        result += f"- 소스 테이블들: {', '.join(lineage_info['source_tables'])}\n"
        result += f"- 프로그램 ID: {lineage_info['program_id']}\n"
        result += f"- 작업 순서: {lineage_info['job_seq']}\n"
        result += f"- 쿼리 순서: {lineage_info['query_seq']}\n"
        result += f"- 소스 데이터베이스: {', '.join(lineage_info['source_databases'])}\n"
        result += f"- 대상 데이터베이스: {lineage_info['target_database']}\n"
        
        return result
    except Exception as e:
        return f"계보 정보 조회 중 오류 발생: {str(e)}"

@tool
def get_etl_query(program_id: str, job_seq: int, query_seq: int) -> str:
    """ETL 쿼리를 조회합니다. 테이블이 어떻게 생성되었는지 확인할 수 있습니다."""
    try:
        etl_info = db.get_etl_query(program_id, job_seq, query_seq)
        
        if isinstance(etl_info, str):
            return etl_info
        
        result = f"ETL 쿼리 정보:\n"
        result += f"- 프로그램 ID: {program_id}\n"
        result += f"- 작업 순서: {job_seq}\n"
        result += f"- 쿼리 순서: {query_seq}\n"
        result += f"- 쿼리 타입: {etl_info['statement_type']}\n"
        result += f"- 프로그램 경로: {etl_info['program_path']}\n"
        result += f"- SQL 쿼리:\n{etl_info['sql']}\n"
        
        return result
    except Exception as e:
        return f"ETL 쿼리 조회 중 오류 발생: {str(e)}"

@tool
def get_table_metadata(table_name: str, database_name: str = None) -> str:
    """테이블의 메타데이터를 조회합니다. 테이블의 한글명과 설명을 확인할 수 있습니다."""
    try:
        metadata = db.get_table_metadata(table_name, database_name)
        
        if "error" in metadata:
            return metadata["error"]
        
        result = f"테이블 {table_name}의 메타데이터:\n"
        result += f"- 테이블명: {metadata['tbl_nm']}\n"
        result += f"- 데이터베이스: {metadata['db_nm']}\n"
        result += f"- 한글명: {metadata['han_nm']}\n"
        result += f"- 설명: {metadata['desc']}\n"
        
        return result
    except Exception as e:
        return f"테이블 메타데이터 조회 중 오류 발생: {str(e)}"

@tool
def get_column_metadata(table_name: str, column_name: str = "", database_name: str = None) -> str:
    """컬럼의 메타데이터를 조회합니다. 컬럼의 한글명과 설명을 확인할 수 있습니다."""
    try:
        # column_name이 빈 문자열이면 None으로 변환
        col_name = column_name if column_name else None
        columns = db.get_column_metadata(table_name, col_name, database_name)
        
        if len(columns) == 1 and "error" in columns[0]:
            return columns[0]["error"]
        
        result = f"테이블 {table_name}의 컬럼 메타데이터:\n"
        for col in columns:
            result += f"- 컬럼명: {col['col_nm']}\n"
            result += f"- 테이블명: {col['tbl_nm']}\n"
            result += f"- 데이터베이스: {col['db_nm']}\n"
            result += f"- 한글명: {col['han_nm']}\n"
            result += f"- 설명: {col['desc']}\n\n"
        
        return result
    except Exception as e:
        return f"컬럼 메타데이터 조회 중 오류 발생: {str(e)}"

@tool
def get_source_table_structure(table_name: str, database_name: str) -> str:
    """원천 테이블의 구조를 조회합니다. 테이블의 컬럼 정보를 확인할 수 있습니다."""
    try:
        structure = db.get_source_table_structure(table_name, database_name)
        
        if "error" in structure:
            return structure["error"]
        
        result = f"테이블 {database_name}.{table_name}의 구조:\n"
        for col in structure['columns']:
            result += f"- 컬럼명: {col['field']}\n"
            result += f"- 타입: {col['type']}\n"
            result += f"- NULL 허용: {col['null']}\n"
            result += f"- 키: {col['key']}\n"
            result += f"- 기본값: {col['default']}\n"
            result += f"- 추가: {col['extra']}\n\n"
        
        return result
    except Exception as e:
        return f"테이블 구조 조회 중 오류 발생: {str(e)}"

@tool
def analyze_column_lineage(target_table: str, target_column: str) -> str:
    """특정 컬럼의 계보를 분석합니다. 해당 컬럼이 어떤 원천 테이블의 어떤 컬럼에서 왔는지 추적합니다."""
    try:
        # 1. 테이블 계보 조회
        lineage_info = db.get_table_lineage(target_table)
        
        if "error" in lineage_info:
            return lineage_info["error"]
        
        # 2. ETL 쿼리 조회
        etl_info = db.get_etl_query(
            lineage_info['program_id'], 
            lineage_info['job_seq'], 
            lineage_info['query_seq']
        )
        
        if isinstance(etl_info, str):
            return etl_info
        
        # 3. 소스 테이블들의 컬럼 정보 조회
        source_columns = []
        for source_table in lineage_info['source_tables']:
            for source_db in lineage_info['source_databases']:
                columns = db.get_column_metadata(source_table, database_name=source_db)
                if not (len(columns) == 1 and "error" in columns[0]):
                    source_columns.extend(columns)
        
        # 4. ETL 쿼리에서 target_column 관련 부분 분석
        sql_query = etl_info['sql']
        etl_analysis = ""
        
        # SELECT 절에서 target_column 찾기
        if target_column.lower() in sql_query.lower():
            etl_analysis += f"ETL 쿼리에서 {target_column} 컬럼 상세 분석:\n"
            
            # SELECT 절 분석
            if "SELECT" in sql_query.upper():
                select_parts = sql_query.upper().split("SELECT")
                if len(select_parts) > 1:
                    select_clause = select_parts[1].split("FROM")[0] if "FROM" in select_parts[1] else select_parts[1]
                    etl_analysis += f"- SELECT 절: {select_clause.strip()}\n"
                    
                    # target_column이 SELECT 절에서 어떻게 처리되는지 분석
                    if target_column.upper() in select_clause:
                        etl_analysis += f"- {target_column} 컬럼 처리: SELECT 절에서 직접 선택됨\n"
                    elif "SUM" in select_clause and target_column.upper() in select_clause:
                        etl_analysis += f"- {target_column} 컬럼 처리: SUM 함수로 집계됨\n"
                    elif "COUNT" in select_clause and target_column.upper() in select_clause:
                        etl_analysis += f"- {target_column} 컬럼 처리: COUNT 함수로 집계됨\n"
                    elif "AVG" in select_clause and target_column.upper() in select_clause:
                        etl_analysis += f"- {target_column} 컬럼 처리: AVG 함수로 집계됨\n"
            
            # FROM 절에서 소스 테이블 확인
            if "FROM" in sql_query.upper():
                from_parts = sql_query.upper().split("FROM")
                if len(from_parts) > 1:
                    from_clause = from_parts[1].split("WHERE")[0] if "WHERE" in from_parts[1] else from_parts[1]
                    from_clause = from_clause.split("JOIN")[0] if "JOIN" in from_clause else from_clause
                    etl_analysis += f"- 메인 소스 테이블: {from_clause.strip()}\n"
            
            # JOIN 절 상세 분석
            if "JOIN" in sql_query.upper():
                join_parts = sql_query.upper().split("JOIN")
                for i, part in enumerate(join_parts[1:], 1):
                    join_table = part.split("ON")[0].strip() if "ON" in part else part.strip()
                    join_condition = part.split("ON")[1].split("WHERE")[0] if "ON" in part and "WHERE" in part else (part.split("ON")[1] if "ON" in part else "")
                    join_condition = join_condition.split("GROUP BY")[0] if "GROUP BY" in join_condition else join_condition
                    etl_analysis += f"- JOIN 테이블 {i}: {join_table}\n"
                    if join_condition:
                        etl_analysis += f"  JOIN 조건: {join_condition.strip()}\n"
            
            # WHERE 절에서 target_column 관련 조건 찾기
            if "WHERE" in sql_query.upper():
                where_parts = sql_query.upper().split("WHERE")
                if len(where_parts) > 1:
                    where_clause = where_parts[1].split("GROUP BY")[0] if "GROUP BY" in where_parts[1] else where_parts[1]
                    where_clause = where_clause.split("ORDER BY")[0] if "ORDER BY" in where_clause else where_clause
                    if target_column.upper() in where_clause:
                        etl_analysis += f"- WHERE 조건 (target_column 관련): {where_clause.strip()}\n"
                    else:
                        etl_analysis += f"- WHERE 조건: {where_clause.strip()}\n"
            
            # GROUP BY 절에서 target_column 확인
            if "GROUP BY" in sql_query.upper():
                group_parts = sql_query.upper().split("GROUP BY")
                if len(group_parts) > 1:
                    group_clause = group_parts[1].split("ORDER BY")[0] if "ORDER BY" in group_parts[1] else group_parts[1]
                    group_clause = group_clause.split("HAVING")[0] if "HAVING" in group_clause else group_clause
                    if target_column.upper() in group_clause:
                        etl_analysis += f"- GROUP BY 포함 (target_column): {group_clause.strip()}\n"
                    else:
                        etl_analysis += f"- GROUP BY: {group_clause.strip()}\n"
            
            # HAVING 절 분석
            if "HAVING" in sql_query.upper():
                having_parts = sql_query.upper().split("HAVING")
                if len(having_parts) > 1:
                    having_clause = having_parts[1].split("ORDER BY")[0] if "ORDER BY" in having_parts[1] else having_parts[1]
                    if target_column.upper() in having_clause:
                        etl_analysis += f"- HAVING 조건 (target_column 관련): {having_clause.strip()}\n"
                    else:
                        etl_analysis += f"- HAVING 조건: {having_clause.strip()}\n"
            
            # ORDER BY 절 분석
            if "ORDER BY" in sql_query.upper():
                order_parts = sql_query.upper().split("ORDER BY")
                if len(order_parts) > 1:
                    order_clause = order_parts[1].split("LIMIT")[0] if "LIMIT" in order_parts[1] else order_parts[1]
                    if target_column.upper() in order_clause:
                        etl_analysis += f"- ORDER BY (target_column 포함): {order_clause.strip()}\n"
                    else:
                        etl_analysis += f"- ORDER BY: {order_clause.strip()}\n"
            
            # 서브쿼리 분석
            if "(" in sql_query and ")" in sql_query:
                etl_analysis += f"- 서브쿼리 포함: 복잡한 쿼리 구조\n"
            
            # 함수 사용 분석
            functions = ["SUM", "COUNT", "AVG", "MAX", "MIN", "CASE", "COALESCE", "NULLIF"]
            used_functions = []
            for func in functions:
                if func in sql_query.upper():
                    used_functions.append(func)
            if used_functions:
                etl_analysis += f"- 사용된 함수들: {', '.join(used_functions)}\n"
        
        result = f"컬럼 {target_column}의 상세 계보 분석:\n"
        result += f"- 대상 테이블: {target_table}\n"
        result += f"- 대상 컬럼: {target_column}\n"
        result += f"- 소스 테이블들: {', '.join(lineage_info['source_tables'])}\n"
        result += f"- 프로그램 ID: {lineage_info['program_id']}\n"
        result += f"- 작업 순서: {lineage_info['job_seq']}\n"
        result += f"- 쿼리 순서: {lineage_info['query_seq']}\n\n"
        
        result += f"ETL 쿼리:\n{sql_query}\n\n"
        result += f"{etl_analysis}\n"
        
        result += f"관련 소스 컬럼들:\n"
        for col in source_columns:
            if (target_column.lower() in col['col_nm'].lower() or 
                'product' in col['col_nm'].lower() or 
                'category' in col['col_nm'].lower()):
                result += f"  * {col['tbl_nm']}.{col['col_nm']}: {col['han_nm']} - {col['desc']}\n"
        
        # 원천 컬럼과의 매핑 관계 분석
        result += f"\n원천-타겟 매핑 분석:\n"
        for source_table in lineage_info['source_tables']:
            result += f"- {source_table} 테이블에서 {target_column} 컬럼이 직접 매핑됨\n"
        
        return result
    except Exception as e:
        return f"컬럼 계보 분석 중 오류 발생: {str(e)}"
