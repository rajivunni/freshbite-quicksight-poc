# FreshBite PoC — Amazon QuickSight + Redshift Serverless BI Dashboard

A fully functional proof-of-concept demonstrating a multi-tenant SaaS BI dashboard built with **Amazon QuickSight** and **Amazon Redshift Serverless**, featuring Row-Level Security (RLS) for franchise-level data isolation.

![Architecture](docs/architecture.png)

## Overview

**Scenario:** FreshBite is a fictional Quick-Service Restaurant (QSR) franchise chain with:
- 10 franchise groups across different US regions
- 50 locations (5 per franchise)
- 20 menu products across 5 categories
- 6 months of daily sales data (~104K records)
- Customer feedback data (~27K records)

**Key features demonstrated:**
- Star schema data modeling optimized for Redshift
- Infrastructure-as-Code (CloudFormation)
- Denormalized analytical views for QuickSight
- Row-Level Security via permissions table
- Interactive dashboard with drill-down filters

## Architecture

```
S3 (CSV staging) → Redshift Serverless → QuickSight Dashboard
                          ↓
              RLS policies (franchise/location filtering)
```

| Component | Service | Detail |
|-----------|---------|--------|
| Data Lake | Amazon S3 | CSV files in star schema |
| Data Warehouse | Redshift Serverless | 8 RPU base, auto-scaling |
| BI Layer | Amazon QuickSight | Enterprise edition with RLS |
| IaC | CloudFormation | One-click deploy |

## Data Model

```
dim_franchises (10 rows)
  └── dim_locations (50 rows)
        └── fact_daily_sales (103,947 rows)
        └── fact_customer_feedback (27,278 rows)
dim_products (20 rows)
rls_user_permissions (11 rules)
```

### Dimension Tables

| Table | Key Fields |
|-------|-----------|
| `dim_franchises` | franchise_id, franchise_name, owner_email, region |
| `dim_locations` | location_id, franchise_id, city, state, open_date |
| `dim_products` | product_id, category, product_name, unit_price |

### Fact Tables

| Table | Key Fields |
|-------|-----------|
| `fact_daily_sales` | sale_date, location_id, product_id, quantity, revenue, cost |
| `fact_customer_feedback` | feedback_date, location_id, rating, response_time_mins |

### RLS Permissions

| Table | Key Fields |
|-------|-----------|
| `rls_user_permissions` | user_email, franchise_id |

## Quick Start

### Prerequisites

- AWS account with access to Redshift Serverless and QuickSight
- AWS CLI configured (or use the Console)
- QuickSight Enterprise edition (required for RLS)

### 1. Deploy Infrastructure

```bash
aws cloudformation deploy \
    --template-file infra/cloudformation_stack.yaml \
    --stack-name freshbite-poc \
    --parameter-overrides \
        Environment=poc \
        DataBucketName=<YOUR_EXISTING_S3_BUCKET> \
        AdminUsername=admin \
        AdminPassword=<YOUR_PASSWORD> \
        BaseCapacity=8 \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1
```

Or upload `infra/cloudformation_stack.yaml` via CloudFormation Console.

### 2. Upload Data to S3

```bash
aws s3 sync ./data/ s3://<YOUR_BUCKET>/freshbite/
```

### 3. Create Schema and Load Data

Connect to Redshift via Query Editor v2, then run:

```bash
# Replace placeholders in the SQL files first:
# - <YOUR_BUCKET> → your S3 bucket name
# - <ROLE_ARN> → RedshiftS3RoleArn from CloudFormation Outputs

# Run in order:
sql/01_create_tables.sql
sql/02_load_data.sql
sql/03_create_views.sql
```

### 4. Connect QuickSight

1. Create a new Redshift data source in QuickSight
2. Use the endpoint from CloudFormation Outputs
3. Select schema `freshbite` → view `vw_sales_dashboard`
4. Build your dashboard (or replicate from screenshots in `docs/`)

### 5. Configure RLS (Optional)

1. Create a dataset from `rls_user_permissions`
2. Attach it as the RLS rules dataset on `vw_sales_dashboard`
3. Map `franchise_id` for row-level filtering per user

## Dashboard Sheets

| Sheet | Purpose |
|-------|---------|
| Executive Summary | KPIs, revenue trend, regional breakdown |
| Sales Performance | Franchise ranking, product mix, profit margins |
| Franchise Drilldown | Filtered view per franchise (simulates RLS) |

## RLS Design

Row-Level Security ensures each franchise owner sees only their own data:

| User Role | Sees |
|-----------|------|
| Corporate Admin | All franchises, all locations |
| Franchise Owner | Only their franchise's locations |
| Location Manager | Single location only |

The `rls_user_permissions` table maps email addresses to `franchise_id`. QuickSight enforces this at query time — no client-side filtering.

## Project Structure

```
freshbite-poc/
├── README.md
├── data/                        # Mock data (CSV)
│   ├── dim_franchises.csv
│   ├── dim_locations.csv
│   ├── dim_products.csv
│   ├── fact_daily_sales.csv
│   ├── fact_customer_feedback.csv
│   └── rls_user_permissions.csv
├── infra/                       # Infrastructure as Code
│   └── cloudformation_stack.yaml
├── sql/                         # Redshift SQL
│   ├── 01_create_tables.sql
│   ├── 02_load_data.sql
│   └── 03_create_views.sql
├── scripts/                     # Utilities
│   └── generate_mock_data.py
└── docs/                        # Documentation
    └── architecture.md
```

## Cleanup

```bash
aws cloudformation delete-stack --stack-name freshbite-poc --region us-east-1
aws s3 rm s3://<YOUR_BUCKET>/freshbite/ --recursive
```

## License

MIT
