from flask import Flask, jsonify, request, render_template_string
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np # Needed for NaN handling

# ---------------------------------------------------------
# RNCP C5: API EXPOSITION (FLASK VERSION)
# Requirement: 2 Resources, 4 Endpoints, Pagination
# ---------------------------------------------------------

app = Flask(__name__)

# Database Config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YourPassword", # put Your password here
    "database": "project_analytics"
}
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
engine = create_engine(DATABASE_URL)

# --- HOME ROUTE (DOCUMENTATION) ---

@app.route('/')
def api_docs():
    """
    Simple HTML Documentation for the API
    """
    html = """
    <h1>🧴 Gulf Perfume Intelligence API</h1>
    <p>Welcome to the Scent of Success API. Use the endpoints below to query market data.</p>
    
    <h2>Resource 1: Perfumes</h2>
    <ul>
        <li><a href="/api/perfumes">GET /api/perfumes</a> - List all perfumes (paginated)</li>
        <li><a href="/api/perfumes?brand=Lattafa">GET /api/perfumes?brand=Lattafa</a> - Filter by Brand</li>
        <li>GET /api/perfumes/&lt;name&gt; - Get details for a specific perfume</li>
    </ul>

    <h2>Resource 2: Market Trends</h2>
    <ul>
        <li><a href="/api/trends">GET /api/trends</a> - View aggregated market stats</li>
        <li><a href="/api/trends/oud%20perfume">GET /api/trends/oud perfume</a> - Get stats for 'Oud' category</li>
    </ul>
    """
    return render_template_string(html)

# --- RESOURCE 1: PERFUMES ---

@app.route('/api/perfumes', methods=['GET'])
def get_perfumes():
    """
    Endpoint 1: List perfumes with pagination and filtering.
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        brand_filter = request.args.get('brand')

        query_str = "SELECT brand, perfume_name, rating_value FROM perfumes"
        params = {'limit': limit, 'offset': offset}
        
        if brand_filter:
            query_str += " WHERE brand = :brand"
            params['brand'] = brand_filter
            
        query_str += " LIMIT :limit OFFSET :offset"

        with engine.connect() as conn:
            result = conn.execute(text(query_str), params)
            data = [dict(row._mapping) for row in result]
            
        return jsonify({
            "page": page,
            "limit": limit,
            "count": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/perfumes/<string:name>', methods=['GET'])
def get_perfume_detail(name):
    """
    Endpoint 2: Single Object Details
    """
    query_str = "SELECT * FROM perfumes WHERE perfume_name = :name"
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str), {"name": name})
            row = result.fetchone()
            
        if row:
            return jsonify(dict(row._mapping))
        return jsonify({"error": "Perfume not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RESOURCE 2: TRENDS ---

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """
    Endpoint 3: List all market trends
    """
    try:
        query_str = "SELECT * FROM v_perfume_market_trends"
        df = pd.read_sql(query_str, engine)
        
        # FIX 1: Handle NaN values (which break JSON)
        df = df.replace({np.nan: None})
        
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trends/<string:category>', methods=['GET'])
def get_trend_detail(category):
    """
    Endpoint 4: Specific Category Stats
    """
    try:
        # FIX 2: Explicitly use text() for the parameter binding
        query_str = "SELECT * FROM v_perfume_market_trends WHERE Trend_Category = :cat"
        
        # Read into DataFrame to safely handle types/NaNs
        with engine.connect() as conn:
             # We execute first to check logic, but pd.read_sql is safer for DataFrame return
             df = pd.read_sql(text(query_str), conn, params={"cat": category})
        
        if not df.empty:
            df = df.replace({np.nan: None})
            return jsonify(df.to_dict(orient="records")[0])
            
        return jsonify({"error": "Category not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Flask API running on http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)