# Architecture

## System Overview

```
┌──────────────┐     ┌─────────────────────────┐     ┌──────────────────────┐
│              │     │                         │     │                      │
│   Amazon S3  │────▶│  Redshift Serverless    │────▶│  Amazon QuickSight   │
│  (CSV Data)  │     │  (Star Schema + Views)  │     │  (BI Dashboard)      │
│              │     │                         │     │                      │
└──────────────┘     └─────────────────────────┘     └──────────────────────┘
                              │                               │
                              ▼                               ▼
                     ┌─────────────────┐            ┌─────────────────┐
                     │  RLS Policies   │            │  Row-Level      │
                     │  (Permissions   │            │  Security       │
                     │   Table)        │            │  (Per-User)     │
                     └─────────────────┘            └─────────────────┘
```

## Components

| Layer | Service | Purpose |
|-------|---------|---------|
| Storage | Amazon S3 | Staging area for CSV data files |
| Compute | Redshift Serverless | Star schema warehouse with analytical views |
| BI | Amazon QuickSight | Interactive dashboards with RLS |
| IaC | CloudFormation | Automated infrastructure deployment |

## Data Flow

1. **Generate** → Python script creates mock data (6 CSVs in star schema)
2. **Stage** → Upload CSVs to S3 bucket
3. **Load** → Redshift COPY commands ingest from S3
4. **Transform** → Denormalized views pre-join dimensions + facts
5. **Visualize** → QuickSight connects to views via Direct Query
6. **Secure** → RLS maps user emails to franchise IDs

## Security Model

Row-Level Security is implemented at two levels:

1. **Redshift Native RLS** (optional) — policies on base tables
2. **QuickSight Dataset RLS** (recommended for this PoC) — rules dataset maps users to allowed franchise_ids

The permissions table (`rls_user_permissions`) drives both approaches:
- `admin@freshbite-corp.com` → `ALL` (corporate view)
- `sarah.johnson@freshbite-north.com` → `FR-001` (single franchise)

## Scaling Considerations

For production deployments:
- Move from CSV/COPY to streaming ingestion (Kinesis → Redshift)
- Enable SPICE in QuickSight for sub-second dashboard loads
- Add location-level RLS for individual store managers
- Implement Redshift materialized views for complex aggregations
- Add CloudWatch alarms for RPU utilization
