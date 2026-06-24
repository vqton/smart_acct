export enum EinvInvoiceCategory { sales = "sales", adjustment = "adjustment", replacement = "replacement", creditNote = "credit_note", debitNote = "debit_note", cancel = "cancel" }

export enum EinvInvoiceStatus { draft = "draft", pendingApproval = "pending_approval", approved = "approved", signed = "signed", issued = "issued", submitted = "submitted", accepted = "accepted", rejected = "rejected", replaced = "replaced", adjusted = "adjusted", cancelled = "cancelled", archived = "archived", expired = "expired", restored = "restored" }

export enum EinvProviderType { vnpt = "vnpt", viettel = "viettel", misa = "misa", fast = "fast", BKAV = "bkav", HHD = "hhd", other = "other" }

export enum EinvTransmissionStatus { pending = "pending", sending = "sending", sent = "sent", acknowledged = "acknowledged", failed = "failed", retrying = "retrying" }

export enum EinvSignatureMethod { rsaSha256 = "rsa_sha256", ecdsaSha256 = "ecdsa_sha256", dsaSha256 = "dsa_sha256" }

export enum EinvDigestAlgorithm { sha256 = "sha_256", sha512 = "sha_512" }

export enum EinvDeliveryMethod { email = "email", sms = "sms", portal = "portal", api = "api" }

export enum EinvAdjustmentType { replacement = "replacement", adjustment = "adjustment", cancellation = "cancellation" }

export enum EinvArchiveStatus { active = "active", archived = "archived", destroyed = "destroyed" }

export enum EinvCertStatus { active = "active", expired = "expired", revoked = "revoked", suspended = "suspended" }
