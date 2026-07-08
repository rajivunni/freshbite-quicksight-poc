-- ============================================================
-- FreshBite PoC: Analytical Views for QuickSight
-- ============================================================

-- Main sales dashboard view (denormalized)
CREATE OR REPLACE VIEW freshbite.vw_sales_dashboard AS
SELECT
    s.sale_date,
    s.location_id,
    l.location_name,
    l.city,
    l.state,
    l.franchise_id,
    f.franchise_name,
    f.owner_email,
    f.region,
    s.product_id,
    p.product_name,
    p.category AS product_category,
    p.unit_price,
    s.quantity,
    s.revenue,
    s.cost,
    s.revenue - s.cost AS gross_profit,
    ROUND((s.revenue - s.cost) / NULLIF(s.revenue, 0) * 100, 1) AS margin_pct
FROM freshbite.fact_daily_sales s
JOIN freshbite.dim_locations l ON s.location_id = l.location_id
JOIN freshbite.dim_franchises f ON l.franchise_id = f.franchise_id
JOIN freshbite.dim_products p ON s.product_id = p.product_id;

-- Customer feedback view
CREATE OR REPLACE VIEW freshbite.vw_feedback_dashboard AS
SELECT
    fb.feedback_date,
    fb.location_id,
    l.location_name,
    l.city,
    l.state,
    l.franchise_id,
    f.franchise_name,
    f.owner_email,
    f.region,
    fb.rating,
    fb.response_time_mins
FROM freshbite.fact_customer_feedback fb
JOIN freshbite.dim_locations l ON fb.location_id = l.location_id
JOIN freshbite.dim_franchises f ON l.franchise_id = f.franchise_id;

-- Location KPI summary (pre-aggregated)
CREATE OR REPLACE VIEW freshbite.vw_location_kpis AS
SELECT
    l.location_id,
    l.location_name,
    l.city,
    l.state,
    f.franchise_id,
    f.franchise_name,
    f.region,
    f.owner_email,
    COUNT(DISTINCT s.sale_date) AS active_days,
    SUM(s.revenue) AS total_revenue,
    SUM(s.cost) AS total_cost,
    SUM(s.revenue) - SUM(s.cost) AS total_profit,
    ROUND(AVG(s.revenue), 2) AS avg_daily_revenue,
    SUM(s.quantity) AS total_units_sold,
    ROUND(SUM(s.revenue) / NULLIF(SUM(s.quantity), 0), 2) AS avg_ticket_size
FROM freshbite.fact_daily_sales s
JOIN freshbite.dim_locations l ON s.location_id = l.location_id
JOIN freshbite.dim_franchises f ON l.franchise_id = f.franchise_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8;

-- ============================================================
-- Row-Level Security Setup (QuickSight Dataset-Level)
-- ============================================================
-- To enable RLS in QuickSight:
-- 1. Create a dataset from this query:
--      SELECT owner_email AS UserName, franchise_id
--      FROM freshbite.rls_user_permissions
--      WHERE franchise_id != 'ALL';
-- 2. Attach it as the RLS rules dataset on vw_sales_dashboard
-- 3. Map franchise_id column for row-level filtering
--
-- Corporate admin (admin@freshbite-corp.com) has franchise_id = 'ALL'
-- and should be excluded from RLS (sees everything by default).
