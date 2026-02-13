"""
Test Endpoints - for validating database connectivity
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.query import execute_query

router = APIRouter()

class TestRecord(BaseModel):
    Id: int
    Name: str
    Description: Optional[str] = None
    CreatedAt: datetime

@router.get("/test", response_model=List[TestRecord])
async def get_test_records():
    """Get all test records from database"""
    try:
        query = "SELECT Id, Name, Description, CreatedAt FROM [dbo].[Test] ORDER BY Id"
        results = execute_query(query)
        
        # Convert to TestRecord models
        records = []
        for row in results:
            records.append(TestRecord(
                Id=row['Id'],
                Name=row['Name'],
                Description=row['Description'],
                CreatedAt=row['CreatedAt']
            ))
        
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch test records: {str(e)}")

@router.post("/test")
async def create_test_record(record: TestRecord):
    """Create a new test record"""
    try:
        query = "INSERT INTO [dbo].[Test] (Name, Description) VALUES (?, ?)"
        execute_query(query, (record.Name, record.Description))
        return {"status": "success", "message": "Test record created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create test record: {str(e)}")
