-- ============================================================
-- FreshBite PoC: Load Data from S3
-- ============================================================
-- Replace these placeholders before running:
--   <YOUR_BUCKET>  → your S3 bucket name
--   <ROLE_ARN>     → RedshiftS3RoleArn from CloudFormation Outputs

COPY freshbite.dim_franchises
FROM 's3://<YOUR_BUCKET>/freshbite/dim_franchises.csv'
IAM_ROLE '<ROLE_ARN>'
CSV IGNOREHEADER 1
REGION 'us-east-1';

COPY freshbite.dim_locations
FROM 's3://<YOUR_BUCKET>/freshbite/dim_locations.csv'
IAM_ROLE '<ROLE_ARN>'
CSV IGNOREHEADER 1
REGION 'us-east-1';

COPY freshbite.dim_products
FROM 's3://<YOUR_BUCKET>/freshbite/dim_products.csv'
IAM_ROLE '<ROLE_ARN>'
CSV IGNOREHEADER 1
REGION 'us-east-1';

COPY freshbite.fact_daily_sales
FROM 's3://<YOUR_BUCKET>/freshbite/fact_daily_sales.csv'
IAM_ROLE '<ROLE_ARN>'
CSV IGNOREHEADER 1
REGION 'us-east-1';

COPY freshbite.fact_customer_feedback
FROM 's3://<YOUR_BUCKET>/freshbite/fact_customer_feedback.csv'
IAM_ROLE '<ROLE_ARN>'
CSV IGNOREHEADER 1
REGION 'us-east-1';

COPY freshbite.rls_user_permissions
FROM 's3://<YOUR_BUCKET>/freshbite/rls_user_permissions.csv'
IAM_ROLE '<ROLE_ARN>'
CSV IGNOREHEADER 1
REGION 'us-east-1';

-- ============================================================
-- Verify row counts
-- ============================================================
SELECT 'dim_franchises' AS table_name, COUNT(*) AS row_count FROM freshbite.dim_franchises
UNION ALL SELECT 'dim_locations', COUNT(*) FROM freshbite.dim_locations
UNION ALL SELECT 'dim_products', COUNT(*) FROM freshbite.dim_products
UNION ALL SELECT 'fact_daily_sales', COUNT(*) FROM freshbite.fact_daily_sales
UNION ALL SELECT 'fact_customer_feedback', COUNT(*) FROM freshbite.fact_customer_feedback
UNION ALL SELECT 'rls_user_permissions', COUNT(*) FROM freshbite.rls_user_permissions
ORDER BY 1;

-- Expected:
-- dim_franchises:          10
-- dim_locations:           50
-- dim_products:            20
-- fact_daily_sales:        103,947
-- fact_customer_feedback:  27,278
-- rls_user_permissions:    11
