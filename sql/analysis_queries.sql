USE project_analytics;

-- Verify you can link Perfumes to Trends
SELECT 
    p.brand, 
    p.perfume_name, 
    p.rating_value,
    t.mean_demand,
    t.growth_rate
FROM perfumes p
INNER JOIN trend_features t 
    ON LOWER(p.perfume_name) = LOWER(t.keyword_term)
ORDER BY t.mean_demand DESC
LIMIT 10;

-- Create a View that maps specific perfumes to generic Google Trend keywords.

CREATE OR REPLACE VIEW v_perfume_market_trends AS
SELECT 
    p.brand,
    p.perfume_name,
    p.rating_value,
    p.`Main Accords`,
    -- Logic to assign a Trend Category
    CASE 
        WHEN LOWER(p.`Main Accords`) LIKE '%oud%' OR LOWER(p.perfume_name) LIKE '%oud%' THEN 'oud perfume'
        WHEN LOWER(p.longevity) LIKE '%eternal%' OR LOWER(p.longevity) LIKE '%long%' THEN 'long lasting perfume'
        WHEN LOWER(p.`Main Accords`) LIKE '%green%' OR LOWER(p.`Main Accords`) LIKE '%herbal%' THEN 'natural perfume'
        ELSE 'perfume' -- Fallback to general category
    END AS Trend_Category
FROM perfumes p;

SELECT 
    v.Trend_Category,
    COUNT(v.perfume_name) as Product_Count,
    ROUND(AVG(v.rating_value), 2) as Avg_Product_Rating,
    t.mean_demand as Market_Search_Volume,
    t.growth_rate as Market_Growth_Trend
FROM v_perfume_market_trends v
INNER JOIN trend_features t 
    ON v.Trend_Category = t.keyword_term
GROUP BY v.Trend_Category, t.mean_demand, t.growth_rate
ORDER BY t.mean_demand DESC;

-- FIND THE MARKET LEADERS (VOLUME)
SELECT 
    brand, 
    COUNT(*) AS oud_perfume_count
FROM perfumes
WHERE LOWER(`Main Accords`) LIKE '%oud%' 
   OR LOWER(perfume_name) LIKE '%oud%'
GROUP BY brand
ORDER BY oud_perfume_count DESC
LIMIT 5;

-- COMPARE CATEGORY SATISFACTION
SELECT 
    Trend_Category,
    COUNT(*) as Product_Volume,
    ROUND(AVG(rating_value), 2) as Avg_Satisfaction_Score
FROM v_perfume_market_trends
GROUP BY Trend_Category
ORDER BY Avg_Satisfaction_Score DESC;

-- FIND THE HIGHEST RATED OUD PERFUMES (Fixed Column Names) 
SELECT 
    perfume_name, 
    brand, 
    rating_value as Rating,
    rating_count as Votes
FROM perfumes
WHERE (LOWER(`Main Accords`) LIKE '%oud%' OR LOWER(perfume_name) LIKE '%oud%')
  AND rating_count > 50 
ORDER BY rating_value DESC
LIMIT 5;

-- Trend Growth Rate (Growth Analysis)
SELECT 
    keyword_term,
    growth_rate,
    mean_demand
FROM trend_features
ORDER BY growth_rate DESC
LIMIT 5;

-- (Assuming we loaded the BigQuery extract into a local table for this analysis)

-- Social Sentiment Correlation (Category Level)
SELECT 
    v.Trend_Category,
    ROUND(AVG(v.rating_value), 2) as avg_product_rating,
    ROUND(AVG(t.mean_demand), 2) as avg_search_volume
FROM v_perfume_market_trends v
JOIN trend_features t ON v.Trend_Category = t.keyword_term
GROUP BY v.Trend_Category
ORDER BY avg_search_volume DESC;