-- 1. Create the Database
CREATE DATABASE IF NOT EXISTS project_analytics;
USE project_analytics;

-- NOTE: The raw tables were loaded directly from Pandas DataFrames using Python (SQLAlchemy).
-- 2. Create view maps individual products to broader market trend categories allowing us to link Product Data with Google Trends Data.

CREATE OR REPLACE VIEW v_perfume_market_trends AS
SELECT 
    p.brand,
    p.perfume_name,
    p.rating_value,
    p.`Main Accords`,
    -- assign a Trend Category based on ingredients/name
    CASE 
        WHEN LOWER(p.`Main Accords`) LIKE '%oud%' OR LOWER(p.perfume_name) LIKE '%oud%' THEN 'oud perfume'
        WHEN LOWER(p.longevity) LIKE '%eternal%' OR LOWER(p.longevity) LIKE '%long%' THEN 'long lasting perfume'
        WHEN LOWER(p.`Main Accords`) LIKE '%green%' OR LOWER(p.`Main Accords`) LIKE '%herbal%' THEN 'natural perfume'
        ELSE 'perfume' -- Fallback to general category
    END AS Trend_Category
FROM perfumes p;

