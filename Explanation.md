# Explanation

## Approach

I built a stock management system using Django REST Framework to handle stock transfers between branches. The system includes creating transfer requests, approving them, and viewing stock summaries.

---

## Transactions

I used `transaction.atomic()` to ensure data consistency.  
During transfer approval:
- Stock is deducted from the source branch
- Stock is added to the destination branch
Both actions happen in a single transaction to avoid partial updates.

---

## Concurrency

To avoid stock issues:
- I used `reserved_quantity` when creating a transfer request
- This ensures stock is blocked before approval
This prevents multiple users from using the same stock at the same time.

---

## Query Optimization

- Used `select_related()` to reduce database queries
- Applied filters at the database level (status, branch, product)
- Avoided unnecessary loops and queries

---

## Role-Based Access

- Admin and Manager can approve transfers
- Staff can only create transfer requests

Permissions are handled using custom DRF permission classes.

---

## Unfinished Work

- Pagination can be improved
- Audit logs for tracking changes can be added
- Test cases can be added