# Column vs Row vs HTAP for Finance Workloads (Sep 2025)

## Executive Summary

- Analytics (OLAP) workloads in finance with large scans and aggregations (tick analytics, risk aggregation, reporting, fraud exploration) overwhelmingly favor columnar storage for compression and scan throughput (e.g., kdb+, ClickHouse, Vertica, Snowflake, BigQuery, Redshift, Druid). Column stores win when queries select few columns over billions of rows, support vectorization, and compress well [kdb+ overview][1][2][3], [ClickHouse][4], [Vertica][13][18], [Snowflake][19], [BigQuery][24], [Redshift][29][30], [Druid][41][42][63].
- OLTP (payments/ledgering, core banking, booking) stays predominantly row‑store, ACID relational, with predictable millisecond latency and strong transactional semantics (PostgreSQL, Oracle, SQL Server). Distributed SQL (CockroachDB, YugabyteDB, TiDB) is chosen for geo‑distribution and horizontal scale with ACID [PostgreSQL][37], [Oracle][71], [SQL Server][73], [CockroachDB][92][93], [YugabyteDB][95][96], [TiDB][88][89][90].
- HTAP choices:
  - “Column-first HTAP” (SAP HANA, SingleStore, TiDB+TiFlash) blend columnar analytics with row/transactional capabilities, enabling operational analytics and near‑real‑time risk views on the same system [HANA][79][80], [SingleStore][83][84], [TiDB/TiFlash][88][89].
  - “Hybrid architecture HTAP” is more common in practice: OLTP in a row‑store or distributed SQL, with CDC/streaming into a columnar analytics engine or lakehouse; sometimes supplemented with a real‑time analytics store (Druid/ClickHouse) for investigative dashboards [Druid][65][41], [ClickHouse][6][9], [Databricks Delta][57][59].
- Evidence and benchmarks: For tick/time‑series analytics, STAC‑M3 is the gold standard—kdb+ dominates published audited results [5][46][45]. For warehouses/lakehouses, vendors and third parties cite TPC‑DS/TPC‑H comparisons; treat non‑TPC‑hosted reports as vendor/3rd‑party studies [TPC‑DS][43], [Databricks TPC‑DS historical][58], [GigaOm studies][21][25].

## How Finance Teams Decide: Column vs Row vs HTAP

- Choose columnar OLAP when:
  - You scan/aggregate many rows and few columns; need high compression and vectorized execution. Typical: tick analytics, risk aggregation, fraud exploration, portfolio analytics, regulatory reporting [1][4][13][18][19][24][29][41].
  - You can tolerate seconds/sub‑second responses for heavy queries; ACID across long transactions is not primary.
- Choose row‑oriented OLTP when:
  - You require low‑latency point reads/writes, high write contention, and strict ACID/serializable isolation. Typical: payments authorization, ledger postings, core banking accounts, booking/trade capture [37][71][73].
- Choose HTAP when:
  - You need up‑to‑date analytics on operational data without heavy ETL, and a single engine can meet both SLA sets; or you embrace a streaming/CDC pattern to maintain derived columnar stores. Typical: real‑time risk/limits, fraud scoring/monitoring on fresh transactions, operational dashboards [79][83][88][57][65].

Rules of thumb:
- Time‑series tick storage and as‑of joins → kdb+ (audited STAC‑M3 leadership) or ClickHouse for cost‑efficient OLAP; TimescaleDB if you need full Postgres SQL/ACID with time‑series features [5][4][6][9][36][38].
- Near‑real‑time investigative analytics at high concurrency over streams → Apache Druid or ClickHouse with Kafka [65][41][6][9].
- Enterprise cloud BI/reporting and cross‑firm data sharing → Snowflake, BigQuery, Redshift, or a Lakehouse (Databricks) [19][24][29][57].
- Core OLTP ledgers/payments → PostgreSQL/Oracle/SQL Server or Distributed SQL (CockroachDB/YugabyteDB/TiDB) for global scale and resiliency [37][71][73][92][95][88].
- Unified platform for operational analytics (HTAP) → SAP HANA, SingleStore, TiDB+TiFlash; or use CDC/streams to lakehouse/warehouse [79][83][88][57].

## Prevailing Practices by Workload

- Trading/tick analytics and backtesting: kdb+ is entrenched in Tier‑1/2 banks for sub‑ms on recent data and fast multi‑year scans; ClickHouse widely used for real‑time analytics and cost efficiency; Druid for high‑concurrency dashboards; warehouses/lakehouses or Vertica for batch/backtesting and integration with ML [5][6][4][6][41][13][58][19][24][29][57].
- Risk aggregation/portfolio analytics: Cloud warehouses (Snowflake, BigQuery, Redshift) or Lakehouse (Databricks) for elasticity/governance; Vertica on‑prem/hybrid for ANSI SQL and compression; kdb+ for intraday risk if tick/time windows matter [19][24][29][57][13][5].
- Fraud detection/AML: Druid and ClickHouse for real‑time exploratory dashboards; warehouse/lakehouse for feature stores and offline training; streaming pipelines (Kafka/Kinesis) feeding both [65][41][6][9][24][57][29].
- Payments/ledgering/core banking OLTP: Oracle/SQL Server/PostgreSQL in traditional deployments; Distributed SQL (CockroachDB, YugabyteDB, TiDB) for multi‑region availability, linear scale, and strong consistency. HTAP layering via CDC to analytics systems is common [71][73][37][92][95][88][89].
- Hybrid architectures: Common Lambda/Kappa patterns—OLTP emits CDC to Kafka; real‑time analytics in Druid/ClickHouse; durable analytics in Snowflake/BigQuery/Redshift/Databricks; optional HTAP engines for specific operational analytics [65][6][57][19][24][29].

## Comparison Table

Note: “Performance Evidence” cites audited benchmarks where available. Non‑audited/vendor studies are labeled accordingly.

| Category | System/Service | Vendor | Data Model | Storage Orientation | Deployment Model | Typical Finance Use Cases | Decision Rationale | Performance Evidence | Consistency/Transactions | Query/Index Features | Scalability/Partitioning | Latency/Throughput | Compression/Storage Efficiency | Cost/TCO Notes | Operational Complexity | Security/Compliance | HTAP Architecture Notes | Notable Trade-offs | Real-World Case Study | Benchmark Type | Source URL(s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Analytics (OLAP, time‑series) | kdb+ | KX | Relational time‑series (q) | Columnar (in‑mem + mmap) | On‑prem, private cloud, KX Cloud | Tick storage/analytics, backtesting, options analytics, risk | Extreme time‑series performance, as‑of joins, vectorization | Multiple audited STAC‑M3 records; e.g., KDB231122: 8× Dell R740xd, 266 TiB, Antuco/Kanaga suites [STAC] | Append‑heavy; durability/logging; not general multi‑table OLTP ACID | q language; as‑of join; time partitioning; splayed tables | Shard by time/symbol; shared‑nothing | Sub‑ms in‑mem; high scan rates over years | Columnar codecs; mmap of historical | Proprietary; HW profile cost driven by NVMe/PMem | Specialist skills (q) | Enterprise deployments; KX Surveillance | Real‑time ingest + historical analytics in one | Proprietary; niche skillset; less SQL ecosystem | Many Tier‑1 banks; numerous audited STAC stacks | STAC‑M3 (audited) | [kdb+ product][3]; [STAC‑M3][5]; [KDB231122][45] |
| Analytics (OLAP) | ClickHouse | ClickHouse Inc. | Relational OLAP | Columnar | Self‑managed; ClickHouse Cloud | Real‑time analytics (payments, fraud dashboards), trade telemetry | High scan throughput, compression, MVs, cost efficiency | Vendor/community comparisons; no public audited STAC/TPC | Single‑statement ACID; experimental multi‑stmt TX not in Cloud | SQL; sparse primary index; data‑skipping indexes; projections; MVs | Shard/replicate; Kafka engine; MVs | Sub‑second aggregates over billions with proper sort | LZ4/ZSTD; delta/Gorilla codecs | Open source + managed; strong price/perf | Design of projections/MVs needed | RBAC; enterprise features in Cloud | Streaming ingest with Kafka + MVs; separation storage/compute in Cloud | Not full ACID for OLTP; complex joins need design | Juspay payments analytics (>50M tx/day) | Vendor/community | [MergeTree][4]; [MVs][9]; [Kafka engine][47]; [Juspay][6] |
| Analytics (OLAP) | Vertica | OpenText | Relational MPP | Columnar | On‑prem; cloud VMs; Eon (S3‑style) | Risk analytics, fraud/security, BI | Mature ANSI SQL, compression, time‑series SQL | Customer stories; limited recent audited public benchmarks | ACID; MVCC; READ COMMITTED default; SERIALIZABLE supported | Projections instead of sec. indexes; TIMESERIES functions | Shared‑nothing MPP; segmentation; K‑safety; Eon decoupling | Low‑latency analytics with tuned projections | Multiple encodings; operates on encoded data | Commercial; hybrid flexibility | Projection design expertise required | Enterprise auditing/security | Batch/micro‑batch; external tables; not streaming DB | Physical design overhead; fewer modern audited benchmarks | QNB Finansbank fraud/security analytics | Case study | [Projections][13]; [Time‑series][14][15]; [Eon][50] |
| Analytics (Cloud DW) | Snowflake | Snowflake Inc. | Relational | Columnar (micro‑partitions) | Fully managed SaaS | Regulatory/reporting, risk analytics, quant ML prep, data sharing | Elastic compute, governance/sharing, low ops | GigaOm TPC‑DS‑derived studies (not official TPC) | Transactions; READ COMMITTED only | SQL; clustering keys; MVs; UDF/UDAF; Snowpark | Elastic multi‑cluster; separation storage/compute | Seconds→minutes for big joins; sub‑second with cache | Columnar on object storage | Consumption pricing; governance needed | Very low ops | Encryption, RBAC, auditing; FS Data Cloud | Streams/Tasks, Snowpipe for near‑real‑time | Compute‑bound costs on heavy scans without pruning | S&P Global ML pipelines for credit risk | Vendor/3rd‑party | [Micro‑partitions][19]; [FS Data Cloud][20]; [GigaOm][21] |
| Analytics (Cloud DW) | BigQuery | Google Cloud | Relational | Columnar | Fully managed serverless | Large‑scale reporting, risk/fraud analytics, geospatial/time‑series ML | Serverless ops, built‑in ML, federated querying | GigaOm TPC‑DS/H studies (not official TPC) | Multi‑stmt ACID; snapshot isolation | GoogleSQL; partition/cluster; MVs; BI Engine; geospatial+raster | Serverless scale‑out via slots | Seconds/sub‑second with BI Engine/cache | Columnar on Colossus; long‑term storage | Per‑TB scan or slots; low ops | Minimal ops; IAM governance | Encryption, audit logs, regional control | Streaming inserts; CDC via Dataflow; near real‑time | Cost control needed; not low‑ms OLTP | ATB Financial: 117× faster insights | Vendor/3rd‑party | [Transactions][24]; [MVs][54]; [BI Engine][55]; [ATB][27] |
| Analytics (Cloud DW) | Amazon Redshift (incl. Serverless) | AWS | Relational | Columnar | Managed on AWS | FS reporting/regulatory, data lakehouse with Spectrum, fraud | Tight AWS integration; AQUA; Spectrum | GigaOm studies; case studies with concrete metrics | Snapshot Isolation default (2024); Serializable | Sort/dist keys; MVs; Spectrum external tables; H3 functions | Scale by nodes/serverless units; concurrency scaling | Seconds to sub‑second for short queries; high S3 throughput | Columnar encodings; AQUA accelerates | Pay‑per‑second (Serverless) or node‑hours | Managed, but sort/dist design still matters | KMS, audit, VPC; Lake Formation | Near‑real‑time via MVs; Kinesis/MSK ingest | Design choices affect perf; cross‑region sharing | PayU: 200 TB/day scanned, <1 min queries, ~$20k/mo savings (2025). Nasdaq: 40→4 min process | Vendor/3rd‑party | [Snapshot Isolation][29]; [Spectrum][56]; [H3][30]; [PayU][31] |
| Analytics (Lakehouse SQL) | Databricks SQL Warehouse | Databricks | Relational over Delta Lake | Columnar (Parquet) | Managed on AWS/Azure/GCP | Risk/VAR, backtesting, fraud, regulatory reporting | Unified data+AI, streaming ETL, governance (Unity Catalog) | Official TPC‑DS historical 100TB result (QphDS 32,941,245) | Delta ACID with optimistic concurrency; serializable option | SQL; materialized views; Z‑order; Photon vectorized engine | Scale‑out clusters/serverless; batch+stream | Seconds/sub‑second at scale depending on cluster | Parquet + Delta log; caching layers | Pay‑per‑compute; cheap lake storage | Managed; requires data layout tuning (Z‑order) | Unity Catalog RBAC, lineage, auditing | Streaming ingest (Auto Loader) + near‑real‑time materializations | No multi‑table TX; not for low‑ms point lookups | Coastal Community Bank: BaaS analytics | Official TPC‑DS (historical) | [Delta/ACID][57]; [TPC‑DS historical][58]; [Streaming][59] |
| Time‑series (SQL) | TimescaleDB | Timescale | Relational (PostgreSQL) | Row for hot; compressed columnstore for cold | Self‑hosted PG + extension; Timescale Cloud | Market metrics, historical pricing/PNL, mixed OLTP+TS | Full Postgres SQL/ACID; continuous aggregates; compression policies | TSBS/community tests; no audited STAC/TPC | Full PG ACID; READ COMMITTED/REPEATABLE READ/SERIALIZABLE | PG SQL + time_bucket, continuous aggregates; joins | Hypertables; distributed hypertables (deprecated path noted); retention/compression policies | Good ingest; ms‑level queries on aggregates | Columnstore compression for older chunks | Uses PG skills; cloud managed available | Familiar PG ops; manage policies | Timescale Cloud SOC2/HIPAA/GDPR posture | CDC into aggregates gives HTAP‑like behavior | Not a pure column OLAP on wide scans | Various fintechs; (examples on vendor site) | Community/vendor | [Continuous aggregates][36]; [Compression policy][38]; [PG isolation][37]; [Security][39] |
| Real‑time analytics | Apache Druid / Imply | ASF / Imply | Columnar analytics + inverted indexes | Columnar segments with rollup | Self‑managed; Imply SaaS | AML/fraud dashboards, surveillance, high‑QPS slicing | Sub‑second aggregations at high concurrency; streaming exactly‑once | Case studies (DBS Bank AML); no audited TPC/STAC | Append‑optimized; exactly‑once streaming ingestion | SQL; bitmap/inverted indexes; sketches; rollup | Time and secondary partitioning; historical/real‑time nodes | Sub‑second with rollup; 10–100× storage reduction possible | Columnar + Roaring bitmaps; dictionary encoding | Efficient for high‑QPS analytics apps | Ingestion supervisors/compaction tuning | TLS, auth, RBAC | Streaming HTAP pattern; ingest materialization | Rollup may lose per‑event detail; not general DW | DBS Bank AML investigations (Imply) | Case study | [Design/segments][63]; [Ingestion][41][65]; [DBS AML][66] |
| OLTP (row‑relational) | PostgreSQL | PostgreSQL Global Dev. Group | Relational | Row | Self‑managed; many managed PG services | Payments, ledgers, booking, risk calc stores | Mature ACID, strong SQL/joins, extensions | TPC‑C exists on tpc.org (various vendors) | ACID; READ COMMITTED/REPEATABLE READ/SERIALIZABLE | Full SQL; rich indexes; MV, FDW, extensions | Vertical scale; partitioning; logical sharding | ms‑level transactions; tuning dependent | TOAST/compression; extensions | Open source; broad tooling; ops responsibility | Requires HA/failover design | Extensible security; audit extensions | CDC to analytics; FDW federation | Single‑node write scaling; manual sharding | Used widely in fintech/banks (various) | TPC‑C (official page) | [PG isolation][37]; [TPC‑C results page][97] |
| OLTP (row‑relational) | Oracle Database | Oracle | Relational | Row (plus columnar in options) | On‑prem; Exadata; cloud | Core banking, payments, ledgering | Proven OLTP, partitioning, RAC/Exadata | TPC‑C results exist (see TPC) | ACID; isolation per Oracle (read consistency) | SQL; advanced indexing; MVs; partitions | Scale‑up; RAC for scale‑out; sharding | Low‑ms OLTP; engineered systems | Advanced compression | License + infra; engineered systems TCO | Complex but mature tooling | TDE, auditing; industry solutions | CDC/GoldenGate to analytics | License cost; vendor lock‑in | Widely used in banking (see FS page) | TPC‑C (official page) | [Oracle transactions][71]; [Oracle FS][72]; [TPC‑C][97] |
| OLTP (row‑relational) | Microsoft SQL Server | Microsoft | Relational | Row (with columnstore index for analytics) | On‑prem; Azure SQL | Core banking apps, payments, reporting | In‑Memory OLTP; mature tooling | TPC‑C results exist (see TPC) | ACID; multiple isolation levels incl. Snapshot | T‑SQL; columnstore indexes; MVs; in‑memory tables | Scale‑up; Always On; sharding patterns | ms‑level OLTP; columnstore for mixed workloads | Row + columnstore index compression | License/subscription; Windows/Linux | Mature admin ecosystem | Encryption, auditing, RBAC | Hybrid with columnstore and replicas for analytics | Scale‑out requires patterns | Used widely across enterprises | TPC‑C (official page) | [Isolation levels][73]; [In‑Memory OLTP][74]; [TPC‑C][97] |
| NoSQL (wide‑column) | Apache Cassandra | ASF | Wide‑column (KV with tables) | Row‑oriented SSTables | Self‑managed; managed (DataStax) | High‑scale payments events, session/ledger adjuncts | High write throughput; tunable consistency; availability | Vendor/community; no official TPC | Tunable consistency; eventual→strong per CL | CQL; no joins; sec. indexes limited | Consistent hashing; multi‑DC replication | Low‑lat write; predictable | LZ4; leveled compaction | Hardware‑efficient at scale | Ops complexity (repair, compaction) | TLS; role‑based | Use CDC/streams to OLAP | Not relational joins/transactions | MobilePay (payments) | Case study | [Arch overview][75]; [Consistency][76]; [MobilePay][98] |
| NoSQL (document) | MongoDB | MongoDB Inc. | Document (BSON) | Row‑like documents | Self‑managed; Atlas | Customer 360, fraud features, time‑series events | Flexible schema; ACID multi‑doc TX; time‑series collections | Vendor materials; no official TPC | Multi‑document ACID; snapshot isolation | Rich indexes; aggregations; time‑series collections | Sharding with hashed/ranged keys | ms‑level ops; depends on doc size | WiredTiger compression | Atlas consumption pricing | Index/modeling best practices required | Encryption, auditing; FS industry page | Streams/CDC to OLAP; time‑series ops | Not a columnar analytics warehouse | Many FS customers (industry page) | Case studies (various) | [Transactions][77]; [Time‑series][78]; [FS industry][99] |
| HTAP (in‑memory columnar) | SAP HANA | SAP | Relational (row + column stores) | Columnar primary; also row store | On‑prem; cloud (HANA Cloud) | Operational analytics, risk on operational data | In‑memory column store with ACID; SQL | Vendor/customer stories | ACID; MVCC; OLTP+OLAP on same data | SQL; calc views; compression | Scale‑up; scale‑out with distributed tables | Low‑ms OLTP + fast analytics | High compression in column store | License; infra for in‑memory | Requires HANA expertise | Enterprise security; banking industry | Native HTAP; mixed row/column | Memory cost; specialized ops | Banks globally (SAP banking page) | Vendor case studies | [HANA arch][79]; [Row vs Column][80]; [SAP Banking][100] |
| HTAP (row+column) | SingleStore | SingleStore | Relational (NewSQL) | Hybrid rowstore+columnstore | Self‑managed; managed | Operational analytics, real‑time BI on transactions | Unified engine; pipelines; MySQL‑compatible | Vendor studies; no official TPC | ACID; snapshot isolation; distributed TX | SQL; columnstore & rowstore; pipelines | Shared‑nothing; hash/range sharding | Sub‑second analytics on fresh data | Columnstore compression | License/SaaS; good price/perf | Ops simpler than polyglot | Enterprise features | Native HTAP (row+column) | Vendor lock‑in; workload tuning | Various fintechs (vendor) | Vendor | [Row vs Columnstore][81]; [Transactions][82] |
| HTAP (Distributed SQL + columnar) | TiDB + TiFlash | PingCAP | Relational (NewSQL) | Row (TiKV) + Columnar (TiFlash) | Self‑managed; cloud | OLTP with up‑to‑date analytics | Separation of row/column replicas; MySQL‑compatible | TPC‑H/TPC‑C‑like vendor tests; case studies | Distributed ACID; SI; optimistic/pessimistic TX | SQL; MPP for TiFlash; indexes | Horizontal scale; placement rules | Low‑ms OLTP; fast analytics via TiFlash | Columnar compression in TiFlash | Open core; managed service available | Ops of multi‑component system | Enterprise features in cloud | Native HTAP via TiFlash | Additional TiFlash cost/ops | WeBank (digital bank) | Vendor | [TiDB overview][88]; [TiFlash][89]; [Transactions][90]; [WeBank][101] |
| OLTP (Distributed SQL) | CockroachDB | Cockroach Labs | Relational (NewSQL) | Row (MVCC) | Self‑managed; Cloud | Global payments/ledgers, card auth | Geo‑distributed ACID with SERIALIZABLE by default | Jepsen and company results; TPC‑C‑like (non‑official) | ACID; SERIALIZABLE default | PostgreSQL‑compatible SQL; sec. indexes | Range‑based sharding; per‑region locality | ms‑level OLTP; WAN‑aware | Replication; automatic rebalancing | License/subscription | Requires topology design (latency) | Encryption, RBAC, audit | CDC to columnar/lake | Analytical scans slower than column stores | Form3 (real‑time payments) | Vendor case | [Architecture][92]; [Serializable][93]; [Form3 case][102] |
| OLTP (Distributed SQL) | YugabyteDB (YSQL) | Yugabyte | Relational (NewSQL) | Row (DocDB + Raft) | Self‑managed; Cloud | Core banking, payments, ledgers | PostgreSQL‑compatible SQL + distributed ACID | Vendor tests/cases | ACID; Serializable isolation | Full SQL; sec. indexes; stored procs (via PG) | Hash/range sharding; per‑table partitioning | ms‑level OLTP; geo‑replication | Compression at storage layer | Open source + managed | Operationally more complex than single node | Encryption; RBAC; audit | CDC/streams to analytics | Analytics slower than column stores | KakaoBank (core banking) | Vendor case | [Transactions][95]; [YSQL][96]; [KakaoBank][103] |

## HTAP Patterns and Architectures Used in Practice

- Single‑engine HTAP:
  - SAP HANA: in‑memory column store with a row store enables OLTP+OLAP on same data; chosen for operational analytics (e.g., intraday risk) where memory budgets and expertise exist [79][80].
  - SingleStore: dual storage engines with distributed ACID; pipelines ingest from Kafka for near‑real‑time analytics on transactional data [81][82].
  - TiDB+TiFlash: row (TiKV) for OLTP with columnar TiFlash replicas for analytics; SQL planner routes queries accordingly; popular where MySQL‑compatibility is desired with HTAP needs [88][89].
- Hybrid (polyglot) HTAP:
  - OLTP in PostgreSQL/Oracle/SQL Server/CockroachDB/YugabyteDB emits CDC to Kafka/Kinesis; real‑time analytics in Druid/ClickHouse for dashboards; durable analytics in Snowflake/BigQuery/Redshift/Databricks; materialized views in warehouses for near‑real‑time reporting [65][6][19][24][29][57].
  - Time‑series First: kdb+ or ClickHouse as tick store; lakehouse/warehouse for long‑horizon risk/reporting and ML feature stores; Druid for investigative UI on streams [5][6][57][41][19][24][29].

## Performance Evidence Landscape

- Tick/time‑series: STAC‑M3 audited results are the reference—kdb+ repeatedly sets records, with disclosures including node counts, storage, and dataset sizes; banks evaluate HW+SW stacks using STAC notices [5][46][45].
- Warehouses/lakehouse: Official TPC‑DS results are published on tpc.org. Databricks has an official historical TPC‑DS 100TB result (QphDS 32,941,245). Many other comparisons are vendor‑sponsored GigaOm studies; treat methodology carefully [43][58][21][25].
- OLTP: TPC‑C results are hosted by TPC; however, many modern distributed SQL systems publish TPC‑C‑like results outside tpc.org (not official). Use TPC’s results page for audited vendor submissions where available [97].

## Selection Checklist (Practical)

- Access pattern:
  - Row‑heavy point reads/writes with strict ACID → row store (PG/Oracle/SQL Server/Distributed SQL).
  - Scan/aggregate few columns over billions of rows → columnar OLAP (ClickHouse/Vertica/Warehouse/Lakehouse).
- Freshness vs cost:
  - Need analytics within seconds on hot operational data → HTAP (HANA/SingleStore/TiDB+TiFlash) or hybrid CDC to Druid/ClickHouse + warehouse/lakehouse.
  - Can tolerate minutes and favor governance/collaboration → Snowflake/BigQuery/Redshift/Databricks.
- Time‑series/tick:
  - Sub‑ms and STAC‑proven → kdb+; cost‑efficient OLAP → ClickHouse; SQL/ACID + TS functions → TimescaleDB.
- Platform constraints: On‑prem or data residency → Vertica, kdb+, self‑managed ClickHouse/Timescale; Cloud‑first → Snowflake/BigQuery/Redshift/Databricks/managed ClickHouse.
- Compliance/governance: Snowflake FS Data Cloud, cloud provider security programs, Unity Catalog/governance in lakehouses; ensure encryption, auditing, lineage [20][24][29][57].

### Sources
[1] Wikipedia – kdb+: https://en.wikipedia.org/wiki/Kdb%2B  
[2] DBDB – kdb+: https://dbdb.io/db/kdb  
[3] KX – kdb+ product page: https://kx.com/products/kdb/  
[4] ClickHouse Docs – MergeTree family: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/  
[5] STAC Research – STAC‑M3 program: https://www.stacresearch.com/m3  
[6] ClickHouse Blog – Juspay analyzes payment transactions: https://clickhouse.com/blog/juspay-analyzes-payment-transactions-in-real-time-with-clickhouse  
[7] ClickHouse Docs – Best practices for materialized views: https://clickhouse.com/docs/best-practices/use-materialized-views  
[8] ClickHouse Docs – Primary indexes: https://clickhouse.com/docs/primary-indexes  
[9] ClickHouse Docs – Kafka integration: https://clickhouse.com/docs/en/engines/table-engines/integrations/kafka  
[10] ClickHouse Blog – Coinhall platform story: https://clickhouse.com/blog/trade-secrets-how-coinhall-uses-clickhouse-to-power-its-blockchain-data-platform  
[11] ClickHouse Docs – Transactional semantics: https://clickhouse.com/docs/guides/developer/transactional  
[12] DBDB – Vertica entry: https://dbdb.io/db/vertica/revisions/22  
[13] Vertica Docs – Projections: https://docs.vertica.com/23.3.x/en/admin/projections/  
[14] Vertica Docs – Time‑series analytics overview: https://docs.vertica.com/12.0.x/en/data-analysis/time-series-analytics/  
[15] Vertica Docs – TIMESERIES clause: https://docs.vertica.com/11.1.x/en/data-analysis/time-series-analytics/gap-filling-and-interpolation-gfi/timeseries-clause-and-aggregates/  
[16] arXiv – Vertica perf context: https://arxiv.org/abs/2001.01192  
[17] Vertica Docs – Transactions and isolation: https://docs.vertica.com/24.2.x/en/admin/transactions/  
[18] Vertica Docs – Encoding types: https://docs.vertica.com/24.3.x/en/sql-reference/statements/create-statements/create-projection/encoding-types/  
[19] Snowflake Docs – Micro‑partitions and clustering: https://docs.snowflake.com/user-guide/tables-clustering-micropartitions  
[20] Snowflake – Financial Services Data Cloud: https://www.snowflake.com/news/snowflake-launches-the-financial-services-data-cloud-to-accelerate-customer-centric-and-data-driven-innovation-in-the-financial-services-industry/  
[21] GigaOm – Cloud DW performance testing: https://gigaom.com/report/cloud-data-warehouse-performance-testing/  
[22] Snowflake Docs – Transactions/isolation: https://docs.snowflake.com/en/sql-reference/transactions  
[23] Snowflake – S&P Global MI customer story: https://www.snowflake.com/en/customers/all-customers/case-study/sandp-global/  
[24] Google Cloud – BigQuery transactions (ACID, snapshot isolation): https://cloud.google.com/bigquery/docs/transactions  
[25] GigaOm – High‑performance cloud DW testing: https://gigaom.com/report/high-performance-cloud-data-warehouse-performance-testing/  
[26] Google Cloud – BigQuery materialized views: https://cloud.google.com/bigquery/docs/materialized-views-intro  
[27] Google Cloud – ATB Financial customer story: https://cloud.google.com/customers/atb-bigquery  
[28] Nasdaq Press – AWS AQUA: https://www.nasdaq.com/press-release/aws-announces-new-analytics-capabilities-to-help-customers-embrace-data-at-scale-2019  
[29] AWS – Redshift snapshot isolation default: https://aws.amazon.com/about-aws/whats-new/2024/05/amazon-redshift-snapshot-isolation-default  
[30] AWS – Redshift H3 functions: https://aws.amazon.com/about-aws/whats-new/2024/02/amazon-redshift-h3-indexing-spatial-grid-functions/  
[31] AWS Case Study – PayU on Redshift: https://aws.amazon.com/solutions/case-studies/payu-redshift-case-study/  
[32] Databricks Blog – Performance record claim (context): https://www.databricks.com/blog/2021/11/02/databricks-sets-official-data-warehousing-performance-record.html  
[33] Databricks Docs – Delta Lake isolation: https://docs.databricks.com/aws/en/lakehouse/acid  
[34] Databricks – Market Risk Accelerator: https://www.databricks.com/solutions/accelerators/market-risk  
[35] Databricks Blog – Coastal Community Bank: https://www.databricks.com/blog/coastal-community-bank-builds-thriving-financial-ecosystem-databricks-data-intelligence  
[36] Timescale Docs – Continuous aggregates: https://docs.timescale.com/use-timescale/latest/continuous-aggregates/about-continuous-aggregates/  
[37] PostgreSQL Docs – Transaction isolation levels: https://www.postgresql.org/docs/current/transaction-iso.html  
[38] Timescale API – add_compression_policy: https://docs.timescale.com/api/latest/compression/add_compression_policy/  
[39] Timescale – Security and compliance: https://www.timescale.com/security  
[40] InfluxData Blog – InfluxDB 3.0 performance: https://www.influxdata.com/blog/influxdb-3-0-is-2.5x-45x-faster-compared-to-influxdb-open-source/  
[41] Apache Druid Docs – Ingestion overview: https://druid.apache.org/docs/24.0.2/ingestion/index.html  
[42] Imply Blog – Fraud/AML with Druid: https://imply.io/blog/combating-financial-fraud-and-money-laundering-at-scale-with-apache-druid/  
[43] TPC – TPC‑DS results list: https://www.tpc.org/tpcds/results/tpcds_results5.asp  
[44] STAC Research – KDB211006: https://stacresearch.com/news/KDB211006  
[45] STAC Research – KDB231122 notice: https://stacresearch.com/KDB231122  
[46] STAC Research – KDB220506 notice: https://www.stacresearch.com/KDB220506  
[47] ClickHouse Docs – Kafka engine: https://clickhouse.com/docs/integrations/kafka/kafka-table-engine  
[48] Apache Druid Docs – Design: segments: https://druid.apache.org/docs/latest/design/segments/  
[49] Apache Druid Docs – Partitioning: https://druid.apache.org/docs/latest/ingestion/partitioning/  
[50] Vertica Docs – Eon architecture: https://docs.vertica.com/latest/en/architecture/eon-concepts/eon-architecture/  
[51] Snowflake Docs – Clustering/micro‑partitions (alt entry): https://docs.snowflake.com/user-guide/tables-clustering-micropartitions  
[52] Snowflake – Financial Services Data Cloud (alt page): https://www.snowflake.com/the-data-cloud-tour-financial-services/  
[53] Snowflake Docs – Iceberg table transactions (context): https://docs.snowflake.com/en/user-guide/tables-iceberg-transactions  
[54] BigQuery – Materialized views: https://cloud.google.com/bigquery/docs/materialized-views-intro  
[55] BigQuery – BI Engine: https://cloud.google.com/bigquery/docs/bi-engine-query  
[56] Amazon Press – Redshift Spectrum announcement: https://press.aboutamazon.com/2017/4/aws-launches-amazon-redshift-spectrum  
[57] Databricks Docs – Delta Lake (overview): https://docs.databricks.com/aws/en/delta/  
[58] TPC – Databricks historical TPC‑DS 100TB: https://www.tpc.org/5013  
[59] Databricks Docs – Structured Streaming with Delta: https://docs.databricks.com/aws/pt/structured-streaming/delta-lake  
[60] Timescale Docs – Distributed hypertables: https://docs.timescale.com/self-hosted/latest/distributed-hypertables/create-distributed-hypertables/  
[61] InfluxData Docs – InfluxDB 3 Enterprise SQL types: https://docs.influxdata.com/influxdb3/enterprise/reference/sql/data-types/  
[62] InfluxData Blog – Apache ecosystem with Dremio: https://www.influxdata.com/blog/how-influxdata-dremio-leverage-apache-ecosystem/  
[63] Apache Druid Docs – Design: segments (latest): https://druid.apache.org/docs/latest/design/segments/  
[64] Apache Druid Docs – Kafka ingestion (exactly‑once, older): https://druid.apache.org/docs/0.19.0/ingestion/index.html  
[65] Apache Druid Docs – Ingestion (overview; exactly‑once): https://druid.apache.org/docs/24.0.2/ingestion/index.html  
[66] Imply – DBS Bank AML video: https://imply.io/videos/summit/apache-druid-anti-money-laundering-dbs-bank/  
[67] Apache Druid Docs – Ingestion (older): https://druid.apache.org/docs//0.20.2/ingestion/index.html  
[68] Druid.io Docs – Ingestion (0.12.3 rollup): https://druid.io/docs/0.12.3/ingestion/index.html  
[69] ClickHouse Docs – Real-time analytics use cases: https://clickhouse.com/docs/cloud/get-started/cloud/use-cases/real-time-analytics  
[70] KX – Surveillance product: https://kx.com/products/surveillance/  
[71] Oracle Docs – Transactions (consistency/isolation): https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/transactions.html  
[72] Oracle – Financial Services industry page: https://www.oracle.com/industries/financial-services/  
[73] Microsoft Docs – SET TRANSACTION ISOLATION LEVEL: https://learn.microsoft.com/sql/t-sql/statements/set-transaction-isolation-level-transact-sql  
[74] Microsoft Docs – In‑Memory OLTP overview: https://learn.microsoft.com/sql/relational-databases/in-memory-oltp/in-memory-oltp-overview  
[75] Apache Cassandra Docs – Architecture overview: https://cassandra.apache.org/doc/latest/architecture/overview.html  
[76] Apache Cassandra Docs – Tunable consistency: https://cassandra.apache.org/doc/latest/operating/consistency.html  
[77] MongoDB Docs – Transactions: https://www.mongodb.com/docs/manual/core/transactions/  
[78] MongoDB Docs – Time series collections: https://www.mongodb.com/docs/manual/core/timeseries-collections/  
[79] SAP Help – SAP HANA Database architecture: https://help.sap.com/docs/SAP_HANA_PLATFORM/4fe29514fd584807ac9f2a04f6754767/2f0dffbd0c6e1014b6c7db2c35dd2347.html  
[80] SAP Help – Row store vs Column store: https://help.sap.com/docs/SAP_HANA_PLATFORM/4fe29514fd584807ac9f2a04f6754767/4f3bde7f761a1014b6d2c3bf75d2d8e4.html  
[81] SingleStore Docs – Rowstore vs Columnstore: https://docs.singlestore.com/managed-service/en/reference/information-about-sql-extensions/rowstore-and-columnstore.html  
[82] SingleStore Docs – Transactions: https://docs.singlestore.com/managed-service/en/developer-resources/transactions.html  
[83] SingleStore (product overview) – HTAP positioning: https://www.singlestore.com/product/  
[84] SingleStore – Pipelines overview: https://docs.singlestore.com/managed-service/en/developer-resources/data-ingestion/pipelines-overview.html  
[85] Google BigQuery – Raster data (geo analytics): https://cloud.google.com/bigquery/docs/raster-data  
[86] Snowflake – Data Cloud Tour FS: https://www.snowflake.com/the-data-cloud-tour-financial-services/  
[87] AWS – Redshift Spectrum (alt): https://press.aboutamazon.com/2017/4/aws-launches-amazon-redshift-spectrum  
[88] PingCAP Docs – TiDB overview: https://docs.pingcap.com/tidb/stable/overview  
[89] PingCAP Docs – TiFlash overview: https://docs.pingcap.com/tidb/stable/tiflash-overview  
[90] PingCAP Docs – Transaction overview: https://docs.pingcap.com/tidb/stable/transaction-overview  
[91] TiDB – Case studies page: https://pingcap.com/cases/  
[92] CockroachDB Docs – Architecture overview: https://www.cockroachlabs.com/docs/stable/architecture/overview.html  
[93] CockroachDB Docs – Serializable isolation: https://www.cockroachlabs.com/docs/stable/serializable  
[94] CockroachDB – CDC docs: https://www.cockroachlabs.com/docs/stable/change-data-capture.html  
[95] YugabyteDB Docs – Transactions architecture: https://docs.yugabyte.com/preview/architecture/transactions/  
[96] YugabyteDB Docs – YSQL (PostgreSQL API): https://docs.yugabyte.com/preview/api/ysql/  
[97] TPC – TPC‑C results list: https://www.tpc.org/tpcc/results/tpcc_results5.asp  
[98] DataStax – MobilePay case study: https://www.datastax.com/customers/mobilepay  
[99] MongoDB – Financial services industry: https://www.mongodb.com/industries/financial-services  
[100] SAP – Banking industry page: https://www.sap.com/industries/banking.html  
[101] PingCAP – WeBank case study: https://pingcap.com/case-studies/webank/  
[102] Cockroach Labs – Form3 case study: https://www.cockroachlabs.com/case-studies/form3/  
[103] Yugabyte – KakaoBank case study: https://www.yugabyte.com/case-studies/kakaobank/