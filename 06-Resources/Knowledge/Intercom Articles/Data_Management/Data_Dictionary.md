# Data Dictionary

A reference for all dataset types and their required fields. Each dataset type serves a specific role in project configuration and downstream analysis.

## Key concepts

- **Member key** — A non-PII reference key that links records across dataset types (Customer, Transaction, Tender Type). Unique per environment.
- **PII fields** — Fields containing personally identifiable information (e.g. email, phone, name) that must be anonymized before upload.
- **Mapping** — The process of aligning your dataset columns to the platform's expected fields during registration.

## Dataset types

---

### Customer

Contains customer-level information including PII that must be anonymized. One row per customer.

| Field | Sample | Description |
|-------|--------|-------------|
| Member key | HA0034 | Unique reference key per environment (not PII) |
| Date Joined | 2026/04/19 | Date the customer joined the loyalty program |
| Email Address | jj@gmail.com | PII — anonymized during processing |
| Cell phone number | 27813934049 | PII — anonymized during processing |
| First Name | Jacques | PII — anonymized during processing |
| Surname | Journey | PII — anonymized during processing |
| Date of Birth | 1986/03/21 | PII — anonymized during processing |

> Fields marked as PII are hashed by the platform during ingestion. Raw values are never stored or exposed to project users.

---

### Product

Complete product master used to match against transactional data. Data does not need to be at SKU level — for most use cases, category level is sufficient.

| Field | Sample | Description |
|-------|--------|-------------|
| UPC | 4651925605502 | Universal Product Code |
| SKU | 52635347 | Stock Keeping Unit |
| Description | Coca-Cola Light | Product description |
| BMC Code | G258 | BMC classification code |
| BMC | Cans | BMC classification name |
| Category Code | G25 | Product category code |
| Category | Carbonated Soft Drinks | Product category name |
| Department Code | G2 | Department code |
| Department | Dry Groceries | Department name |
| Division Code | G | Division code |
| Division | Groceries | Division name |

---

### Transaction

The core transaction table used to create features for all use cases. Each row represents a single transaction at a point in time.

**Upload requirements:**
- Sales data should be at a daily or weekly level, uploaded weekly
- Initial upload should include **24 to 36 months** of historic data

| Field | Sample | Description |
|-------|--------|-------------|
| Member key | HA0034 | Links to Customer dataset |
| Transaction date | 2022/06/23 | Date of transaction |
| Store code | 25346 | Store identifier |
| EAN / Article / Category Code | 4651925605502 / G25 | Links to Product dataset |
| Sales Amount | 20 | Gross sales value |
| Discount Amount | 5 | Discount applied |
| After discount sales amount | 15 | Net sales value |
| Promotion flags | Y | Whether a promotion was active |

---

### Tender Type

Provides the tender type for each transaction. Used to create features based on formal banking vs. cash usage patterns.

| Field | Sample | Description |
|-------|--------|-------------|
| Member key | HA0034 | Links to Customer dataset |
| Transaction date | 2022/06/23 | Date of transaction |
| Store code | 25346 | Store identifier |
| Tender type | Cash | Payment method (e.g. Cash, Card) |
| After discount sales amount | 10 | Net sales value for this tender |

---

### Product Holding Type

Indicates the types of credit products consumers hold.

**Examples:**
- Credit cards
- Personal loans
- Vehicle finance
- Mortgages

**Purpose:**
Provides insight into:
- Credit exposure
- Financial sophistication
- Credit appetite

---

### Credit Activity

Shows the number or percentage of consumers who applied for credit in the past 6 months.

**Purpose:**
Indicates:
- Credit demand
- Market activity
- Potential emerging risk

Higher application frequency can signal:
- Expansion behaviour
- Or financial stress

---

### Secured vs Unsecured Products

Compares credit products backed by assets vs those without security.

**Secured Products:**
- Mortgage
- Vehicle finance (Asset acts as collateral)

**Unsecured Products:**
- Credit cards
- Personal loans (No linked asset)

**Purpose:**
Provides insight into:
- Risk profile
- Collateral coverage
- Lending mix

---

## Relationships between datasets

```
Customer (Member key)
    ├── Transaction (Member key + Product via EAN/Article/Category Code)
    │       └── Product (UPC / Category Code)
    └── Tender Type (Member key + Transaction date + Store code)
```

## Limitations

- Product data at SKU level is accepted but not required — category level is sufficient for most use cases
- Transaction and Tender Type datasets do not contain PII and do not require anonymization
- Member key format varies by environment

## Related

- [Datasets](https://help.omnisient.com/en/articles/datasets)

---

**Before publishing:**
- [ ] Confirm: are there additional fields for any dataset type not captured here?
- [ ] Confirm: are there other dataset types to document (Dimension, Customer Activation, Other)?
- [ ] Confirm: is "Member key" the correct linking field across all environments, or does this vary?
- [x] Confirm: exact PII hashing behavior — the platform hashes all marked PII fields automatically during ingestion
