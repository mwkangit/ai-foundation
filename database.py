import pymysql
import pandas as pd
from typing import Dict, List, Any, Optional
from config import MYSQL_CONFIG

class MySQLDatabase:
    def __init__(self):
        self.config = MYSQL_CONFIG
        self.connection = None
    
    def connect(self):
        """MySQL 데이터베이스에 연결합니다."""
        try:
            self.connection = pymysql.connect(**self.config)
            return True
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결을 종료합니다."""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """SQL 쿼리를 실행하고 결과를 DataFrame으로 반환합니다."""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            
            # PyMySQL에서는 %s를 사용해야 함
            if params:
                query = query.replace('?', '%s')
            
            df = pd.read_sql_query(query, self.connection, params=params)
            return df
        except Exception as e:
            print(f"쿼리 실행 실패: {e}")
            return pd.DataFrame()
    
    def get_table_lineage(self, target_table: str) -> Dict[str, Any]:
        """테이블의 계보 정보를 조회합니다."""
        query = """
        SELECT 
            SRC_TBL_NM,
            TRGT_TBL_NM,
            PGM_ID,
            JOB_SEQ,
            QRY_SEQ,
            SRC_DB_NM,
            TRGT_DB_NM
        FROM pgm_qry.pgm_qry_tbl_dtl 
        WHERE TRGT_TBL_NM = ?
        ORDER BY SRC_TBL_NM_SEQ
        """
        
        df = self.execute_query(query, (target_table,))
        
        if df.empty:
            return {"error": f"테이블 {target_table}의 계보 정보를 찾을 수 없습니다."}
        
        lineage_info = {
            "target_table": target_table,
            "source_tables": df['SRC_TBL_NM'].tolist(),
            "program_id": df['PGM_ID'].iloc[0],
            "job_seq": df['JOB_SEQ'].iloc[0],
            "query_seq": df['QRY_SEQ'].iloc[0],
            "source_databases": df['SRC_DB_NM'].dropna().unique().tolist(),
            "target_database": df['TRGT_DB_NM'].iloc[0]
        }
        
        return lineage_info
    
    def get_etl_query(self, program_id: str, job_seq: int, query_seq: int) -> str:
        """ETL 쿼리를 조회합니다."""
        query = """
        SELECT ORGL_SQL, STATEMENT_TYP, PGM_PATH
        FROM pgm_qry.pgm_qry_mst 
        WHERE PGM_ID = ? AND JOB_SEQ = ? AND QRY_SEQ = ?
        """
        
        df = self.execute_query(query, (program_id, job_seq, query_seq))
        
        if df.empty:
            return f"프로그램 {program_id}의 ETL 쿼리를 찾을 수 없습니다."
        
        result = {
            "sql": df['ORGL_SQL'].iloc[0].decode('utf-8') if df['ORGL_SQL'].iloc[0] else "",
            "statement_type": df['STATEMENT_TYP'].iloc[0],
            "program_path": df['PGM_PATH'].iloc[0]
        }
        
        return result
    
    def get_table_metadata(self, table_name: str, database_name: str = None) -> Dict[str, Any]:
        """테이블 메타데이터를 조회합니다."""
        if database_name:
            query = """
            SELECT tbl_nm, db_nm, han_nm, `desc`
            FROM metadata.tbl_mst 
            WHERE tbl_nm = ? AND db_nm = ?
            """
            df = self.execute_query(query, (table_name, database_name))
        else:
            query = """
            SELECT tbl_nm, db_nm, han_nm, `desc`
            FROM metadata.tbl_mst 
            WHERE tbl_nm = ?
            """
            df = self.execute_query(query, (table_name,))
        
        if df.empty:
            return {"error": f"테이블 {table_name}의 메타데이터를 찾을 수 없습니다."}
        
        return df.iloc[0].to_dict()
    
    def get_column_metadata(self, table_name: str, column_name: str = None, database_name: str = None) -> List[Dict[str, Any]]:
        """컬럼 메타데이터를 조회합니다."""
        if column_name and database_name:
            query = """
            SELECT col_nm, tbl_nm, db_nm, han_nm, `desc`
            FROM metadata.col_mst 
            WHERE tbl_nm = ? AND col_nm = ? AND db_nm = ?
            """
            df = self.execute_query(query, (table_name, column_name, database_name))
        elif column_name:
            query = """
            SELECT col_nm, tbl_nm, db_nm, han_nm, `desc`
            FROM metadata.col_mst 
            WHERE tbl_nm = ? AND col_nm = ?
            """
            df = self.execute_query(query, (table_name, column_name))
        else:
            query = """
            SELECT col_nm, tbl_nm, db_nm, han_nm, `desc`
            FROM metadata.col_mst 
            WHERE tbl_nm = ?
            ORDER BY col_nm
            """
            df = self.execute_query(query, (table_name,))
        
        if df.empty:
            return [{"error": f"테이블 {table_name}의 컬럼 메타데이터를 찾을 수 없습니다."}]
        
        return df.to_dict('records')
    
    def get_source_table_structure(self, table_name: str, database_name: str) -> Dict[str, Any]:
        """원천 테이블의 구조를 조회합니다."""
        query = f"""
        DESCRIBE {database_name}.{table_name}
        """
        
        df = self.execute_query(query)
        
        if df.empty:
            return {"error": f"테이블 {database_name}.{table_name}의 구조를 조회할 수 없습니다."}
        
        columns = []
        for _, row in df.iterrows():
            columns.append({
                "field": row['Field'],
                "type": row['Type'],
                "null": row['Null'],
                "key": row['Key'],
                "default": row['Default'],
                "extra": row['Extra']
            })
        
        return {
            "table_name": table_name,
            "database_name": database_name,
            "columns": columns
        }
