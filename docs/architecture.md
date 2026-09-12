# Architecture and implementation status

## Data path

~~~
Python generator -> six synthetic CSV files -> existing S3 bucket
                                                   |
                                                   v
                                   Redshift Serverless tables
                                                   |
                                                   v
                                     denormalized SQL views
                                                   |
                                                   v
                             QuickSight, configured manually
~~~

## Implemented source

The CloudFormation template defines a Redshift Serverless namespace/workgroup and two IAM roles. SQL defines dimension, fact and illustrative permission tables, plus sales, feedback and location-summary views.

The data generator uses a fixed seed to produce January through June 2026 fixtures. All names and email addresses are synthetic.

## Manual components

QuickSight connectivity, datasets, analyses, dashboards, identities and RLS configuration are not deployed by this repository. There is no included dashboard export or screenshot proving those settings.

The permissions table is data, not an active access policy. Its `ALL` marker does not grant access by itself. The example SQL alias must be mapped to real QuickSight identities before any RLS evaluation. The owner-only example excludes the admin marker and does not define corporate access.

Native Redshift RLS, location-level manager permissions, identity provisioning and tenant-isolation tests against a live service are not implemented.

## Analytical limits

The sales grain is date, location and product. It is not a transaction ledger. The location view's legacy `avg_daily_revenue` field averages product-day rows, while `avg_ticket_size` divides revenue by units. These aliases need correction before use as business KPIs.

## Deployment and security status

Only offline source/data checks are included. AWS provisioning, QuickSight connectivity and RLS behavior have not been verified as part of this publication cleanup. Read [SECURITY.md](../SECURITY.md) before any AWS evaluation.
