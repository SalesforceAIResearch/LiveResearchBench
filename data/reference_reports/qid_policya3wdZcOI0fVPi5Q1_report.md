# Colorado SB24-205 vs. Texas Responsible Artificial Intelligence Governance Act (HB 149, “TRAIGA”): What Large Technology Enterprises Need to Do Now

## Executive Summary

- Colorado’s Artificial Intelligence Act (SB24-205) establishes a “high-risk AI” framework that imposes affirmative duties on developers and deployers to use reasonable care to avoid algorithmic discrimination, with defined disclosures, risk assessments, and consumer rights around consequential decisions; the effective date was delayed to June 30, 2026, with further adjustments anticipated. Enforcement is by the Colorado Attorney General under the state consumer protection regime. [1], [2], [3], [4]

- Texas enacted the Texas Responsible Artificial Intelligence Governance Act (HB 149) in June 2025 (commonly referred to as “TRAIGA” in commentary, though the official short title omits “Generative”), effective January 1, 2026. HB 149 creates a new Texas Business & Commerce Code Title 11, Subtitle D (Chs. 551–554), specifies prohibitions (e.g., intentional discrimination; manipulation/self-harm incitement; certain sexually explicit AI), sets limited disclosure duties and AG information rights, preempts local AI ordinances, creates an AI regulatory sandbox under the Texas Department of Information Resources (DIR), amends biometric and TDPSA provisions, and provides safe harbors tied to recognized AI risk frameworks. Exclusively enforced by the Texas Attorney General, with tiered penalties and a mandatory cure process. [5]

- Texas also enacted complementary public-sector AI statutes in 2025 affecting vendor expectations (DIR AI Code of Ethics aligned to NIST AI RMF; standardized public notices; “heightened scrutiny” standards; agency AI division; training requirements). These influence contracting and due diligence for private vendors that sell to Texas state or local agencies. [6], [7], [8], [9], [10]

- For a multi-state technology enterprise, Colorado sets a higher, process-centric baseline (risk management, impact assessments, consumer rights), while Texas focuses on intent-based prohibitions, transparency in specific contexts, and integration with privacy/biometric law. A unified enterprise program anchored to NIST AI RMF, robust impact assessments for consequential decisions, and privacy-by-design (TDPSA) can satisfy or exceed both regimes, with targeted overlays for each state’s unique requirements. [5], [6], [1], [3], [4], [11]


## Plain-English Overviews

### Colorado Artificial Intelligence Act (SB24-205)
- Purpose and scope: Creates a statewide framework to reduce algorithmic discrimination from “high-risk AI systems” used to make (or substantially factor into) consequential decisions (e.g., employment, housing, credit, healthcare), and requires consumer transparency when AI interacts with consumers. [1]
- Who it applies to: Developers and deployers of high-risk AI systems, plus general consumer-interaction AI notice obligations; enforced by the Colorado Attorney General. [1]
- Effective dates and status: Enacted in 2024. The effective date was delayed in 2025 to June 30, 2026, with further changes anticipated as part of an ongoing legislative process. [2], [3], [4]
- Implementing authority: Colorado Attorney General under the state’s consumer protection framework; watch for rulemaking/guidance and further legislative adjustments prior to the delayed effective date. [1], [2], [3], [4]

### Texas Responsible Artificial Intelligence Governance Act (HB 149, 2025) (“TRAIGA” in common usage)
- Purpose and scope: Establishes general private-sector AI prohibitions (e.g., intentional discrimination; incitement of self-harm/crime), targeted disclosures (e.g., healthcare AI use), AG information rights, a regulatory sandbox, and safe harbors tied to NIST-aligned risk management. Preempts local AI ordinances. Effective January 1, 2026. [5]
- Who it applies to: “Any person” doing business in Texas or developing/deploying AI in Texas; exclusive AG enforcement; no private right of action under HB 149. [5]
- Related public-sector AI measures: DIR must adopt an AI Code of Ethics aligned with the NIST AI RMF, standardize public notices for public-facing AI and AI controlling consequential decisions, and set “heightened scrutiny” standards. DIR also gets an AI Division and must certify AI training for state/local personnel. These measures shape vendor obligations through contracts and RFPs. [6], [7], [8], [9], [10]
- Effective dates and implementing authority: HB 149 effective Jan 1, 2026; AG online complaint portal due Sept 1, 2026. DIR rules for the sandbox, ethics, and training to be adopted under separate statutes effective Sept 1, 2025. [5], [6], [7], [8], [9], [10]


## Side-by-Side Comparison Table (with citations)

| Dimension | Colorado SB24-205 | Texas HB 149 (“TRAIGA”) and related 2025 AI measures |
|---|---|---|
| 1) Covered entities and roles | - Applies to “developers” and “deployers” of “high-risk AI systems,” along with general consumer-interaction AI disclosure duties. Enforcement by Colorado AG under consumer protection law. [1]  - Statewide framework; 2025 legislation delays effective date to June 30, 2026 and indicates further changes anticipated. [2], [3], [4] | - Subtitle applies to “any person” who does business in Texas, produces products/services used by Texans, or develops/deploys AI in Texas. [5]  - Roles: “developer” and “deployer” defined in HB 149 Ch. 552.001; AG has exclusive enforcement authority. [5]  - Preemption: supersedes local AI ordinances. [5] |
| 2) Covered systems and use cases | - “High-risk AI system” (used to make or be a substantial factor in “consequential decisions” across domains such as employment, credit, housing, etc.) and broader duty for AI that “interacts with consumers.” See SB24‑205 bill page for definitions and domains. [1]  - Further legislative adjustments are expected before the delayed effective date. [2], [3] | - “Artificial intelligence system” defined in Ch. 551.001. [5]  - Prohibitions: development/deployment with intent to incite self-harm/crime; governmental social scoring; certain biometric identification uses by government; development/deployment with sole intent to infringe constitutional rights; intentional unlawful discrimination (disparate impact alone is insufficient). [5]  - Sexually explicit deepfakes/child exploitation content prohibited; separate civil and criminal regimes augmented by SB 441/HB 581. [5], [12], [13] |
| 3) Disclosure and transparency | - Deployer notice when using high-risk AI to make a consequential decision; adverse-action style notices and human review/appeal rights are part of the framework; general disclosure when an AI system interacts with consumers. See the official SB24‑205 page for text; implementation is delayed to 6/30/2026 with further changes anticipated. [1], [2], [3] | - Healthcare providers must disclose if AI is used “in relation to health care service or treatment” by the first service date (emergency exception). [5]  - Governmental entities must disclose when consumers interact with AI; standardized notices and public-facing AI requirements will flow from SB 1964 rules (vendor implications). [5], [7]  - No general private-sector AI labeling/watermarking mandate in HB 149; election and sexual deepfake statutes impose separate liabilities (criminal/civil). [11], [12], [13] |
| 4) Risk management and governance | - Developer/deployer duties include “reasonable care” to avoid algorithmic discrimination; risk management programs; impact assessments; testing/validation; documentation; post-deployment monitoring; human oversight—details to be finalized with the delayed effective date and potential further statutory changes. [1], [2], [3], [4] | - HB 149 provides safe-harbor/defense concepts: discovery via red-teaming/adversarial testing and “substantial compliance” with recognized frameworks such as the NIST AI RMF Generative AI Profile as part of an internal review. [5]  - AG may request high-level documentation (purpose, data types, outputs, testing metrics, known limitations, safeguards). [5]  - For government procurements/use, SB 1964 mandates NIST AI RMF-aligned AI Code of Ethics, standards for “heightened scrutiny” systems, testing and oversight expectations—likely to be pushed via contracts to private vendors. [7] |
| 5) Vendor and third-party management | - Developers must provide deployers technical documentation and updates; deployers must maintain documentation and conduct assessments; integration with vendor management and flow-down terms anticipated when rules/guidance finalize. [1], [2], [3] | - TDPSA processor duties explicitly include personal data “collected, stored, and processed by an artificial intelligence system” effective 1/1/2026, affecting processor assistance and contractual clauses/audit rights. [5], [8]  - AG documentation requests may reach developer/deployer records. [5]  - DIR AI standards (SB 1964) will set public-sector vendor expectations (notice language, testing, monitoring, complaint intake). [7] |
| 6) Enforcement mechanisms | - Enforced by Colorado AG under consumer protection law; no private right of action created by SB24‑205 itself. Effective date delayed; further changes anticipated. [1], [2], [3] | - Exclusive AG enforcement; civil investigative demands; online complaint mechanism mandated by 9/1/2026; 60‑day cure process. [5]  - DIR sandbox administered by DIR; application by rule. [5], [6]  - No private right of action under HB 149; separate civil/criminal enforcement exists for deepfakes and minors’ exposure. [12], [13] |
| 7) Penalty structures | - Civil penalties under Colorado consumer protection law apply; watch for any implementing rules/guidance pre‑effective date. [1], [2] | - Tiered civil penalties: curable/breach of cure $10,000–$12,000 per violation; uncurable $80,000–$200,000; continuing violations $2,000–$40,000 per day; injunctive relief and fees; professional boards may add sanctions up to $100,000 after an AG violation finding. [5] |
| 8) Effective dates and timelines | - Enacted 2024. The legislature delayed the effective date to June 30, 2026 and signaled that further changes are anticipated before then. Plan programs now with flexibility for amendments and rulemaking. [2], [3], [4] | - HB 149 effective Jan 1, 2026. AG complaint portal due by Sept 1, 2026. Fiscal constraint clause for unfunded mandates on agencies. [5]  - SB 1964, HB 2818, HB 3512 effective Sept 1, 2025 (DIR rules forthcoming). [7], [8], [9] |
| 9) Preemption and interaction | - Integrated with Colorado consumer protection framework; no general municipal AI preemption noted in the bill materials; statewide effect. [1]  - Watch for consistency with federal EO 14110 guidance and NIST AI RMF; Colorado’s approach parallels risk‑management frameworks. [1], [2], [3] | - Express state preemption of local AI ordinances (HB 149 §552.003). [5]  - TDPSA separately preempts local privacy rules; HB 149 amends TDPSA processor clause; HB 149 also amends biometric law (§503.001). [5], [8], [6], [11]  - State public-sector AI regime (SB 1964 et al.) aligns to NIST AI RMF; DIR rulemaking will drive implementation. [7] |
| 10) Definitions and key terms | - SB24‑205 defines “artificial intelligence system,” “high-risk AI system,” and “consequential decision.” See official bill page for authoritative definitions and links to the bill text; final definitions may be affected by 2025 amendments. [1], [2], [3] | - “Artificial intelligence system” (Ch. 551.001). [5]  - “Developer,” “deployer,” and other role terms defined in Ch. 552.001. [5]  - HB 149 amends “biometric identifiers” framework (Tex. Bus. & Com. Code §503.001) for consent/training carve‑outs. [5], [11] |


## Enterprise Compliance Challenges (Concrete Scenarios)

### Colorado SB24-205 (examples to prepare now, ahead of 6/30/2026)
1) Talent selection platform (HR): A resume‑ranking model used as a substantial factor in interview selection triggers “high-risk” obligations: deployer impact assessment pre‑deployment/periodically; consumer notice for consequential decisions; reasons/appeal and human review for adverse outcomes; developer documentation access. Build an HR AI impact assessment, capture feature importances, and ensure human review protocols. [1], [2], [3]

2) Consumer lending underwriting (product/engineering): Credit decisioning models used as a controlling or substantial factor in approvals must undergo pre‑deployment risk assessment and ongoing monitoring for algorithmic discrimination; provide adverse decision explanations and data‑source transparency to applicants; maintain logs and controls. [1], [2], [3]

3) Tenant screening (procurement/vendor): When procuring a third‑party model, require developer model documentation (intended use, known limitations, test metrics), contract flow‑downs, and monitoring hooks to meet deployer duties. [1], [2], [3]

4) Healthcare eligibility triage bot (customer-facing): If the system substantially factors into access to health services, ensure consumer AI interaction disclosure, high‑risk assessment, human review options, and post‑deployment monitoring. [1], [2], [3]

5) Internal IT risk scoring (enterprise ops): Workforce access or fraud risk models affecting employment/discipline require assessments, oversight, and appeal channels if used as a substantial factor; document model purpose, inputs, and controls. [1], [2], [3]

Note: Program design must remain flexible due to the delayed effective date and anticipated amendments. [2], [3], [4]

### Texas HB 149 (“TRAIGA”) and related statutes
1) Product safety for chatbots (product/engineering): Prohibit configurations intended to “incite self-harm, harm to others, or criminal activity.” Maintain red‑team logs and guardrails to evidence non‑intent and leverage safe harbor. [5]

2) Hiring assistant (HR): Avoid intent to unlawfully discriminate. HB 149 requires intent; “a disparate impact is not sufficient by itself” to show intent. Capture decision rationales, red‑team reports, and policy training to demonstrate lack of discriminatory intent and use NIST AI RMF artifacts to support safe harbor. [5]

3) Healthcare AI feature (customer-facing): If used “in relation to health care service or treatment,” disclose AI use to the patient/representative by the first service date (except emergencies). Update EHR/CRM flows, scripting, and templates to capture disclosures. [5]

4) Government sales (procurement/vendor management): Expect SB 1964 RFP requirements for NIST AI RMF alignment, public notices for public-facing AI or AI controlling consequential decisions, testing and complaint‑intake mechanisms; reflect in SOWs and SLAs; provide model documentation and monitoring reports. [7]

5) Data pipelines for model training (privacy/biometrics): Under the amended biometric law, consent cannot be inferred from publicly available images unless posted by the person; AI training “carve‑outs” apply unless used for unique identification; if later used for a commercial purpose, CUBI duties kick in. Inventory biometric sources and restrict repurposing. Effective 1/1/2026. [5], [11]

6) Platform risk for sexual deepfakes (marketing/platform trust): Build 72‑hour takedown workflows, detection tooling, and reporting systems to comply with SB 441 civil duties; implement age verification and source‑consent processes if tools can generate “artificial sexual material harmful to minors” (HB 581). Effective 9/1/2025. [12], [13]

7) Election‑season moderation (policy/trust & safety): Moderate “deep fake video” dissemination within 30 days before an election—criminal offense if intent to deceive/influence; no labeling safe harbor. Implement temporary escalations and filters pre‑election. [14]

8) Processor contracts (IT/procurement): Update TDPSA processor terms to include assistance for personal data “collected, stored, and processed by an AI system,” audit options, and DPA support, effective 1/1/2026. [5], [8]


## Strategic Program Design for Multi-State Operations

- Baseline vs. overlays
  - Baseline: Adopt NIST AI RMF across the AI lifecycle; institutionalize model inventories, use‑case risk classification, pre‑deployment impact assessments for consequential decisions, human oversight, post‑deployment monitoring, incident management, and model documentation—this aligns with Colorado’s process‑centric approach and underpins Texas safe harbors. [7], [5], [1]
  - Overlays:
    - Colorado overlay: High‑risk AI mapping to consequential decisions; deployer assessment timing (pre‑deployment/periodic); consumer notices with adverse decision explanations and human review; developer documentation intake; clear data‑source transparency. Build state‑specific notice and appeal templates. [1], [2], [3]
    - Texas overlay: Implement HB 149 prohibited‑intent controls (policy, training, red‑teaming evidence); healthcare AI disclosure flows; AG documentation readiness; integrate TDPSA processor and DPA obligations; content safety modules for deepfakes/sexual material; implement DIR public‑sector vendor requirements when contracting with agencies. [5], [7], [8], [12], [13], [14]

- Governance and staffing
  - Central AI governance council (Legal, Privacy, Security, ML Engineering, HR, Product, Procurement, Marketing/Trust & Safety, Customer Support) with state‑law SMEs. Use a single model registry tagging each use‑case with “consequential decision,” “public‑facing,” “healthcare,” “election‑season risk,” “sexual content risk,” “government customer” flags. [1], [5], [7], [12], [14]
  - ML model risk committee to approve high‑risk deployments and exceptions; Legal/Privacy to maintain response kits for AG CIDs (HB 149) and for Colorado AG inquiries. [5], [1]

- Budget/resource implications
  - Incremental headcount: AI risk managers, ML auditors, red‑teamers, privacy engineers; external assurance on high‑risk systems; legal budget for Colorado/Texas overlays; content moderation engineering for deepfakes compliance. [1], [5], [12], [13]
  - Tooling: Model documentation, lineage, and governance platforms; adversarial testing frameworks; content authentication/watermarking where helpful (not legally required under HB 149); age verification vendor integrations; DSR/opt‑out systems for TDPSA. [5], [8], [12], [13]

- Monitoring and audits
  - Annual review cycles for high‑risk models; event‑triggered re‑assessments on data/model changes; audit trails for human‑in‑the‑loop decisions; periodic red‑team exercises; complaint intake and remediation pipelines for public‑facing AI (especially for Texas public‑sector work). [1], [7], [5]

- Enforcement risk
  - Colorado: Failure to implement reasonable care, to conduct required impact assessments, or to provide notices/appeal rights in consequential decisions. Given the delayed effective date and anticipated amendments, keep implementation agile but documented. [1], [2], [3], [4]
  - Texas: AG investigations focusing on intent‑based prohibitions; documentation shortfalls; non‑disclosure of healthcare AI use; processor assistance gaps; deepfake content liabilities; data broker overlaps (if applicable). Texas AG has an active privacy enforcement initiative. [5], [15], [16]


## Unsettled/Evolving Issues and Watch-Items

- Colorado SB24-205
  - Effective date delayed to June 30, 2026; the legislature has signaled further changes are anticipated; track new bills amending SB24‑205 and AG rulemaking/guidance. [2], [3], [4]
  - Final definitions, assessment contents, reporting triggers, and enforcement posture may evolve before the effective date; maintain flexible implementation plans and update templates accordingly. [1], [2], [3]

- Texas HB 149 (TRAIGA) and related laws
  - DIR rulemaking for the AI sandbox (HB 149 Ch. 553) and SB 1964 AI Code of Ethics/notice standards pending; monitor DIR for application forms, criteria, and public‑sector AI implementation rules. [5], [6], [7]
  - AG online complaint portal due by Sept 1, 2026; guidance on documentation expectations and use of safe harbors is likely; monitor AG publications. [5]
  - Interplay with TDPSA data protection assessments (profiling producing legal/similarly significant effects) and HB 149’s intent standards; expect AG to leverage TDPSA CIDs to obtain DPAs. [8], [5]
  - Enforcement activity under synthetic media statutes (SB 441; HB 581) will shape platform obligations and safe practices; track cases and AG actions. [12], [13]


## Mapping Obligations to Enterprise Controls and Teams

- Legal/Compliance: Maintain state‑law overlays; update contracts (processor duties, documentation sharing, audit rights); prepare AG CID response kits; oversee DIR public‑sector vendor requirements in Texas; track Colorado amendments. [5], [8], [7], [1], [2]
- Security/IT: Access controls for model artifacts and training data; incident/injury reporting workflows; vulnerability management for prompt injections and jailbreaks; content moderation pipelines (sexual deepfakes/election periods). [12], [14], [5]
- Model Governance/ML Engineering: Model cards; testing/validation; bias and error metrics; human oversight design; post‑deployment monitoring; red‑team exercises supporting safe harbor; impact assessments for consequential decisions. [5], [7], [1]
- Product/UX: Consumer notices (Colorado high‑risk decisions; Texas healthcare AI use; public‑sector notices in Texas); adverse decision explanations; appeal and human review flows. [1], [5], [7]
- HR: Define non‑discriminatory use of AI in hiring/promotion; ensure impact assessments, audit trails, and human review; train HR personnel on disclosures/appeals (Colorado). [1]
- Procurement/Vendor Management: Require developer documentation, testing evidence, safe‑use constraints, data provenance; contract flow‑downs for assessments, logging, incident notification, and AG documentation cooperation. [1], [5], [8], [7]
- Marketing/Customer Support/Trust & Safety: Build deepfake detection/takedown and age‑verification processes; create playbooks for election windows; configure complaint intake for public‑facing AI. [12], [13], [14], [7]


## High-Risk Enforcement Scenarios and Likely Regulator Theories

- Colorado
  - Failure to provide required adverse decision notices and human review for high‑risk AI consequential decisions in employment or credit; lack of a pre‑deployment impact assessment or post‑deployment monitoring demonstrating “reasonable care.” [1], [2], [3]
  - Developer failure to furnish required documentation to deployers leading to deployer noncompliance. [1]

- Texas
  - Intent‑based discrimination allegations tied to internal communications or design documents; absence of red‑team evidence or NIST‑aligned governance to support safe harbor. [5]
  - Failure to disclose healthcare AI use by first service date; missed DIR‑mandated notices in public‑sector deployments. [5], [7]
  - Synthetic media violations: delayed removal of explicit deepfakes; failure to implement age verification for AI tools enabling sexual content harmful to minors; criminal liability for election deepfake videos. [12], [13], [14]
  - TDPSA violations overlapping with AI profiling (lack of DPA; ignoring opt‑outs; weak processor contracts and audits). [8]


## First 90 Days Readiness Checklists

### Colorado SB24-205 (pre‑effective planning)
- Inventory: Tag models and use‑cases that make or substantially factor into consequential decisions (hiring, credit, housing, healthcare, education, insurance, etc.). [1]
- Draft deployer assessments: Pre‑deployment impact assessment templates; define update triggers and annual review cadence. [1]
- Consumer notices: Prepare adverse decision and AI interaction notice templates; design human review/appeal workflows and staffing plans. [1]
- Developer documentation: Build intake process for vendor documentation (intended use, testing metrics, limitations) and contract terms requiring updates; maintain internal model cards. [1]
- Monitoring: Define post‑deployment monitoring, bias checks, incident capture, and remediation playbooks; align to NIST AI RMF for defensibility. [1], [2], [3]
- Watch: Track 2025–2026 amendments and AG guidance to finalize definitions/requirements; keep templates modular. [2], [3], [4]

### Texas HB 149 (TRAIGA) and related measures
- Policy and training: Adopt prohibited‑intent policy; train teams on avoiding discriminatory intent; document red‑team procedures; align to NIST AI RMF (safe harbor). [5], [7]
- Healthcare AI disclosures: Identify features/services involving healthcare AI; implement disclosures by first service date and emergency exceptions; update scripts and patient communications. [5]
- Public-sector sales readiness: Prepare SB 1964‑aligned notices, testing, and complaint intake processes for agency procurement; track DIR rulemaking for sandbox and ethics standards. [7], [6]
- TDPSA alignment: Update processor agreements to include AI‑data assistance; review DPAs for profiling/ADM use‑cases; build AG CID response kits. [8], [5]
- Biometrics: Inventory training data for biometric identifiers; implement consent restrictions and avoid repurposing for unique identification without CUBI compliance; update destruction schedules. Effective 1/1/2026. [11], [5]
- Synthetic media controls: Implement deepfake detection, 72‑hour takedown workflows, reporting channels; deploy age verification for tools that can produce sexual content harmful to minors. Effective 9/1/2025. [12], [13]
- Election readiness: Create an election‑season moderation plan for “deep fake video” within 30 days pre‑election; escalation criteria and legal review. [14]


## Jurisdiction-by-Jurisdiction Strategy

- Where obligations materially diverge
  - Colorado imposes affirmative, negligence‑style duties (reasonable care) with comprehensive assessment/notice/appeal requirements for “high‑risk AI.” [1], [2]
  - Texas focuses on intent‑based prohibitions, limited sectoral disclosures (healthcare), safe harbors, and integration with privacy and biometric statutes; public‑sector AI rules are separate and vendor‑oriented. [5], [7], [8], [11]

- Harmonization approach
  - Build a single NIST AI RMF‑based baseline with mandatory impact assessments for any consequential decisions; add Colorado‑specific consumer notices and appeal rights and Texas‑specific disclosures/record‑keeping and public‑sector contracting modules; maintain a rolling law‑watch to adapt to Colorado amendments and Texas DIR rules. [7], [5], [1], [2], [3]


### Sources
1) Colorado General Assembly — SB24‑205 official bill page: https://leg.colorado.gov/bills/sb24-205  
2) GT Law — Colorado Delays Comprehensive AI Law, With Further Changes Anticipated (Sept. 2025): https://www.gtlaw.com/en/insights/2025/9/colorado-delays-comprehensive-ai-law-with-further-changes-anticipated  
3) National Law Review — Colorado Delays Comprehensive AI Law; Further Changes Anticipated: https://natlawreview.com/article/colorado-delays-comprehensive-ai-law-further-changes-anticipated  
4) GovTech — Colorado Passes Bill Amending Current AI Legislation: https://www.govtech.com/artificial-intelligence/colorado-passes-bill-amending-current-ai-legislation  
5) Texas Legislature Online — HB 149 (89R, 2025) enrolled text (Texas Responsible Artificial Intelligence Governance Act): https://capitol.texas.gov/tlodocs/89R/billtext/html/HB00149F.HTM  
6) Texas DIR — Technology Legislation (updated Aug. 21, 2025): https://dir.texas.gov/technology-legislation  
7) Texas Legislature Online — SB 1964 (89R, 2025) enrolled (Gov’t Code ch. 2054 Subch. S — AI ethics, notices): https://capitol.texas.gov/tlodocs/89R/billtext/html/SB01964F.HTM  
8) Texas Statutes — Business & Commerce Code ch. 541 (Texas Data Privacy and Security Act): https://statutes.capitol.texas.gov/Docs/BC/htm/BC.541.htm  
9) Texas Legislature Online — HB 2818 (89R, 2025) enrolled text (DIR AI Division): https://capitol.texas.gov/tlodocs/89R/billtext/html/HB02818F.htm  
10) Texas Legislature Online — HB 3512 (89R, 2025) enrolled text (AI training for state/local personnel): https://capitol.texas.gov/tlodocs/89R/billtext/html/HB03512F.htm  
11) Texas Statutes — Business & Commerce Code §503.001 (biometric identifiers): https://statutes.capitol.texas.gov/docs/bc/htm/bc.503.htm  
12) Texas Legislature Online — SB 441 (89R, 2025) enrolled (Penal Code §21.165; Civil Practice & Remedies Code ch. 98B amendments): https://capitol.texas.gov/tlodocs/89R/billtext/html/SB00441F.HTM  
13) Texas Legislature Online — HB 581 (89R, 2025) enrolled (CPRC ch. 129B — artificial sexual material harmful to minors): https://capitol.texas.gov/tlodocs/89R/billtext/html/HB00581F.htm  
14) Texas Statutes — Election Code §255.004 (deep fake video law): https://statutes.capitol.texas.gov/docs/el/htm/el.255.htm  
15) Texas Attorney General — Data Privacy & Security Initiative (June 4, 2024): https://www.texasattorneygeneral.gov/news/releases/attorney-general-ken-paxton-launches-data-privacy-and-security-initiative-protect-texans-sensitive  
16) Texas Attorney General — Biometric Identifier Act guidance/complaint page: https://www.texasattorneygeneral.gov/consumer-protection/file-consumer-complaint/consumer-privacy-rights/biometric-identifier-act