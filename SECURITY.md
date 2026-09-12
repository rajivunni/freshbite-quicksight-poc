# Security and synthetic-data boundary

This is a BI starter using synthetic records, not a production multi-tenant application.

## Current limits

- The workgroup template sets `PubliclyAccessible: true` and does not define explicit subnets or security groups. Review the resulting network access before deployment.
- QuickSight and Redshift RLS enforcement is not implemented by the checked-in source. A permissions table and dashboard filters do not isolate tenants.
- The `ALL` fixture value is a project-specific marker, not an automatically recognized access rule.
- The QuickSight IAM role includes wildcard resource permissions. Review actual required actions and scope before use.
- The S3 access role can read across the supplied bucket, not only the demo prefix. Use a dedicated demo bucket and review the permission scope.
- Database passwords are accepted through a `NoEcho` CloudFormation parameter. Do not commit them or put them in copied command examples.
- Redshift connection and activity log exports are enabled. Review access, contents and retention before any non-synthetic evaluation.

## Safe use

Use synthetic data and a separate demo environment. Do not replace the public fixtures with client records, real email addresses or private reports. Keep credentials, environment files, state files and local configuration out of Git.

Before sharing a dashboard with users, configure the intended access controls and test both allowed and denied access for every exposed dataset. Offline data tests do not verify authorization.

## Reporting

Open an issue only with sanitized source-level details. Do not post credentials, private reports, database endpoints or client data. Revoke any exposed credential through its issuing service before discussing the exposure publicly.
