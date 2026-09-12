# FreshBite: Redshift Serverless and QuickSight BI Starter

A portfolio proof of concept for a fictional restaurant franchise. It contains synthetic CSV data, a Redshift star schema, analytical SQL views, a data generator and CloudFormation source for a Redshift Serverless workgroup and supporting IAM roles.

QuickSight dashboards and row-level security must be configured manually. This repository does not contain an exported dashboard, a QuickSight dataset resource or an enforced RLS policy. No live AWS deployment was performed for this publication cleanup.

## Included data

| Dataset | Rows |
| --- | ---: |
| Franchises | 10 |
| Locations | 50 |
| Products | 20 |
| Daily sales | 103,947 |
| Customer feedback | 27,278 |
| Illustrative permission mappings | 11 |

Sales and feedback cover January through June 2026. Names and email addresses are synthetic. The generator uses a fixed random seed.

## Architecture

~~~
Synthetic CSV files -> existing S3 bucket -> Redshift tables and views
                                                   |
                                                   v
                                  manually configured QuickSight dataset/dashboard
~~~

See [architecture notes](docs/architecture.md) for the implementation boundary.

## Repository

- `infra/cloudformation_stack.yaml`: Redshift namespace/workgroup and IAM roles. It uses an existing S3 bucket.
- `sql/01_create_tables.sql`: schema and six tables.
- `sql/02_load_data.sql`: S3 COPY statements and row-count checks.
- `sql/03_create_views.sql`: sales, feedback and location KPI views, plus illustrative RLS setup notes.
- `data/`: synthetic CSV fixtures.
- `scripts/generate_mock_data.py`: regeneration script requiring pandas and NumPy.
- `tests/test_data.py`: standard-library offline fixture and source checks.
- `SECURITY.md`: current security limits.

## Offline checks

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
~~~

These checks validate data shape, foreign-key references, Python syntax and selected source assumptions. They do not run Redshift SQL, validate CloudFormation against AWS, or prove tenant isolation.

To regenerate the data, first install pandas and NumPy in your own environment, then run the generator into a separate output directory. Dependency versions are not pinned and byte-for-byte reproduction across versions is not guaranteed.

~~~bash
python3 scripts/generate_mock_data.py --output-dir ./generated-data
~~~

## Manual AWS evaluation

AWS resources can incur charges. Review the template, current service requirements and [security notes](SECURITY.md) before creating resources.

1. Provide a dedicated existing S3 bucket and review network/IAM settings. The template currently sets `PubliclyAccessible: true`.
2. Validate and deploy the CloudFormation template using your normal AWS process. Parameters are `Environment`, `DataBucketName`, `AdminUsername`, `AdminUserPassword` and `BaseCapacity`. The password parameter is named `AdminUserPassword`, not `AdminPassword`.
3. Upload the six CSV files to a `freshbite/` prefix in that bucket.
4. Replace `<YOUR_BUCKET>` and `<ROLE_ARN>` in the load SQL. The supplied COPY commands specify `us-east-1`; reconcile the region with your deployment.
5. Connect to the `freshbite_db` database and run the SQL files in numerical order. The CREATE/COPY scripts are intended for an empty demo schema and are not an idempotent migration or reload process.
6. Create and configure QuickSight connectivity, a dataset from `freshbite.vw_sales_dashboard`, and your dashboard manually. No screenshots or dashboard export are bundled.
7. If demonstrating tenant isolation, configure and test RLS before granting access. Filters and drill-down controls alone do not establish a security boundary.

## RLS implementation boundary

`rls_user_permissions` is an ordinary table containing `user_email` and `franchise_id`. It does not enforce access. The SQL comments show an illustrative owner-rule query using `user_email AS UserName`; replace synthetic identities with the actual QuickSight identities used in your environment.

The `ALL` value in the admin fixture is only a project-specific marker. It is not a deployed wildcard permission. The example owner query excludes that marker and therefore does not define admin access.

No native Redshift RLS policies or location-manager rules are implemented. Corporate access, unmatched identities and each franchise's allowed/denied rows need explicit configuration and verification in QuickSight. Apply the chosen protection to every exposed dataset, not only the sales view.

## KPI caveats

The location summary keeps the original demonstration calculations. Its `avg_daily_revenue` alias currently means average revenue per product-day fact row, not total daily location revenue. Its `avg_ticket_size` alias means revenue per unit sold, not average transaction value. There is no transaction/order identifier in the dataset. Do not present these fields as validated business KPIs.

## Cleanup

Remove only the demo objects and resources you intentionally created. The S3 bucket already existed and is not created by this stack. QuickSight resources created manually need separate cleanup. Verify the resulting resource and billing state before considering the evaluation complete.

## License

The existing MIT license is preserved in [LICENSE](LICENSE).
