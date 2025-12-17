# Scent of Success: Hybrid Data Architecture

[View the Presentation Slides](docs/RNCP_Report_Scent_of_Success.pdf)

## Project Context
This project validates delivers a **complete data engineering pipeline** to analyze the shift from "Synthetic" to "Oud/Natural" perfumes in the **Gulf market**, a region where oud perfumes are culturally significant and commercially lucrative.

**Objective:** Build a robust, GDPR-compliant infrastructure to **Collect, Store, Analyze, and Expose** market data in real-time, enabling brands to make data-driven decisions.

---

## Technical Architecture

### Hybrid Data Pipeline
1. **Data Collection (C1)**
   - **Web Scraping (Real-Time):** `scraper.py` uses `cloudscraper` to bypass Cloudflare and fetch live pricing/ratings from Fragrantica. Runs daily, outputs `scraped_live_update.csv`.
   - **Big Data (Scalability):** `bigquery_connector.py` ingests social sentiment logs from Google BigQuery (requires `gcp_keys.json`).
   - **Flat Files (History):** Historical CSV metadata for 60,000+ products.

2. **Storage & Cleaning (C2-C4)**
   - **ETL:** Pandas scripts for normalization (e.g., 1-10 → 1-5 rating scale), deduplication, and GDPR compliance (anonymized User IDs, aggregated demographics).
   - **Database:** MySQL for structured data (ACID compliance for Brand/Product hierarchies).

3. **Exposition (C5)**
   - **REST API:** FastAPI (production) and Flask (alternative). Both expose SQL data via HTTP endpoints.
   - **Architecture Decision: FastAPI vs. Flask**
     | Feature       | FastAPI (Selected)             | Flask (Alternative)       |
     |---------------|--------------------------------|---------------------------|
     | Performance   | Async (ASGI), high concurrency | Sync (WSGI), blocking     |
     | Documentation | Auto Swagger UI (`/docs`)      | Manual setup required     |
     | Validation    | Pydantic (strong typing)       | Manual validation         |

---

### Repository Structure

gulf-perfume-market/
├── data/
│   ├── fragrance_combined_cleaned.csv  # Final cleaned dataset
│   ├── scraped_live_update.csv         # Output of scraper.py
│   └── bigquery_extract.csv            # Output of bigquery_connector.py
├── sql/
│   ├── schema_setup.sql                # Table creation & Views
│   └── analysis_queries.sql            # 5 KPI Queries (see below)
├── notebooks/
│   └── perfume_market_prediction.ipynb # Jupyter Notebook (ML analysis)
├── docs/
│   ├── RNCP_Report_Scent_of_Success.pdf # Final Report
|
├── images/
│   ├── architecture_diagram.png        # Diagram of data flow
│   ├── api_swagger_screenshot.png      # API endpoints
│   |── trello_board.png                # Planning
│   ├── oud_cluster.png                 # Visualization
│   ├── market_search_volume.png        # Visualization
│   └── gcc_perfume_trend.png           # Visualization
|
├── api_main.py                         # Production FastAPI App
├── api_flask.py                        # Alternative Flask App
├── bigquery_connector.py               # BigQuery data ingest
├── scraper.py                          # Web Scraper
├── requirements.txt                    # Python dependencies
└── README.md

---

Key Insights & SQL Analysis

### Top 5 KPIs from SQL Queries

1. **Category Trends:**
   | Trend_Category     | Product_Count | Avg_Product_Rating | Market_Search_Volume | Market_Growth_Trend|
   |--------------------|---------------|--------------------|----------------------|--------------------|
   | Oud Perfume        | 4,911         | 4.17               | 0.001                | 0.025              |
   | Natural Perfume    | 17,512        | 4.00               | 0.39                 | 0.17               |
   | General Perfume    | 44,447        | 4.15               | 0.55                 | 0.25               |

2. **Oud Perfume Brands:**
   | brand          | oud_perfume_count |
   |----------------|-------------------|
   | Al Haramain    | 33                |
   | Paris Corner   | 9                 |
   | Lattafa        | 7                 |

3. **Product Volume vs. Satisfaction Score:**
   | Trend_Category      | Product_Volume | Avg_Satisfaction_Score|
   |--------------------|----------------|------------------------|
   | Oud Perfume        | 4,911          | 4.17                   |
   | General Perfume    | 44,447         | 4.15                   |
   | Natural Perfume    | 17,512         | 4.00                   |

4. **Top-Rated Perfumes:**
   | perfume_name                              | brand         | Rating | Votes |
   |-------------------------------------------|---------------|--------|-------|
   | Alexandria II (Xerjoff 2017)              | Xerjoff       | 9.2    | 86    |
   | Blue Contemporary (Enrico Coveri 1998)    | Enrico Coveri | 8.8    | 71    |

5. **Regional Demand:**
   | keyword_term       | growth_rate | mean_demand |
   |--------------------|-------------|-------------|
   | Perfume Qatar      | 1.00        | 0.40        |
   | Arabian Oud        | 0.72        | 0.19        |
   | Oud UAE            | 0.51        | 0.51        |

**Conclusion:**
Oud perfumes **outperform** natural and general perfumes in both **rating (4.17 vs. 4.00)** and **demand growth**, especially in **Qatar and UAE**. Brands should prioritize oud-based formulations and regional targeting.

---

## How to Run the Project

**Dockerfile and docker-compose.yml for easy deployment, not included due to time constraints, but recommended for production.**

### Prerequisites
- Python 3.9+
- MySQL 8.0+
- Google Cloud credentials (`gcp_keys.json`) 
# Note: `gcp_keys.json` is required for BigQuery access (not included for security).

### Setup
``bash
git clone https://github.com/YOUR_USERNAME/gulf-perfume-market.git
pip install -r requirements.txt
# Set environment variables (see .env.example)

**Run**
# 1. Scrape live data
python scraper.py  # Output: data/scraped_live_update.csv

# 2. Ingest BigQuery data
python bigquery_connector.py  # Output: data/bigquery_extract.csv

# 3. Start API (FastAPI recommended)
python api_main.py  # Swagger UI: http://127.0.0.1:8000/docs

## ML Findings

Random Forest Classifier: 71% accuracy in predicting market success.
Feature Importance: Social Purchase Intent > Price Elasticity > Brand Reputation.
Visualization: Oud perfumes show a stronger correlation between rating count and rating value, indicating consistent quality recognition.

### Known Limitations

The scraper may break if Fragrantica updates its HTML structure.
The dataset is limited to the Gulf region; expanding to other markets would require additional data sources.
The ML model could be improved with more features (e.g., seasonal trends, competitor pricing).

### Compliance & Documentation

GDPR: User IDs anonymized (SHA-256), demographics aggregated.
RNCP Alignment: Explicitly maps to C1-C5 competencies (see report).
License: MIT (see LICENSE).

---

**[View initial version of project]**
[v1](https://github.com/rmoind/gulf-perfume-market-prediction)

Project developed for Ironhack & RNCP Certification.
*Project by Rahala MOINDZE - Ironhack Data Analytics Bootcamp 2025*