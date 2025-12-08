---
marp: true
theme: gaia
class: lead
paginate: true
backgroundColor: #fff
style: |
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  h1 {
    color: #2c3e50;
  }
  /* Customizing the code block look */
  code {
    background: #f0f0f0;
    color: #d63384;
  }
  /* Custom footer alignment */
  footer {
    font-size: 12px;
    color: #7f8c8d;
  }
---

# Backend Architecture v2.0
## Optimization & Scalability Strategy

**Author:** Technical Writing Team
**Contact:** [23f2000898@ds.study.iitm.ac.in](mailto:23f2000898@ds.study.iitm.ac.in)

---

## Algorithmic Complexity Analysis

Our previous search algorithm operated at quadratic time. The new implementation utilizes a **Balanced Binary Search Tree**, optimizing query performance significantly.

**Time Complexity Formula:**

$$
T(n) = O(\log n)
$$

Where $n$ represents the number of active records in the database. This reduces latency by **40%** during peak load.

---

## Database Schema Changes

We have migrated strictly structured data to PostgreSQL while moving ephemeral logs to Redis.

```sql
-- New User Table Structure
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);