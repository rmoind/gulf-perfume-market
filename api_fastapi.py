import uvicorn
from fastapi import FastAPI, HTTPException, Query, Path
from sqlalchemy import create_engine, text
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np # Needed for NaN handling



# 1. Database Config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YourPassword", # put Your password here
    "database": "project_analytics"
}
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
engine = create_engine(DATABASE_URL)

# 2. Initialize FastAPI
app = FastAPI(
    title="Gulf Perfume Intelligence API",
    description="REST API for Scent of Success Project. Features 2 resources and pagination.",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 3. Pydantic Models (Data Validation & Documentation)
class PerfumeSummary(BaseModel):
    brand: str
    perfume_name: str
    rating_value: float

class PerfumeDetail(BaseModel):
    brand: str
    perfume_name: str
    rating_value: Optional[float]
    rating_count: Optional[int]
    main_accords: Optional[str] = None
    # Add other columns as needed

class PaginatedResponse(BaseModel):
    page: int
    limit: int
    count: int
    data: List[PerfumeSummary]

class TrendStat(BaseModel):
    Trend_Category: str
    avg_rating: Optional[float]
    volume: Optional[int]
    
# RESOURCE 1: PERFUMES

@app.get("/api/perfumes", response_model=PaginatedResponse, tags=["Perfumes"])
def list_perfumes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    brand: Optional[str] = Query(None, description="Filter by Brand Name")
):
    """
    **Endpoint 1:** List perfumes with pagination and filtering.
    - **page**: The page number (starts at 1)
    - **limit**: Number of items to return
    - **brand**: (Optional) Filter by brand name
    """
    offset = (page - 1) * limit
    
    query_str = "SELECT brand, perfume_name, rating_value FROM perfumes"
    params = {'limit': limit, 'offset': offset}
    
    if brand:
        query_str += " WHERE brand = :brand"
        params['brand'] = brand
        
    query_str += " LIMIT :limit OFFSET :offset"

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str), params)
            data = [dict(row._mapping) for row in result]
            
        return {
            "page": page,
            "limit": limit,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/perfumes/{name}", response_model=Dict[str, Any], tags=["Perfumes"])
def get_perfume_detail(
    name: str = Path(..., description="Exact name of the perfume")
):
    """
    **Endpoint 2:** Get detailed information for a single perfume object.
    """
    query_str = "SELECT * FROM perfumes WHERE perfume_name = :name"
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str), {"name": name})
            row = result.fetchone()
            
        if row:
            # Convert row to dict and handle NaNs for JSON safety
            data_dict = dict(row._mapping)
            for key, value in data_dict.items():
                if isinstance(value, float) and np.isnan(value):
                    data_dict[key] = None
            return data_dict
            
        raise HTTPException(status_code=404, detail="Perfume not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RESOURCE 2: TRENDS

@app.get("/api/trends", response_model=List[Dict[str, Any]], tags=["Market Trends"])
def list_trends():
    """
    **Endpoint 3:** View aggregated market stats (All Categories).
    """
    try:
        query_str = "SELECT * FROM v_perfume_market_trends"
        df = pd.read_sql(query_str, engine)
        
        # Handle NaN values
        df = df.replace({np.nan: None})
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends/{category}", response_model=Dict[str, Any], tags=["Market Trends"])
def get_trend_detail(
    category: str = Path(..., description="Category name (e.g., 'oud perfume')")
):
    """
    **Endpoint 4:** Get stats for a specific Trend Category.
    """
    try:
        # Use text() for safe parameter binding
        query_str = "SELECT * FROM v_perfume_market_trends WHERE Trend_Category = :cat"
        
        with engine.connect() as conn:
             df = pd.read_sql(text(query_str), conn, params={"cat": category})
        
        if not df.empty:
            df = df.replace({np.nan: None})
            return df.to_dict(orient="records")[0]
            
        raise HTTPException(status_code=404, detail="Category not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    print(" FastAPI running on http://127.0.0.1:8000")
    print(" Swagger UI available at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)