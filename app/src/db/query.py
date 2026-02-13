"""
Database utilities for SQL Server connections
"""
import pyodbc
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import settings

def get_connection_string() -> str:
    """Build connection string from environment variables"""
    db_server = settings.DB_SERVER
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    
    if not all([db_server, db_name, db_user, db_password]):
        raise ValueError("Missing database configuration in environment variables")
    
    return f"Driver={{ODBC Driver 17 for SQL Server}};Server=tcp:{db_server},1433;Database={db_name};Uid={db_user};Pwd={db_password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dicts"""
    try:
        conn_str = get_connection_string()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")
