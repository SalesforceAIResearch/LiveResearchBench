# Memory Management for LLM Agents (2023–2025): Architectures, Strategies, Trade-offs, and Evaluation

## Overview

Memory has become a central design axis for LLM agents. Between 2023–2025, work converged along two complementary paths: (1) scaling or restructuring the model’s internal memory (context windows, KV-cache, and attention/stateful variants), and (2) augmenting models with external memory systems (vector stores, structured knowledge bases, episodic/semantic stores, and reflective/summarization controllers). This review synthesizes advances in both autonomous agents and static LLMs augmented with memory, covering architectures, read/write/selection policies, reflection and distillation, memory editing/unlearning, safety/privacy, and evaluation. It emphasizes trends from top AI venues and influential preprints and open-source projects, and organizes findings by research thrusts and empirical trade-offs.

## External Memory and Retrieval-Augmentation for Agents

Retrieval-augmented generation (RAG) matured from single-turn QA to multi-session, tool-using agents with episodic and semantic memory. Early agent frameworks like ReAct synergized “reasoning + acting” by keeping visible traces of thoughts and actions during interaction, effectively a transient scratchpad that also conditions subsequent steps [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). Building on multi-step interaction, Reflexion introduced an explicit self-reflective memory: agents critique their own trajectories and write distilled insights for later reuse, improving credit assignment across trials and tasks [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366).

Long-horizon, multi-session memory pushed beyond transient traces. MemGPT designated short-, long-, and archival memory tiers with specialized read/write policies, using summarization and vector search to keep conversational agents coherent over extended interactions while controlling token cost [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560). Generative Agents implemented a psychologically-inspired memory stream for situated agents, scoring observations by recency, importance, and relevance, and inducing higher-level “reflections” to synthesize longer-term plans and social dynamics [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442). These works established that what to store (episodic vs. semantic), when to store (importance/novelty), and how to compress (summarization and embeddings) are critical knobs for reliable, scalable agent memory.

Within the RAG family, learning to decide when and how to retrieve became important to counteract over-retrieval and reduce hallucinations. Self-RAG jointly learns retrieval, generation, and critique, providing a controller that selects evidence and self-verifies claims [Self-RAG: Learning to Retrieve, Generate, and Critique for Better Language Modeling](https://arxiv.org/abs/2310.11511). GraphRAG extended this by constructing structured knowledge graphs and retrieving along graph topology, improving grounding and global coherence on large corpora while introducing graph-building overhead [GraphRAG (Microsoft)](https://github.com/microsoft/graphrag). At the user-personalization end, MemPrompt demonstrated a practical memory loop that records user corrections and retrieves them for future similar queries to reduce repeated hallucinations [MemPrompt: Memory-assisted Prompt Editing with Search](https://arxiv.org/abs/2305.13162).

Overall, the trend in 2023–2025 is toward unified memory stacks that (a) maintain episodic traces, (b) distill semantic summaries, and (c) coordinate retrieval through learned or rule-based controllers. The key trade-offs are: improved grounding and personalization versus higher latency and engineering complexity, plus new attack surfaces (e.g., memory poisoning and retrieval-time prompt injection).

## Reflection, Summarization, and Scratchpads

Reflection and summarization emerged as general-purpose memory management primitives. Reflexion-style critique logs help with credit assignment and reduce repeated errors across episodes [Reflexion](https://arxiv.org/abs/2303.11366). Summarization policies—often layered (daily/weekly summaries, task- and persona-level summaries)—curb memory growth and token cost while maintaining global coherence, as seen in MemGPT’s hierarchical design [MemGPT](https://arxiv.org/abs/2310.08560) and in the cognitive loops of Generative Agents [Generative Agents](https://arxiv.org/abs/2304.03442).

Scratchpads (chain-of-thought, ReAct traces) remain a strong transient memory mechanism; they improve single-session reasoning and tool control but can accumulate irrelevant tokens, amplifying “lost-in-the-middle” effects in long contexts [ReAct](https://arxiv.org/abs/2210.03629); [Lost in the Middle: How Language Models Use Long Context](https://arxiv.org/abs/2307.03172). Consequently, summarization and selection become necessary for long-horizon tasks. A pattern that emerged is: write granular traces; periodically summarize to semantic memory; index both with retrieval calibrated to task difficulty and uncertainty (e.g., only retrieve when confidence is low, à la Self-RAG [Self-RAG](https://arxiv.org/abs/2310.11511)).

## Long-Context Scaling vs. External Memory

A parallel line of work tries to keep more “inside” the model. Context-window extension methods (e.g., RoPE scaling such as YaRN) and long-context finetuning (e.g., LongLoRA) let static LLMs ingest substantially longer inputs without architectural changes, improving long-document QA and coding tasks while preserving base weights’ capabilities; however, performance often degrades as context grows, and models become sensitive to position effects [LongLoRA: Efficient Fine-tuning of LLMs for Long Context](https://arxiv.org/abs/2309.12307); [YaRN: Efficient Context Window Extension of LLMs](https://arxiv.org/abs/2309.00071). “Lost in the Middle” documented accuracy drops for information placed away from the ends of long contexts, underscoring the need for selection or structure over naïve concatenation [Lost in the Middle](https://arxiv.org/abs/2307.03172).

At inference time, KV-cache policies and attention variants address latency and memory footprint. StreamingLLM introduces “attention sinks” with sliding windows, enabling models to process streams of arbitrary length while keeping specific anchors in cache [StreamingLLM (MIT-HAI Lab)](https://github.com/mit-han-lab/streaming-llm). RetNet replaces standard attention with a retentive mechanism that maintains a recurrent state, allowing linear-time inference and stable long-sequence processing when trained accordingly [Retentive Network: A Successor to Transformer](https://arxiv.org/abs/2307.08621). KV-cache selection (e.g., heavy-hitter/salient token caching) offers practical speedups with minimal quality loss by caching only influential tokens instead of all keys/values [FlashAttention-2](https://github.com/Dao-AILab/flash-attention). The trade-off space is clear: long-context scaling simplifies the system but increases compute and can still fail with unstructured long inputs; external memory (RAG/episodic stores) adds engineering complexity and retrieval errors but reduces token/bandwidth needs and improves controllability, editability, and privacy options.

## Lifelong and Stateful Memory for Embodied, Web, and Coding Agents

Embodied and tool-use agents particularly benefit from explicit long-term memory. Voyager, a Minecraft agent, accumulates a skill library (code functions and experiences) discovered through autonomous exploration and self-verification; the library acts as a reusable semantic memory enabling faster curriculum progression and generalization to new tasks [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291). In web and multi-tool settings, frameworks such as AutoGen support multi-agent dialogues with persistent logs and external stores for coordination and reuse of tool results [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155). These agent memories must address write policies (what skills/results to store), indexing (by intent, API, site, or task), and replay/retrieval for robustness.

In code, repository-level tasks (e.g., SWE-bench) revealed strong benefits from structured retrieval over large codebases and from maintaining episodic traces of prior edits and test feedback; naive long-context concatenation is rarely efficient or reliable for multi-file reasoning [SWE-bench](https://arxiv.org/abs/2310.06770). The pattern across domains is consistent: stateful memory organized around reusable abstractions (skills, tools, files, web tasks) and semantically indexed episodic logs improves data efficiency, temporal generalization, and robustness, provided compaction and deduplication are applied.

## Memory Editing, Safety, and Privacy

Editing and erasure target the model’s internal “semantic memory.” MEMIT enables mass editing of factual associations in LLMs, updating many relations in a single step with better locality than naive finetuning [MEMIT: Mass-Editing Memory in a Transformer](https://arxiv.org/abs/2210.06169). Such methods are complementary to RAG, which supports non-destructive updates in external memory. A practical pattern emerges: keep volatile or personalized knowledge in external stores (easy to update, delete, and audit) and rely on editing only for global, stable corrections.

Safety and privacy risks increased with memory-equipped agents. Persistent stores can be poisoned or prompt-injected at retrieval time; long contexts leak sensitive data; and stored interaction logs can amplify privacy risks. Work on evaluating long-context vulnerabilities documented sensitivity to placement and format [Lost in the Middle](https://arxiv.org/abs/2307.03172). Structured RAG like GraphRAG [GraphRAG](https://github.com/microsoft/graphrag) and verification loops (Self-RAG) [Self-RAG](https://arxiv.org/abs/2310.11511) reduce hallucinations and can be combined with provenance checks, access controls, and red-teaming. Editing and unlearning remain open research areas for compliance (“right to be forgotten”) and safety.

## Evaluation: Settings, Benchmarks, and Metrics (2023–2025)

Evaluation diversified in 2023–2025 to cover long-horizon, tool-use, and personalized settings.

- Long-context reasoning/recall: LongBench (multi-task long-context suite), L-Eval (unified long-context benchmarks), and diagnostic probes like Needle-in-a-Haystack and Lost-in-the-Middle test retrieval/recall and positional robustness [LongBench](https://github.com/THUDM/LongBench); [L-Eval](https://arxiv.org/abs/2307.11088); [Lost in the Middle](https://arxiv.org/abs/2307.03172).
- Web/tool-use/planning: WebArena, Mind2Web, and AgentBench assess real or simulated web navigation, tool invocation, and planning across long tasks [WebArena](https://webarena.dev); [Mind2Web](https://arxiv.org/abs/2306.06070); [AgentBench](https://arxiv.org/abs/2308.03688).
- Coding and repository-level reasoning: SWE-bench measures end-to-end software bug-fixing with repo-scale context and feedback loops [SWE-bench](https://arxiv.org/abs/2310.06770).

Common metrics include: task success/return, factual consistency/hallucination rate, long-range recall and temporal generalization, retention/forgetting across sessions, interference, robustness to adversarial retrieval, privacy leakage, latency and throughput, token/cost efficiency, memory growth/compactness, and reproducibility (e.g., seeding, deterministic retrieval).

Gaps and needs: standardized multi-session personalization benchmarks with privacy constraints; metrics for write policy quality (overwriting vs. redundancy vs. loss); calibration under retrieval uncertainty; and unified cost-quality measurements that combine KV-cache, retrieval, and reflection overheads.

## Empirical Trends and Trade-offs

- Long-context alone is not enough. Even with extended windows, unstructured long prompts degrade accuracy and inflate cost; selection, structure, and summaries (or stateful attention) are needed [Lost in the Middle](https://arxiv.org/abs/2307.03172); [RetNet](https://arxiv.org/abs/2307.08621).
- Reflective memory improves temporal credit assignment. Reflexion-style critique memory and MemGPT-like tiered stores reduce repeated errors and stabilize long-horizon behavior but add latency and require robust write policies [Reflexion](https://arxiv.org/abs/2303.11366); [MemGPT](https://arxiv.org/abs/2310.08560).
- Structured retrieval reduces hallucination and improves global coherence. Controllers (Self-RAG) and structured stores (GraphRAG) outperform naive chunk retrieval on complex reasoning, at the expense of pipeline complexity [Self-RAG](https://arxiv.org/abs/2310.11511); [GraphRAG](https://github.com/microsoft/graphrag).
- KV-cache and attention innovations deliver practical speed/scale benefits. StreamingLLM and retentive/stateful attention reduce memory and compute while preserving long-range awareness when properly trained or configured [StreamingLLM](https://github.com/mit-han-lab/streaming-llm); [RetNet](https://arxiv.org/abs/2307.08621).
- Task-specialized stateful memory pays off. Skill libraries, tool traces, and repository-aware retrieval substantially improve embodied, web, and coding performance by making memory reusable at the right abstraction level [Voyager](https://arxiv.org/abs/2305.16291); [SWE-bench](https://arxiv.org/abs/2310.06770).

## Open Challenges

- Write/read policies and credit assignment: How to decide what to store, what to summarize, and when to retrieve under cost and safety constraints—without amplifying confirmation bias or accumulating stale/poisoned entries.
- Interference and drift: Avoiding contradictory or duplicated memories; handling temporal evolution (e.g., outdated APIs, changed preferences) with explicit versioning/decay.
- Calibration and verification: When to trust memory, when to re-query, when to self-critique; combining confidence estimates with retrieval/verifier loops (e.g., Self-RAG).
- Privacy, safety, and unlearning: Preventing privacy leakage from logs and caches; robust defenses against prompt injection and data poisoning in RAG; auditable deletion and policy-compliant unlearning in both external memory and model parameters (e.g., combining external memory deletion with internal editing via methods like MEMIT).
- Reproducibility and cost accounting: Standardizing evaluation for multi-session agents with reproducible seeds for retrieval, deterministic tool APIs, and cost/latency reporting that includes KV-cache, retrieval, and reflection overhead.

---

## Comparative Table (Selected Works 2023–2025)

| Year | Venue | Paper/Project | Memory Type/Architecture | Agent Type | Core Technique | Task/Benchmark/Protocol | Metrics | Key Findings | Limitations | Source URL | Code URL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | ICLR | ReAct | Scratchpad/tool-augmented traces (transient) | Autonomous | Interleaving reasoning and acting with explicit traces | QA, WebShop, ALFWorld | Task success | Combining thoughts/actions improves tool control and reasoning | Costly long traces; sensitive to context placement | https://arxiv.org/abs/2210.03629 | https://github.com/ysymyth/ReAct |
| 2024 | ICLR | Reflexion | Reflective memory (critiques, lessons) | Autonomous | Self-reflection write/read policy for credit assignment | ALFWorld, HotpotQA, coding | Success, sample efficiency | Reflection logs improve success across trials | Extra tokens/latency; needs good trigger policies | https://arxiv.org/abs/2303.11366 | https://github.com/noahshinn024/reflexion |
| 2023 | arXiv | MemGPT | Tiered episodic/semantic/archival memory with summarization & vector search | Autonomous assistant | Hierarchical memory manager, write thresholds, summarization | Multi-session dialogue | Retention, coherence, cost | Tiered memory stabilizes long sessions at lower token cost | Engineering complexity; retrieval calibration | https://arxiv.org/abs/2310.08560 | https://github.com/memgpt/memgpt |
| 2023 | arXiv (CHI’24 demo) | Generative Agents | Episodic stream + reflective summaries (importance/recency/relevance) | Autonomous (simulated) | Scored memory stream; induced reflections and plans | Simulated town interactions | Human eval, coherence | Reflection-driven summaries enable believable long-term behavior | Hard to quantify; domain-specific | https://arxiv.org/abs/2304.03442 | https://github.com/joonspk-research/generative_agents |
| 2023 | NeurIPS | Self-RAG | External retrieval with learned retrieve/generate/critique controller | Static LLM with memory | Joint policy for retrieval + self-critique | Open-domain QA, reasoning | Factuality, grounding | Controller reduces hallucinations vs naive RAG | Training/integration complexity | https://arxiv.org/abs/2310.11511 | https://github.com/selfrag/selfrag |
| 2024 | arXiv | GraphRAG | Structured knowledge store (knowledge graph) | Static/Agent | Graph construction + graph-based retrieval | Long-context QA, synthesis | Grounding, coherence | Structured retrieval improves global coherence and provenance | Graph building cost; maintenance overhead | https://github.com/microsoft/graphrag | https://github.com/microsoft/graphrag |
| 2023 | arXiv | MemPrompt | Episodic correction memory (user feedback) | Static/Agent | Store-and-retrieve past corrections to similar queries | QA, dialogue | Hallucination recurrence | Reduces repeated hallucinations over time | Needs reliable feedback; retrieval quality | https://arxiv.org/abs/2305.13162 | — |
| 2023 | NeurIPS (D&B) | Voyager | Skill library (semantic memory of code/tools) | Autonomous embodied | Autonomous curriculum + skill discovery & reuse | Minecraft | Progression, generalization | Reusable skills accelerate exploration and tasks | Domain-specific scaffolding | https://arxiv.org/abs/2305.16291 | https://github.com/MineDojo/Voyager |
| 2023 | arXiv | AutoGen | Multi-agent conversation logs + optional external stores | Autonomous (multi-agent) | Orchestrated agents with persistent histories | Coding, planning, tool use | Task success | Persistent multi-agent memory aids coordination | Framework (not a benchmark); eval varies | https://arxiv.org/abs/2308.08155 | https://github.com/microsoft/autogen |
| 2023 | arXiv/NeurIPS | StreamingLLM | KV-cache eviction/sinks for streaming long inputs | Static LLM | Sliding window + attention sinks | Long-context inference | Perplexity, recall | Enables effectively unbounded input processing | May forget global details if misconfigured | https://github.com/mit-han-lab/streaming-llm | https://github.com/mit-han-lab/streaming-llm |
| 2023 | NeurIPS | RetNet | Retentive/stateful attention (recurrent memory) | Static LLM | Retention mechanism for linear-time long-seq | Language modeling | PPL, throughput | Stateful memory supports long sequences efficiently | Requires training; integration cost | https://arxiv.org/abs/2307.08621 | — |
| 2023 | arXiv | LongLoRA | Long-context finetuning for context window extension | Static LLM | Parameter-efficient finetuning for long contexts | LongBench suite | Long-context accuracy | Extends context with moderate finetuning cost | Degrades at extreme lengths; data needs | https://arxiv.org/abs/2309.12307 | — |
| 2023 | arXiv | YaRN | RoPE scaling for longer windows | Static LLM | Position embedding extrapolation | Long-document QA | Accuracy vs window | Simple, effective extension of context | Sensitivity to placement; limits remain | https://arxiv.org/abs/2309.00071 | — |
| 2023 | EMNLP | LLMLingua | Prompt/context compression | Static/Agent | LLM-aware compression of inputs | QA, reasoning | Cost, accuracy | Reduces tokens while preserving quality | Compression errors can harm recall | https://arxiv.org/abs/2310.05736 | https://github.com/IntelLabs/LLMLingua |
| 2023 | EMNLP | Lost in the Middle | Diagnostic: position sensitivity in long contexts | Static/Agent | Analysis of retrieval/placement effects | Synthetic + QA | Accuracy vs position | Middle-position info often ignored | Calls for selection/structure | https://arxiv.org/abs/2307.03172 | — |
| 2023 | NeurIPS (D&B) | LongBench | Long-context benchmark suite | Static/Agent | Multi-task long-context eval | Multiple tasks | Accuracy, recall | Unified comparisons across long-context tasks | Synthetic bias; rapid model changes | https://github.com/THUDM/LongBench | https://github.com/THUDM/LongBench |
| 2023 | arXiv | L-Eval | Long-context evaluation suite | Static/Agent | Unified long-context tasks | Summarization, QA | Accuracy, grounding | Broad coverage across modalities/tasks | Evolving protocols | https://arxiv.org/abs/2307.11088 | — |
| 2023 | NeurIPS (D&B) | AgentBench | Agent evaluation (planning, tools, web) | Autonomous | Standardized agent tasks | Multi-domain | Success, robustness | Highlights gaps in planning/memory | Rapid drift; setup complexity | https://arxiv.org/abs/2308.03688 | https://github.com/THUDM/AgentBench |
| 2023 | NeurIPS (D&B) | WebArena | Web navigation environment | Autonomous | Realistic websites for agents | Web tasks | Success, efficiency | End-to-end eval for web memory/tool use | Environment upkeep, reproducibility | https://webarena.dev | https://github.com/web-arena-x/webarena |
| 2023 | EMNLP | Mind2Web | Open-world web agent dataset | Autonomous | Cross-website tasks with tool use | Web tasks | Success, generalization | Diverse, real-world tasks | Eval variance across sites/tools | https://arxiv.org/abs/2306.06070 | — |
| 2023 | NeurIPS (D&B) | SWE-bench | Repo-level coding benchmark | Autonomous/Static | Multi-file reasoning, testing | Software bug fixing | Task success, tests passed | Stresses memory for large codebases | Expensive eval; infra heavy | https://arxiv.org/abs/2310.06770 | https://github.com/princeton-nlp/SWE-bench |
| 2022–2023 | NeurIPS (orig. arXiv 2022) | MEMIT | Parameter-space memory editing/erasure | Static LLM | Mass editing of factual relations | CounterFact, QA | Edit success, specificity | Efficient, local edits vs finetuning | Risk of side effects; scope limits | https://arxiv.org/abs/2210.06169 | https://github.com/kmeng01/memit |
| 2023 | — | FlashAttention-2 | Attention kernel enabling long-context efficiency | Static LLM | IO-aware exact attention | LM, long-context | Throughput, memory | Large speedups, enabler for long contexts | Not a memory policy per se | https://github.com/Dao-AILab/flash-attention | https://github.com/Dao-AILab/flash-attention |

Notes:
- Venue markings reflect widely cited versions; several works began as arXiv preprints and later appeared in venues.
- Where official code is not confidently available, the field is left blank.

---

## Practical Guidance and Design Patterns

- For long-horizon agents (planning/web/embodied): combine episodic logs with semantic summaries and a retrieval controller. Use reflection to write distilled lessons and reduce repeated failures [Reflexion](https://arxiv.org/abs/2303.11366); [MemGPT](https://arxiv.org/abs/2310.08560).
- For knowledge-heavy tasks: prefer structured or controlled retrieval (e.g., graph-based) and verification/critique loops to reduce hallucination and improve provenance [Self-RAG](https://arxiv.org/abs/2310.11511); [GraphRAG](https://github.com/microsoft/graphrag).
- For efficiency: use prompt/context compression and KV-cache policies; if training is possible, consider stateful attention (RetNet) [LLMLingua](https://arxiv.org/abs/2310.05736); [StreamingLLM](https://github.com/mit-han-lab/streaming-llm); [RetNet](https://arxiv.org/abs/2307.08621).
- For personalization and safety: keep sensitive/user-specific knowledge external for easy deletion and auditing; apply memory editing (e.g., MEMIT) only to stable facts; instrument provenance and access controls; red-team retrieval pipelines [MEMIT](https://arxiv.org/abs/2210.06169).
- For evaluation: complement task success with retention/forgetting, temporal generalization, interference, privacy leakage, and cost/token growth metrics; benchmark both single-session and multi-session regimes [LongBench](https://github.com/THUDM/LongBench); [L-Eval](https://arxiv.org/abs/2307.11088); [AgentBench](https://arxiv.org/abs/2308.03688).

### Sources
[1] ReAct: Synergizing Reasoning and Acting in Language Models: https://arxiv.org/abs/2210.03629  
[2] Reflexion: Language Agents with Verbal Reinforcement Learning: https://arxiv.org/abs/2303.11366  
[3] MemGPT: Towards LLMs as Operating Systems: https://arxiv.org/abs/2310.08560  
[4] Generative Agents: Interactive Simulacra of Human Behavior: https://arxiv.org/abs/2304.03442  
[5] Self-RAG: Learning to Retrieve, Generate, and Critique for Better Language Modeling: https://arxiv.org/abs/2310.11511  
[6] GraphRAG (Microsoft) GitHub: https://github.com/microsoft/graphrag  
[7] MemPrompt: Memory-assisted Prompt Editing with Search: https://arxiv.org/abs/2305.13162  
[8] Voyager: An Open-Ended Embodied Agent with Large Language Models: https://arxiv.org/abs/2305.16291  
[9] AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation: https://arxiv.org/abs/2308.08155  
[10] StreamingLLM (MIT-HAI Lab) GitHub: https://github.com/mit-han-lab/streaming-llm  
[11] Retentive Network: A Successor to Transformer: https://arxiv.org/abs/2307.08621  
[12] LongLoRA: Efficient Fine-tuning of LLMs for Long Context: https://arxiv.org/abs/2309.12307  
[13] YaRN: Efficient Context Window Extension of LLMs: https://arxiv.org/abs/2309.00071  
[14] LLMLingua: Compressing Prompts for Accelerating Inference of Large Language Models: https://arxiv.org/abs/2310.05736  
[15] Lost in the Middle: How Language Models Use Long Context: https://arxiv.org/abs/2307.03172  
[16] LongBench GitHub: https://github.com/THUDM/LongBench  
[17] L-Eval: https://arxiv.org/abs/2307.11088  
[18] AgentBench: https://arxiv.org/abs/2308.03688  
[19] WebArena: https://webarena.dev  
[20] Mind2Web: https://arxiv.org/abs/2306.06070  
[21] SWE-bench: https://arxiv.org/abs/2310.06770  
[22] MEMIT: Mass-Editing Memory in a Transformer: https://arxiv.org/abs/2210.06169  
[23] FlashAttention-2 GitHub: https://github.com/Dao-AILab/flash-attention