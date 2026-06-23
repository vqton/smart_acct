# Slice 1: Core FixedAsset CRUD

## What to build

Domain entity `FixedAsset` with original cost, classification, and type, plus create/list/get endpoints. Write-through all layers: domain → repository interface → application service → in-memory repo → Express router.

## UCs covered

- UC-01: Recognize Fixed Asset (3 criteria check)
- UC-02: Determine Original Cost (cost aggregation per acquisition method)
- UC-03: Classify by Purpose (business/welfare/security)

## Acceptance criteria

- [ ] `FixedAsset` entity with id, name, type (tangible/intangible/lease), original cost, acquisition date, purpose, depreciation method, useful life
- [ ] Original cost validated (≥ 30,000,000 VND)
- [ ] 3 recognition criteria (future economic benefit, useful life > 1 year, cost ≥ threshold)
- [ ] Classification by purpose: business / welfare / security
- [ ] `FixedAssetRepository` interface (save, findById, findAll)
- [ ] `InMemoryFixedAssetRepository` implementation
- [ ] `FixedAssetService.create` / `.get` / `.list`
- [ ] POST /fixed-assets, GET /fixed-assets/:id, GET /fixed-assets
- [ ] Tests: unit tests for entity + service, integration for routes

## Blocked by

None — can start immediately
