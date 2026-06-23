# GL Module REST API Endpoints

## Base URL: `/api/gl`

### Accounts
| Method | Path | Description |
|--------|------|-------------|
| POST | `/accounts` | Create account |
| GET | `/accounts` | List all accounts |
| GET | `/accounts/active` | List active accounts |
| GET | `/accounts/tree` | Get hierarchy tree |
| GET | `/accounts/:id` | Get account by ID |
| PATCH | `/accounts/:id` | Update account |
| DELETE | `/accounts/:id` | Deactivate account |
| POST | `/accounts/import` | Bulk import accounts |

### Journals
| Method | Path | Description |
|--------|------|-------------|
| POST | `/journals` | Create journal batch |
| GET | `/journals` | Search journals |
| GET | `/journals/:id` | Get journal detail |
| DELETE | `/journals/:id` | Delete draft journal |
| POST | `/journals/:id/submit` | Submit for approval |
| POST | `/journals/:id/approve` | Approve journal |
| POST | `/journals/:id/post` | Post journal |
| POST | `/journals/:id/reverse` | Reverse posted journal |
| POST | `/journals/validate` | Validate batch |
| POST | `/journals/batch-post` | Post multiple batches |

### Periods
| Method | Path | Description |
|--------|------|-------------|
| POST | `/periods/fiscal-years` | Create fiscal year |
| GET | `/periods/fiscal-years` | List fiscal years |
| GET | `/periods/fiscal-years/active` | Get active FY |
| GET | `/periods/fiscal-years/:id` | Get FY details |
| POST | `/periods/fiscal-years/:id/close` | Close FY |
| GET | `/periods/fiscal-years/:id/periods` | List periods |
| POST | `/periods/periods/:id/close` | Close period |
| POST | `/periods/periods/:id/reopen` | Reopen period |
| POST | `/periods/periods/:id/lock` | Lock period |

## Headers
- `X-User-Id`: User ID for audit trail (required for mutations)

## Standard Error Responses
- `400`: Validation error
- `404`: Resource not found
- `409`: Conflict (duplicate)
- `500`: Internal error
