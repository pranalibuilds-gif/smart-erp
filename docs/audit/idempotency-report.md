# Phase 4 Idempotency Report

**Status**: PASS
**Date**: 2026-06-27

## 1. Idempotency Behavior
Verified that critical transactional endpoints behave predictably when called multiple times (e.g., due to network retries).

## 2. Tested Endpoints

### A. Voucher Posting
- **Behavior**: Second call to `/vouchers/{id}/post` returns `400 Bad Request` with message "Voucher is already posted".
- **Safety**: Prevents duplicate balance updates if the user double-clicks or the UI retries.

### B. Financial Year Closing
- **Behavior**: Second call to `/financial-years/{id}/close` returns `400 Bad Request` with message "FY is already closed".
- **Safety**: Prevents creating multiple rollover years.

### C. Invoice Creation
- **Behavior**: **Non-idempotent by design**. Identical payloads result in new invoices with unique numbers.
- **Verification**: UI is responsible for disabling the submit button; backend allows multiple identical documents if intended.
