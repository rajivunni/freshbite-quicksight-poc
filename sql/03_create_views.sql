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
-- Legacy aliases below are not validated business KPI definitions:
-- avg_daily_revenue averages product-day rows, not location daily totals.
-- avg_ticket_size is revenue per unit, not per transaction (no order IDs exist).
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
-- Illustrative Row-Level Security Setup (not deployed or enforced here)
-- ============================================================
-- Manual evaluation requires actual QuickSight identities and service-side tests.
-- The following owner-only query is a starting point, not a complete policy:
--      SELECT user_email AS UserName, franchise_id
--      FROM freshbite.rls_user_permissions
--      WHERE franchise_id != 'ALL';
-- Configure an RLS rules dataset manually and verify allowed and denied rows.
-- Apply the intended controls to every exposed dataset, including feedback.
--
-- ALL is only a fixture marker, not an implemented wildcard permission.
-- This query excludes that marker and does not define corporate admin access.
-- No native Redshift policies or location-manager permissions are implemented.
