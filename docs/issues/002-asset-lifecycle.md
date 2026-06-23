# Slice 2: Asset Lifecycle

## What to build

Depreciation calculation, schedule generation, repair/upgrade handling, disposal (liquidate/sell/revaluate), and depreciation method registration.

## UCs covered

- UC-04: Calculate Depreciation
- UC-05: Register Depreciation Method
- UC-09: Record Repair Cost
- UC-10: Record Upgrade Cost
- UC-12: Dispose / Liquidate Fixed Asset
- UC-13: Sell / Transfer Fixed Asset
- UC-14: Revaluate Fixed Asset
- UC-15: Generate Depreciation Schedule

## Acceptance criteria

- [ ] Depreciation calculation (straight-line / declining balance / units of production)
- [ ] Depreciation method registration per asset
- [ ] POST /fixed-assets/:id/depreciate — calculate and record period depreciation
- [ ] GET /fixed-assets/:id/depreciation-schedule
- [ ] POST /fixed-assets/:id/repairs — record repair cost (expensed, not capitalized)
- [ ] POST /fixed-assets/:id/upgrades — record upgrade cost (capitalized, increases original cost)
- [ ] POST /fixed-assets/:id/liquidate — write off asset, record gain/loss
- [ ] POST /fixed-assets/:id/sell — record sale, remove asset, record gain/loss
- [ ] POST /fixed-assets/:id/revaluate — adjust carrying value
- [ ] Tests: domain logic, service, route integration

## Blocked by

- docs/issues/001-core-fixed-asset-crud.md
