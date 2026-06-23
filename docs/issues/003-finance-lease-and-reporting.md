# Slice 3: Finance Lease + Reporting

## What to build

Finance lease asset recognition, installment payments, end-of-lease transfer, inventory, handover documentation, and fixed asset reporting.

## UCs covered

- UC-06: Record Finance Lease Asset
- UC-07: Pay Finance Lease Installment
- UC-08: Transfer Ownership at Lease End
- UC-11: Conduct Fixed Asset Inventory
- UC-16: Record Fixed Asset Transfer
- UC-17: Generate Fixed Asset Reports

## Acceptance criteria

- [ ] Finance lease recognition (meets ≥1 of 3 conditions)
- [ ] Lease liability tracking with principal/interest split
- [ ] POST /finance-leases, GET /finance-leases/:id
- [ ] POST /finance-leases/:id/payments
- [ ] POST /finance-leases/:id/transfer-ownership
- [ ] POST /fixed-assets/inventory — record inventory results (surplus/deficit)
- [ ] POST /fixed-assets/:id/handover — record handover between departments
- [ ] GET /fixed-assets/reports — aggregate report (original cost, accumulated depreciation, net book value by group)
- [ ] Tests: domain logic, service, route integration

## Blocked by

- docs/issues/001-core-fixed-asset-crud.md
