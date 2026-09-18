# Omnisient Tech Stack

Reference for Ada when discussing technical feasibility, constraints, and options.

## Data Platform

### Azure Synapse Analytics (Dedicated SQL Pool)

- **What it is:** Enterprise data warehouse with dedicated compute resources
- **How Omnisient uses it:** Primary analytical data store for data products
- **Key characteristics:**
  - MPP (Massively Parallel Processing) architecture
  - Dedicated compute — always-on, billed by DWU (Data Warehouse Units)
  - Best for: Complex analytical queries, large dataset joins, aggregations
  - Limitations: Not ideal for high-concurrency OLTP workloads, costs scale with compute tier
- **Cost consideration:** DWU costs are significant — always consider whether a query pattern justifies dedicated compute vs. serverless alternatives

### Azure Data Pipelines (Azure Data Factory)

- **What it is:** Cloud ETL/ELT orchestration service
- **How Omnisient uses it:** Data ingestion, transformation, and movement between systems
- **Key characteristics:**
  - Visual pipeline designer with code-behind option
  - Supports 100+ data connectors
  - Trigger-based (schedule, event, tumbling window)
  - Integration Runtimes for on-prem/cloud connectivity
- **Cost consideration:** Billed per activity run and data movement — pipeline complexity directly impacts cost

### SQL Stored Procedures

- **What it is:** Pre-compiled SQL logic stored in the database
- **How Omnisient uses it:** Core business logic, data transformations, calculations
- **Key characteristics:**
  - Significant existing investment — many critical processes are SP-based
  - Tightly coupled to Synapse Dedicated SQL Pool
  - Can be difficult to version control and test
  - Performance depends on query optimization and distribution strategy
- **Legacy consideration:** Stored procedures represent accumulated business logic. Replacing them is expensive and risky — always prefer extending over rewriting unless there's a clear architectural mandate.

## Visualization & Analytics

### PowerBI

- **What it is:** Microsoft business intelligence and reporting platform
- **How Omnisient uses it:** Client-facing dashboards, internal analytics, data product visualization
- **Key characteristics:**
  - DirectQuery and Import modes (tradeoff: real-time vs. performance)
  - Row-Level Security for multi-tenant access
  - Embedded analytics capability for product integration
  - DAX for calculated measures
- **Cost consideration:** Pro vs. Premium licensing affects embedding, dataset size, and refresh rates

## Front End

- **Status:** TBC — front-end technology stack is being defined
- **Current state:** Web platform exists but specific technologies not yet documented
- **Implication:** Front-end technical options are more open than back-end

## Data Collaboration Platform

- **Privacy-preserving architecture:** Core differentiator — all data products must maintain privacy guarantees
- **Cleanroom capabilities:** Secure computation environments for multi-party data analysis
- **Scale:** 160M+ consumer profiles protected across 80+ enterprise clients

## Integration Points

- **Data sellers → Synapse:** Ingestion pipelines bring seller data into the platform
- **Synapse → PowerBI:** Analytics and visualization layer
- **Synapse → Cleanrooms:** Privacy-preserving computation
- **Cleanrooms → Data buyers:** Insights delivered without exposing raw data

## When Discussing Technical Options

Always consider:

1. **Does it work with Synapse Dedicated SQL Pool?** Most data processing routes through here
2. **Can existing pipelines handle it?** New pipeline patterns add complexity
3. **Does it require new tooling?** Tool sprawl is a concern — justify any new tool
4. **What's the SP migration cost?** If touching stored procedures, estimate the blast radius
5. **PowerBI compatibility?** Client-facing analytics must work within PowerBI's constraints
