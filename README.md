---
marp: true
theme: gaia
paginate: true
backgroundColor: #fff
footer: '© 2025 TechWriter Solutions | Confidential'
style: |
  section {
    font-family: 'Helvetica Neue', sans-serif;
  }
  h1 {
    color: #0066cc;
  }
  code {
    background-color: #f0f0f0;
    padding: 2px 5px;
    border-radius: 4px;
  }
---

# Product API Documentation v2.0
## Microservices Architecture & Scalability

**Maintained by:** Technical Documentation Team
**Contact:** [23f2000898@ds.study.iitm.ac.in](mailto:23f2000898@ds.study.iitm.ac.in)

---

## Introduction

We have migrated our monolithic backend to a **distributed microservices** architecture. This transition allows for:

* **Independent Deployment:** Services can be updated without downtime.
* **Polyglot Persistence:** Utilizing different databases for different needs.
* **Resilience:** Fault isolation prevents cascading failures.

> "Documentation is a love letter that you write to your future self."

---

![bg left:40%](https://images.unsplash.com/photo-1558494949-ef526b0042a0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

## Visual Architecture

The image to the left represents our new **Cloud Mesh Network**.

### Key Components:
1. **API Gateway:** Entry point for all clients.
2. **Auth Service:** OAuth2 implementation.
3. **Data Lake:** Long-term storage for analytics.

---

## Algorithmic Complexity

To ensure high throughput, we optimized the routing algorithm. The computational complexity for request distribution is now defined as:

$$
T(n) = \sum_{i=1}^{k} \left( n \log n + \frac{1}{i} \right)
$$

Where:
* $n$ is the number of active nodes.
* $k$ is the number of concurrent requests.

---

## Deployment Strategy

We utilize a **Blue-Green** deployment strategy to minimize risk.

```yaml
version: '3.8'
services:
  web:
    image: product-api:latest
    deploy:
      replicas: 5
      update_config:
        parallelism: 2