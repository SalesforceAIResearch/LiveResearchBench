# Circuit Breakers vs. Timeouts, Retries, Bulkheads, and Rate Limiting in Cloud‑Native Systems

## Executive Summary

- Always bound work. Set explicit per‑request deadlines/timeouts and propagate them downstream; cancel server work on expiry to prevent wasted effort and inflated tail latency [1][2].
- Use retries sparingly, with exponential backoff and jitter, and only for idempotent operations; add retry quotas/budgets to prevent storms and kⁿ amplification across call graphs [2][21][22][23].
- Prefer client‑side throttling and early load shedding to keep queues short and preserve goodput under overload; use token‑bucket style rate limiting and criticality‑aware admission [4][8][20].
- Isolate failure domains with bulkheads (concurrency caps and per‑dependency pools) and multitenant sharding (e.g., shuffle sharding) to contain blast radius [9][19].
- Use circuit breakers judiciously to fail fast and apply backpressure when a dependency is unhealthy; include hysteresis (half‑open probes) to avoid flapping [10][11][54].
- Manage to SLOs and error budgets using percentile SLIs (p95/p99/p99.9) and burn‑rate alerts; tails matter more than means for user experience [51].

These controls interact: timeouts bound latency, retries recover transient failures but can amplify load, circuit breakers fail fast to prevent cascades, bulkheads contain blast radius, and rate limiting enforces backpressure. Their tuning should be grounded in queuing theory (Little’s Law) and tail latency principles [6][7] and instrumented to SLOs [51].


## Foundations: Latency, Queues, and Backpressure

- Tail latency dominates as systems scale; a small fraction of slow outliers can significantly impact user‑visible performance. Hedged/racing requests can reduce p99s if paired with strict budgets and cancellation of “losers” [5].
- Queuing basics: Little’s Law (L = λW) links concurrency (L), arrival rate (λ), and latency (W). As latency or arrival rate rises, in‑flight work rises—pressuring threads, fds, and memory [6].
- In an M/M/1 model, response time increases sharply as utilization approaches 1 (R ≈ 1/(μ−λ)), producing the familiar “hockey‑stick” curve—avoid running hot [7].
- Most cascades start with overload and propagate via retries/health‑based load balancing; prefer “fail early and cheaply,” short queues, and client‑side throttling [3][4].
- Load shedding preserves goodput during overload; rejecting early avoids paying cost for requests you will drop later [8].


## How Each Pattern Trades Off Key Dimensions

### 1) Timeouts and Deadlines

- Purpose. Bound end‑to‑end latency, free resources, and prevent work waste—especially crucial during overload [2][1].
- Latency. Deadlines cap p95/p99; too‑short timeouts cause false timeouts and extra retries; too‑long timeouts tie up scarce resources [2].
- Isolation/availability. Timely cancellation limits in‑flight work, reducing amplification and improving availability under partial failures [1][4].
- Operational needs. Propagate deadlines (e.g., gRPC Context) and instrument DEADLINE_EXCEEDED/error‑budget burn [1][51].
- Practical defaults.
  - Set per‑try timeout < overall deadline; adjust to downstream p99–p99.9 and user SLOs [12][51].
  - Always cancel server work on deadline expiry (gRPC supports this) [1].

Example (gRPC service config):
```json
{
  "methodConfig": [{
    "name": [{"service": "my.svc.Service"}],
    "retryPolicy": {
      "maxAttempts": 3,
      "initialBackoff": "0.2s",
      "maxBackoff": "2s",
      "backoffMultiplier": 2.0,
      "retryableStatusCodes": ["UNAVAILABLE","RESOURCE_EXHAUSTED"]
    },
    "timeout": "2s"
  }]
}
```
[22]


### 2) Retries with Exponential Backoff and Jitter

- Why jitter. Plain exponential backoff aligns retries; jitter spreads them and reduces collisions and excess work under failure [2].
- Latency/throughput. Retries help recover transient errors but add extra work; bound attempts and total retry budget to protect p99s and capacity [2][21].
- Isolation. Retry quotas/token buckets stop infinite amplification during downstream brownouts [21].
- Idempotency. Restrict retries to idempotent operations or use idempotency tokens; otherwise use compensating actions [23].
- Practical defaults.
  - 1–2 retries for interactive requests; exponential backoff with full jitter; cap max backoff [2][22].
  - Enforce retry budgets/quotas (SDK or proxy) to bound overhead [21][11].

gRPC retries (±20% jitter, status‑code gated) [22]. AWS SDKs implement token‑bucket and adaptive retry throttling to limit client amplification [21].


### 3) Circuit Breakers

- Purpose. Fail fast and apply backpressure when a dependency is degraded to prevent cascading failures; typical states: closed/open/half‑open with limited probes [10][54].
- Latency/availability. Reduce tail latency during partial failures by avoiding long waits; may reduce availability for the broken path but protect overall system [10].
- Flapping. Add hysteresis (cooldown; half‑open max probes) and use error‑rate plus concurrency signals to avoid oscillation [10][11].
- Placement. Close to the caller (client libraries or sidecars) to minimize wasted work [11].
- Practical defaults (mesh/sidecar).
  - Envoy cluster circuit breakers: set explicit caps for max_connections, max_pending_requests, max_requests, max_retries; optionally enable a retry_budget [11].
  - Pair with per‑try timeouts and retry budgets at the route [12].

Envoy cluster example:
```yaml
circuit_breakers:
  thresholds:
  - priority: DEFAULT
    max_connections: 512
    max_pending_requests: 256
    max_requests: 1024
    max_retries: 3
    retry_budget:
      budget_percent: { value: 20.0 }
      min_retry_concurrency: 10
```
[11]


### 4) Bulkheads (Isolation)

- Concept. Partition resources (threads, connections, queues) per dependency/route/tenant so one slow thing can’t starve others [9].
- Latency/throughput. Caps prevent latency‑driven concurrency spikes via Little’s Law; some utilization is traded for isolation [6][9].
- Multitenancy. Use per‑tenant quotas and shuffle sharding to confine a tenant’s blast radius to a tiny fraction of total capacity [19].


### 5) Rate Limiting and Load Shedding

- Algorithms. Token/leaky bucket are standard for shaping and policing; token bucket bounds average rate and burstiness [20].
- Client‑side throttling. Adaptive client‑side throttling (keep requests ≈ K×recent accepts) stabilizes global rates using only local signals [4].
- Overload. Drop low‑priority work early; keep queues short; validate that “drop cost” is cheap [8][4].
- Mesh/gateway. Use per‑route local rate limits and global front‑door throttling to guard shared dependencies [14][42][44].


## Interactions and Recommended Ordering

- For synchronous calls: deadline > per‑try timeouts; per‑try retries with jittered backoff; client‑side rate limit; circuit breaker and bulkhead in client/sidecar; early shedding at proxy/gateway [1][2][11][12][14][20].
- Align budgets. Make retry budgets and circuit‑breaker thresholds consistent with SLOs and error‑budget burn alerts [11][51].
- Beware amplification. Depth‑n graphs with k retries per hop can amplify to ~kⁿ. Prefer one retry layer, capped budgets, and client‑side throttling [2][21][4].
- Backpressure first. Rate limit/throttle at the source; keep queues small; avoid head‑of‑line blocking and queue collapse [4][8][20].


## Workload‑Specific Guidance

### A) Synchronous HTTP/gRPC

- Set per‑RPC deadlines; propagate and cancel server work on expiry [1].
- Retries: only for idempotent methods; configure gRPC retry policy with capped attempts and jitter; consider hedging for idempotent reads with strict budgets [22][5][23].
- Sidecar/mesh: configure Envoy/Istio per‑route timeouts, per‑try timeouts, retries with backoff; enable circuit breakers and outlier ejection [12][15][11][13].

Istio example:
```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
spec:
  hosts: [ ratings ]
  http:
  - timeout: 8s
    retries:
      attempts: 2
      perTryTimeout: 3s
      retryOn: gateway-error,connect-failure,refused-stream
```
[15]

DestinationRule “bulkhead‑like” pools and outlier detection:
```yaml
trafficPolicy:
  connectionPool:
    tcp: { maxConnections: 100 }
    http:
      http1MaxPendingRequests: 512
      http2MaxRequests: 1024
      maxRequestsPerConnection: 100
  outlierDetection:
    consecutive5xxErrors: 5
    interval: 10s
    baseEjectionTime: 30s
    maxEjectionPercent: 10
```
[16]


### B) Asynchronous Messaging/Streaming

- Producer idempotence/transactions and bounded buffers (block/back off) for safe retries (Kafka idempotent/transactional producers) [24].
- Consumer backpressure/flow control (e.g., RabbitMQ prefetch) to cap in‑flight work and avoid consumer overload [25].
- Per‑tenant limits and sharding to isolate hot senders; apply token‑bucket rate limits at ingress [19][20].


## Multitenancy and Noisy‑Neighbor Protection

- Shuffle sharding isolates tenants so an attack/failure affects only a small shard (e.g., mapping tenants to small subsets of workers) [19].
- Apply per‑tenant quotas at ingress and in sidecars; combine with bulkheads (per‑tenant pools) and local rate limiting [11][14][19].


## Deployment Contexts

- Service meshes (Envoy/Istio/Linkerd). Provide built‑in timeouts, retries, local rate limiting, circuit breakers, outlier ejection, and retry budgets; configure explicitly rather than relying on distro defaults [11][12][13][15][16][17][18].
- API gateways. Use route/stage throttles (e.g., AWS API Gateway), WAF rate‑based rules, and upstream timeouts aligned with app deadlines [42][43][44].
- L7/L4 proxies. NGINX limit_req (token bucket) for rate limiting; tune burst/delay; reuse connections; fail fast on bad upstreams [39].
- Kubernetes. Set realistic resource requests/limits (QoS), readiness/liveness/startup probes, HPA with stabilization, PDBs, and graceful termination to avoid overload oscillations during scaling and rollouts [46][47][48][49][50].


## Failure Modes and Edge Cases

- Slow responses/brownouts. Deadlines, cancellation, and load shedding are critical; circuit breakers protect callers from long waits [1][8][10].
- Fail‑stop errors. Timeouts and circuit breakers trip quickly; outlier ejection removes bad instances from load‑balancing pools [13][10].
- Network partitions (CAP). Under partitions, systems choose between availability and consistency; resilience controls like timeouts and shedding typically bias toward availability [26].
- Idempotency. Only retry idempotent operations (HTTP PUT/DELETE are defined idempotent) or use idempotency tokens (e.g., AWS EC2 ClientToken) [23].
- Retry storms and thundering herd. Jitter all retries; centralize retry policy; use retry budgets and client‑side throttling [2][21][4].
- Circuit breaker flapping. Use half‑open probe limits and cooldowns; combine error‑rate and concurrency signals [10][11].


## Practical Defaults and Tunables (by stack)

Calibrate with load tests to your own downstream p95–p99.9 and SLOs. Start conservative (short timeouts; few retries; small concurrency) and iterate.

- Java (Resilience4j)
  - TimeLimiter: timeoutDuration ~2s; cancelRunningFuture=true [27].
  - CircuitBreaker: failureRateThreshold=50, slidingWindowSize=100, minimumNumberOfCalls=100, waitDurationInOpenState=60s (documented defaults; set explicitly) [28].
  - Retry: maxAttempts=3 with exponential backoff (IntervalFunction), add jitter and cap delays [29].
  - Bulkhead: semaphore maxConcurrentCalls≈25; maxWaitDuration=0 (default) [30].

- .NET (Polly v8)
  - Timeout: override default; e.g., 2–3s per I/O call [32].
  - Retry: 1–2 retries; exponential backoff with jitter; cap MaxDelay [33].
  - Circuit breaker: FailureRatio≈0.2, MinimumThroughput 50–100, Sampling 30s, Break 30s (defaults differ; set explicitly) [34].

- Go
  - Circuit breaker (sony/gobreaker): Timeout 30–60s; half‑open MaxRequests 1–3; default ReadyToTrip trips after >5 consecutive failures [35].
  - HTTP retries (go‑retryablehttp): RetryMax 1–2; jittered backoff strategy [36].

- Node.js
  - Circuit breaker (opossum): timeout ~3000ms, errorThresholdPercentage 50, resetTimeout 30000ms; set rollingCount window and volumeThreshold [37].
  - Retry and breaker (cockatiel): decorrelated jitter exponential backoff; breaker on 5 consecutive failures [38].

- Envoy/Istio/Linkerd
  - Route timeouts and retries (per‑try) with explicit backoff; keep overall timeout > sum of per‑try timeouts [12][15][17].
  - Cluster circuit breakers with retry_budget; outlier ejection enabled [11][13].
  - Local rate limiting per route/pod; consider adaptive concurrency cautiously [14][52][18].

- Gateways/front door
  - NGINX limit_req zone burst/delay (e.g., 10 r/s burst 20) [39].
  - Kong rate limiting (move to Redis/Advanced for accuracy at scale) [40][41].
  - AWS API Gateway throttles (RPS + burst) and WAF rate‑based rules; align integration timeouts with app deadlines (Regional/private can exceed 29s, but keep bounded) [42][44][43].

- Kubernetes platform guardrails
  - Resource requests/limits and QoS; probes (tune defaults); HPA with scale‑down stabilization; PDB; terminationGracePeriodSeconds to cover in‑flight requests [46][47][48][49][50].


## Concrete Code and Config Examples

- Resilience4j (Java):
```java
CircuitBreakerConfig cbCfg = CircuitBreakerConfig.custom()
  .failureRateThreshold(50f).slidingWindowSize(100).minimumNumberOfCalls(100)
  .waitDurationInOpenState(Duration.ofSeconds(60)).build(); // [28]
TimeLimiterConfig tlCfg = TimeLimiterConfig.custom()
  .timeoutDuration(Duration.ofSeconds(2)).cancelRunningFuture(true).build(); // [27]
RetryConfig rCfg = RetryConfig.custom()
  .maxAttempts(3)
  .intervalFunction(IntervalFunction.ofExponentialBackoff(200, 2.0)) // add jitter
  .build(); // [29]
BulkheadConfig bhCfg = BulkheadConfig.custom()
  .maxConcurrentCalls(25).maxWaitDuration(Duration.ZERO).build(); // [30]
```

- Polly (.NET):
```csharp
var pipeline = new ResiliencePipelineBuilder<HttpResponseMessage>()
  .AddTimeout(TimeSpan.FromSeconds(2)) // [32]
  .AddRetry(new RetryStrategyOptions<HttpResponseMessage>{
    MaxRetryAttempts = 2, BackoffType = DelayBackoffType.Exponential, UseJitter = true,
    Delay = TimeSpan.FromMilliseconds(500) }) // [33]
  .AddCircuitBreaker(new CircuitBreakerStrategyOptions<HttpResponseMessage>{
    FailureRatio = 0.2, MinimumThroughput = 50,
    SamplingDuration = TimeSpan.FromSeconds(30), BreakDuration = TimeSpan.FromSeconds(30) }) // [34]
  .Build();
```

- Envoy route (timeouts, retries, backoff):
```yaml
route:
  timeout: 3s
  retry_policy:
    retry_on: 5xx,connect-failure,reset
    num_retries: 2
    per_try_timeout: 1s
    retry_back_off: { base_interval: 100ms, max_interval: 1s }
```
[12]

- NGINX rate limit:
```nginx
limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;
server {
  location /api/ {
    limit_req zone=perip burst=20 delay=8;
    proxy_pass http://upstream;
  }
}
```
[39]


## Observability, Alerting, and SLOs

- Define SLIs across availability and latency percentiles (p95/p99/p99.9). Alert on error‑budget burn rates rather than raw thresholds; “metrics are distributions” and tails often behave differently [51].
- Instrument and dashboard:
  - Deadline/timeouts and cancellation counts [1].
  - Retry attempt counts, backoff distribution, and budget/token exhaustion [21][22].
  - Circuit‑breaker state transitions and rejection counts [10][11].
  - Bulkhead rejections and in‑flight concurrency per dependency [9].
  - Rate‑limit drops (local and front door) and shed‑load decisions [8][14][42].


## Real‑World Case Studies and Patterns

- Tail latency and hedging at scale (Web search + GFS workloads): “The Tail at Scale” demonstrates that modest replication/hedging can materially reduce p99 latency, especially with large fan‑outs—when combined with cancellations and budgets [5].
- Cascading failures and overload handling (Google SRE). “Fail early and cheaply,” keep queues short, employ client‑side throttling, and categorize traffic by criticality to avoid collapses [3][4].
- AWS Builders’ Library series:
  - Timeouts/retries with jitter prevent synchronized retries, improve completion time, and reduce excess work [2].
  - Load shedding maintains goodput by dropping early; dropping late wastes resources [8].
  - Dependency isolation via bulkheads and concurrency caps prevents slowdowns from propagating [9].
  - Shuffle sharding isolates tenants; reduces blast radius in multitenant systems [19].
  - “Resilience lessons from the lunch rush”: practical advice on retry budgets, constant‑work patterns, and backpressure [55].


## When to Prefer Circuit Breakers vs. Related Controls

- Prefer timeouts/deadlines first to bound latency and prevent waste. Add retries with jitter only for idempotent, transient failures and with strict budgets [1][2][23].
- Add circuit breakers when:
  - The downstream exhibits brownouts/slow failures that inflate tail latency and tie up resources [10].
  - You need to fail fast and apply backpressure to protect the caller and upstream dependencies [11][54].
  - You can provide safe fallbacks/degraded responses or alternative providers.
- Use bulkheads and per‑route/tenant concurrency caps to contain blast radius; pair with circuit breakers for degraded dependencies [9][11][16].
- Enforce client‑side rate limits/adaptive throttling to stabilize traffic and prevent retry storms; add gateway/WAF throttles as global guardrails [4][14][42][44].


## Checklist to Deploy Safely

- Set and propagate per‑request deadlines (p99–p99.9 aligned) and per‑try timeouts; cancel on expiry [1][12].
- Enable bounded, jittered retries for idempotent operations; add retry budgets or token buckets [2][21][22][23].
- Configure circuit breakers and outlier ejection in clients/sidecars; add half‑open probes and cooldowns [10][11][13].
- Add bulkheads: per‑dependency concurrency caps and queues kept small (prefer 0) [4][9].
- Apply client‑side throttling and local/global rate limits; implement priority‑based shedding [4][14][42].
- Validate with load tests to find “knees” in latency/utilization; tie thresholds to SLOs and error‑budget policies [7][51].
- Observe and alert on tail latency, deadlines exceeded, retries/budgets, breaker opens, bulkhead rejections, and shed counts [51].


### Sources

[1] gRPC: Deadlines — https://grpc.io/docs/guides/deadlines/  
[2] AWS Builders’ Library: Timeouts, retries, and backoff with jitter — https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/  
[3] SRE Book: Addressing Cascading Failures — https://sre.google/sre-book/addressing-cascading-failures/  
[4] SRE Book: Handling Overload — https://sre.google/sre-book/handling-overload/  
[5] Dean & Barroso, The Tail at Scale (CACM) — https://cacm.acm.org/research/the-tail-at-scale/  
[6] Hopp & Spearman (Little’s Law Retrospective) — https://pubsonline.informs.org/doi/abs/10.1287/opre.1110.0940  
[7] Harchol‑Balter, Introduction to Queueing — https://www.cambridge.org/core/books/performance-modeling-and-design-of-computer-systems/introduction-to-queueing/22FC745E9EF8829F5D61EE58B7235E40  
[8] AWS Builders’ Library: Using load shedding to avoid overload — https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/  
[9] AWS Builders’ Library: Dependency isolation — https://aws.amazon.com/builders-library/dependency-isolation/  
[10] Azure Architecture Center: Circuit breaker pattern — https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker  
[11] Envoy: Cluster circuit breakers (incl. retry budgets) — https://www.envoyproxy.io/docs/envoy/latest/configuration/upstream/cluster_manager/cluster_circuit_breakers  
[12] Envoy router filter: timeouts, retries, backoff — https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/router_filter.html  
[13] Envoy outlier detection (API v3) — https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/outlier_detection.proto  
[14] Envoy HTTP local rate limit filter — https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter  
[15] Istio VirtualService reference — https://istio.io/latest/docs/reference/config/networking/virtual-service/  
[16] Istio DestinationRule reference (v1.17) — https://istio.io/v1.17/docs/reference/config/networking/destination-rule/  
[17] Linkerd: Retries and timeouts — https://linkerd.io/2.17/features/retries-and-timeouts/  
[18] Linkerd: Rate limiting — https://linkerd.io/2.17/features/rate-limiting/  
[19] AWS Builders’ Library: Workload isolation using shuffle sharding — https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/  
[20] RFC 2475: Differentiated Services Architecture (token/leaky bucket context) — https://datatracker.ietf.org/doc/html/rfc2475  
[21] AWS SDKs: Retry behavior (token bucket, adaptive rate) — https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html  
[22] gRPC: Retries (policy, jitter, hedging) — https://grpc.io/docs/guides/retry/  
[23] HTTP Semantics (RFC 9110): Idempotency and Methods — https://httpwg.org/specs/rfc9110  
[24] Apache Kafka Producer Javadoc (idempotence/transactions/blocking) — https://kafka.apache.org/36/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html  
[25] RabbitMQ: Consumer Prefetch — https://www.rabbitmq.com/docs/3.13/consumer-prefetch  
[26] Gilbert & Lynch (2002): CAP theorem — https://dl.acm.org/doi/abs/10.1145/564585.564601  
[27] Resilience4j: TimeLimiter docs — https://resilience4j.readme.io/docs/timeout  
[28] Resilience4j CircuitBreaker Javadoc (defaults/options) — https://javadoc.io/static/io.github.resilience4j/resilience4j-circuitbreaker/2.3.0/io/github/resilience4j/circuitbreaker/CircuitBreakerConfig.Builder.html  
[29] Resilience4j RetryConfig Javadoc (interval functions) — https://javadoc.io/static/io.github.resilience4j/resilience4j-retry/1.3.1/io/github/resilience4j/retry/RetryConfig.Builder.html  
[30] Resilience4j: Bulkhead docs — https://resilience4j.readme.io/docs/bulkhead  
[31] Spring Cloud Circuit Breaker reference (Resilience4j) — https://docs.spring.io/spring-cloud-circuitbreaker/docs/current/reference/html/spring-cloud-circuitbreaker.html  
[32] Polly Timeout strategy — https://www.pollydocs.org/strategies/timeout.html  
[33] Polly Retry strategy — https://www.pollydocs.org/strategies/retry  
[34] Polly Circuit Breaker strategy — https://www.pollydocs.org/strategies/circuit-breaker.html  
[35] sony/gobreaker README — https://github.com/sony/gobreaker/blob/master/README.md  
[36] hashicorp/go-retryablehttp — https://pkg.go.dev/github.com/hashicorp/go-retryablehttp  
[37] opossum (Node.js circuit breaker) — https://www.npmjs.com/package/opossum/v/6.2.0  
[38] cockatiel (Node.js resilience) — https://github.com/connor4312/cockatiel  
[39] NGINX: limit_req module — https://nginx.org/en/docs/http/ngx_http_limit_req_module.html  
[40] Kong Gateway: rate limiting (getting started) — https://docs.konghq.com/gateway/latest/get-started/rate-limiting/  
[41] Kong Rate Limiting Advanced — https://developer.konghq.com/plugins/rate-limiting-advanced/  
[42] AWS API Gateway: throttling — https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html  
[43] AWS: API Gateway integration timeout > 29s (Regional/private) — https://aws.amazon.com/about-aws/whats-new/2024/06/amazon-api-gateway-integration-timeout-limit-29-seconds/  
[44] AWS WAF: configurable time windows for rate-based rules — https://aws.amazon.com/about-aws/whats-new/2024/03/aws-waf-rate-based-rules-configurable-time-windows/  
[45] AWS Application Load Balancers (idle timeout defaults, etc.) — https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html  
[46] Kubernetes: Manage resources for containers — https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/  
[47] Kubernetes: Pod QoS classes — https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/  
[48] Kubernetes API reference (Pod v1 fields, probe defaults) — https://github.com/kubernetes/website/blob/main/content/en/docs/reference/kubernetes-api/workload-resources/pod-v1.md  
[49] Kubernetes: Horizontal Pod Autoscaler — https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/  
[50] Kubernetes: Pod lifecycle (termination grace) — https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/  
[51] SRE Book: Service Level Objectives — https://sre.google/sre-book/service-level-objectives/  
[52] Envoy adaptive concurrency filter — https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter  
[53] Envoy L4 local rate limit — https://www.envoyproxy.io/docs/envoy/latest/configuration/listeners/network_filters/local_rate_limit_filter  
[54] Envoy Gateway: circuit breaker task (quote) — https://gateway.envoyproxy.io/v1.0/tasks/traffic/circuit-breaker/  
[55] AWS Builders’ Library: Resilience lessons from the lunch rush — https://aws.amazon.com/builders-library/resilience-lessons-from-the-lunch-rush/