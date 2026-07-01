# Phase 0B — Evidence Audit: Module Dependency Graph

`mermaid
graph TD
    audit --> auth
    audit --> companies
    auth --> audit
    auth --> companies
    banking --> auth
    banking --> billing
    banking --> companies
    banking --> masters
    banking --> vouchers
    billing --> audit
    billing --> auth
    billing --> companies
    billing --> masters
    billing --> notifications
    billing --> parties
    billing --> search
    billing --> vouchers
    companies --> audit
    companies --> auth
    companies --> billing
    companies --> inventory
    companies --> masters
    companies --> notifications
    companies --> vouchers
    inventory --> audit
    inventory --> auth
    inventory --> companies
    inventory --> masters
    inventory --> vouchers
    masters --> auth
    masters --> companies
    masters --> search
    notifications --> auth
    notifications --> companies
    parties --> audit
    parties --> auth
    parties --> companies
    parties --> masters
    parties --> search
    reports --> auth
    reports --> companies
    reports --> masters
    reports --> vouchers
    search --> auth
    search --> companies
    vouchers --> audit
    vouchers --> auth
    vouchers --> companies
    vouchers --> masters
    vouchers --> notifications
    vouchers --> search
`