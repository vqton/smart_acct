-- Legacy domain DDL
-- Simple accounts (legacy, replaced by GL Chart of Accounts in production)
CREATE TABLE IF NOT EXISTS legacy_accounts (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type ENUM('asset','liability','equity','revenue','expense') NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Legacy transactions (simple double-entry, replaced by GL JournalBatch in production)
CREATE TABLE IF NOT EXISTS legacy_transactions (
  id VARCHAR(36) PRIMARY KEY,
  debit_account_id VARCHAR(36) NOT NULL,
  credit_account_id VARCHAR(36) NOT NULL,
  amount BIGINT NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',
  description TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_legacy_tx_debit (debit_account_id),
  KEY idx_legacy_tx_credit (credit_account_id),
  CONSTRAINT fk_legacy_tx_debit FOREIGN KEY (debit_account_id) REFERENCES legacy_accounts(id),
  CONSTRAINT fk_legacy_tx_credit FOREIGN KEY (credit_account_id) REFERENCES legacy_accounts(id)
);
