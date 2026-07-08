-- ============================================================
-- FreshBite PoC: Create Schema and Tables
-- ============================================================

CREATE SCHEMA IF NOT EXISTS freshbite;

CREATE TABLE freshbite.dim_franchises (
    franchise_id    VARCHAR(10) PRIMARY KEY,
    franchise_name  VARCHAR(100) NOT NULL,
    owner_name      VARCHAR(100) NOT NULL,
    owner_email     VARCHAR(200) NOT NULL,
    region          VARCHAR(50) NOT NULL
)
DISTSTYLE ALL
SORTKEY (franchise_id);

CREATE TABLE freshbite.dim_locations (
    location_id     VARCHAR(10) PRIMARY KEY,
    franchise_id    VARCHAR(10) NOT NULL REFERENCES freshbite.dim_franchises(franchise_id),
    location_name   VARCHAR(100) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    state           VARCHAR(5) NOT NULL,
    open_date       DATE NOT NULL
)
DISTSTYLE ALL
SORTKEY (franchise_id, location_id);

CREATE TABLE freshbite.dim_products (
    product_id      VARCHAR(10) PRIMARY KEY,
    category        VARCHAR(50) NOT NULL,
    product_name    VARCHAR(100) NOT NULL,
    unit_price      DECIMAL(8,2) NOT NULL
)
DISTSTYLE ALL
SORTKEY (category, product_id);

CREATE TABLE freshbite.fact_daily_sales (
    sale_date       DATE NOT NULL,
    location_id     VARCHAR(10) NOT NULL REFERENCES freshbite.dim_locations(location_id),
    product_id      VARCHAR(10) NOT NULL REFERENCES freshbite.dim_products(product_id),
    quantity        INTEGER NOT NULL,
    revenue         DECIMAL(12,2) NOT NULL,
    cost            DECIMAL(12,2) NOT NULL
)
DISTKEY (location_id)
SORTKEY (sale_date, location_id);

CREATE TABLE freshbite.fact_customer_feedback (
    feedback_date       DATE NOT NULL,
    location_id         VARCHAR(10) NOT NULL REFERENCES freshbite.dim_locations(location_id),
    rating              DECIMAL(2,1) NOT NULL,
    response_time_mins  INTEGER NOT NULL
)
DISTKEY (location_id)
SORTKEY (feedback_date, location_id);

CREATE TABLE freshbite.rls_user_permissions (
    user_email      VARCHAR(200) NOT NULL,
    franchise_id    VARCHAR(10) NOT NULL
);
