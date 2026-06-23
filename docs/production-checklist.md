# GL Module Production Checklist

## 1. Database
- [x] SQL DDL generated (`src/infrastructure/gl/schema.sql`)
- [x] Prisma schema generated (`prisma/schema.prisma`)
- [ ] Run migration in staging environment
- [ ] Set up partitioning for `journal_entry_lines` (yearly by posting_date)
- [ ] Create read replicas for reporting queries
- [ ] Configure connection pool limits
- [ ] Set up automated backups

## 2. Authentication & Authorization
- [ ] Implement RBAC (roles: accountant, chief_accountant, auditor, admin)
- [ ] Implement ABAC for field-level security
- [ ] Add X-User-Id middleware for audit trail
- [ ] Add permission checks on all endpoints

## 3. Audit Trail
- [x] `AuditLog` table in schema
- [ ] Implement audit log middleware to capture all mutations
- [ ] Make audit logs immutable (append-only)
- [ ] Implement tamper detection (hash chain)

## 4. Validation Rules
- [x] Debit = Credit validation (domain level)
- [x] Period closed/locked validation
- [x] Fiscal year closed validation
- [x] Inactive account posting prevention
- [x] Control account posting prevention
- [ ] Add duplicate detection (same voucher number in period)
- [ ] Add cross-company validation for intercompany

## 5. Error Handling
- [x] DomainError with kind categorization
- [ ] Global Express error handler middleware
- [ ] Log errors with correlation IDs
- [ ] Define error response format consistently

## 6. Performance
- [x] Index strategy in DDL
- [x] Database partitioning plan
- [ ] Load test with 1M journal entries
- [ ] Query optimization for trial balance reports
- [ ] Caching for chart of accounts (frequently read, rarely written)

## 7. Security
- [x] Soft delete on accounts
- [ ] Encrypt sensitive fields at rest
- [ ] Rate limiting on API endpoints
- [ ] Input sanitization and validation
- [ ] CORS configuration for production

## 8. Monitoring
- [ ] Set up health check endpoint (`GET /health`)
- [ ] Metrics for posting latency
- [ ] Alert on posting failures
- [ ] Dashboard for period close progress

## 9. Deployment
- [ ] Environment-specific config via env vars
- [ ] CI/CD pipeline for DB migrations
- [ ] Zero-downtime migration strategy
- [ ] Blue/green deployment for schema changes

## 10. Compliance
- [x] Circular 99/2025/TT-BTC compliance
- [x] Accounting Law 88/2015/QH13 compliance
- [ ] Tax authority reporting formats
- [ ] Document retention policy (5 years per Art. 13)
- [ ] Digital signature for vouchers (Law on Electronic Transactions)
