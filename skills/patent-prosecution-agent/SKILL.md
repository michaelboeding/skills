---
name: patent-prosecution-agent
description: >
  Use this skill for responding to patent office actions, examiner rejections, and patent prosecution.
  Triggers: "office action", "examiner rejection", "patent rejection", "102 rejection", "103 rejection",
  "101 rejection", "112 rejection", "respond to examiner", "amend claims", "narrow claims",
  "office action response", "patent prosecution", "final rejection", "non-final rejection",
  "restriction requirement", "appeal brief", "PTAB appeal", "RCE", "request for continued examination",
  "after-final amendment", "examiner interview", "claim amendment", "overcome rejection",
  "distinguish prior art", "traverse rejection", "patent response"
  Outputs: Office action analysis, response strategy, amended claims, arguments/remarks, full office action response, appeal brief.
  DISCLAIMER: This is informational only, not legal advice. Consult a licensed patent attorney.
---

# Patent Prosecution Agent

Analyze patent office actions and draft responses to examiner rejections.

**This is a companion skill to `patent-lawyer-agent`.** Use `patent-lawyer-agent` for initial patent drafting and strategy. Use this skill after the USPTO (or other patent office) issues an office action rejecting or objecting to your claims.

**This skill uses 5 specialized agents** that analyze office actions from different perspectives and draft complete responses.

## What It Produces

| Output | Description |
|--------|-------------|
| **Office Action Analysis** | Breakdown of each rejection type, cited references, and affected claims |
| **Response Strategy** | Recommended approach for each rejection (amend, argue, or both) |
| **Amended Claims** | Rewritten claims with proper markup showing additions and deletions |
| **Arguments/Remarks** | Legal arguments distinguishing the invention over cited prior art |
| **Full Response** | Complete office action response document ready for attorney review |
| **Appeal Brief** | PTAB appeal brief for final rejections |

## Prerequisites

- Web access for searching cited prior art references
- `pip install markdown weasyprint` - For PDF generation

## How It Works

**This agent is request-driven.** Tell it what you need and it uses whichever agents are required:

| You Ask | What Happens |
|---------|--------------|
| "I got an office action, help me respond" | Full analysis + strategy + response drafting |
| "Analyze this office action" | Parses rejections, identifies issues, maps claims |
| "How should I respond to this 103 rejection?" | Strategy recommendation for the specific rejection |
| "Amend my claims to overcome this rejection" | Drafts narrowed/amended claims with markup |
| "Write arguments to distinguish over the cited art" | Drafts remarks section with legal arguments |
| "I got a restriction requirement" | Analyzes and recommends claim election |
| "I got a final rejection, what are my options?" | RCE vs appeal vs after-final amendment analysis |
| "Prepare an appeal brief" | Drafts PTAB appeal brief |

**You don't need to follow a rigid workflow.** The agent uses whichever specialized agents are needed for your request.

---

## Request Types

### 1. Full Office Action Response

"I received an office action, help me respond" / "Draft a response to this rejection"

**Use the `AskUserQuestion` tool for each question below.** Do not just print questions in your response — use the tool to create interactive prompts.

**Q1: Office Action**
> "I'll help you respond to this office action!
>
> **First — share the office action details.**
>
> You can:
> - Paste the full office action text
> - Provide a summary of the rejections
> - Upload the office action document
>
> *(Include the rejection types, cited references, and affected claims)*"

*Wait for response.*

**Q2: Your Claims**
> "Now share your **current claims** as filed (or as last amended).
>
> *(Paste the full claim set so I can analyze what the examiner is rejecting)*"

*Wait for response.*

**Q3: Invention Context**
> "Any additional context about your invention?
>
> - What makes your invention different from the cited art?
> - Are there features the examiner may have missed?
> - Any preferred scope you want to maintain?
> - Or say 'none' and I'll work from the claims alone"

*Wait for response.*

**What it does:**
1. Parses and categorizes every rejection in the office action
2. Maps each rejection to affected claims and cited references
3. Develops a response strategy for each rejection
4. Drafts amended claims (if amendments are recommended)
5. Writes arguments/remarks distinguishing over prior art
6. Assembles complete response document

**Uses agents:** Office Action Analyzer, Prosecution Strategist, Claim Amendment Drafter, Argument Writer, Prior Art Distinguisher

**Output:** Complete office action response in Markdown + PDF

---

### 2. Office Action Analysis Only

"Analyze this office action" / "What is the examiner saying?"

**What it does:**
1. Parses the office action into structured components
2. Categorizes each rejection by type (101, 102, 103, 112)
3. Identifies cited prior art references
4. Maps rejections to specific claims
5. Highlights the examiner's key reasoning
6. Identifies the strongest and weakest rejections

**Uses agents:** Office Action Analyzer

---

### 3. Response Strategy

"How should I respond to this rejection?" / "What's the best strategy here?"

**What it does:**
1. Analyzes the rejection(s)
2. Evaluates strength of examiner's position
3. Recommends for each rejection: amend, argue, or both
4. Identifies which claim limitations to add or modify
5. Assesses risk of each strategy option
6. Recommends prosecution timeline

**Uses agents:** Office Action Analyzer, Prosecution Strategist

---

### 4. Draft Amended Claims

"Amend my claims to overcome this rejection" / "Narrow my claims"

**What it does:**
1. Analyzes what the examiner requires
2. Identifies minimum narrowing needed to overcome rejection
3. Drafts amended claims with proper markup:
   - ~~Strikethrough~~ for deleted text
   - **Underline** for added text
4. Preserves maximum scope while overcoming rejection
5. Maintains proper claim dependency chain
6. Explains rationale for each amendment

**Uses agents:** Office Action Analyzer, Prosecution Strategist, Claim Amendment Drafter

---

### 5. Arguments/Remarks Only

"Write arguments distinguishing my invention over the cited art" / "Help me argue against this rejection"

**What it does:**
1. Analyzes the cited prior art references
2. Identifies meaningful differences from the invention
3. Constructs legal arguments for each rejection type:
   - **102**: Shows missing elements in cited reference
   - **103**: Argues against motivation to combine / teaches away
   - **101**: Argues practical application / technical improvement
   - **112**: Clarifies specification support
4. Drafts formal remarks section

**Uses agents:** Prior Art Distinguisher, Argument Writer

---

### 6. Restriction Requirement Response

"I got a restriction requirement" / "The examiner wants me to elect claims"

**Use the `AskUserQuestion` tool for each question below.**

**Q1: Restriction Details**
> "Share the **restriction requirement** details.
>
> *(Which groups did the examiner identify? Which claims are in each group?)*"

*Wait for response.*

**Q2: Business Priority**
> "What's most important to your business?
>
> - Broadest method protection
> - Specific apparatus/device claims
> - System-level claims
> - Or describe your priority"

*Wait for response.*

**What it does:**
1. Analyzes the examiner's restriction groupings
2. Evaluates the scope and value of each group
3. Recommends which group to elect
4. Drafts election response with traverse (if appropriate)
5. Notes divisional filing opportunities for non-elected groups

**Uses agents:** Office Action Analyzer, Prosecution Strategist

---

### 7. Final Rejection Response

"I got a final rejection" / "What are my options after final rejection?"

**What it does:**
1. Analyzes the final rejection
2. Evaluates three paths:
   - **After-Final Amendment** (narrow, low cost, limited scope)
   - **RCE** (restart prosecution, new arguments, additional cost)
   - **Appeal to PTAB** (challenge examiner, higher cost, longer timeline)
3. Recommends best path based on rejection strength and claim value
4. Drafts the chosen response document

**Uses agents:** Office Action Analyzer, Prosecution Strategist, Claim Amendment Drafter, Argument Writer

---

### 8. Appeal Brief Preparation

"Prepare an appeal brief" / "I want to appeal to the PTAB"

**Use the `AskUserQuestion` tool for each question below.**

**Q1: Prosecution History**
> "Share the **prosecution history** for this appeal:
>
> - The original claims
> - The examiner's rejections (all office actions)
> - Any amendments already made
> - The final rejection
>
> *(The more history you provide, the stronger the brief)*"

*Wait for response.*

**Q2: Key Arguments**
> "What are the **strongest arguments** you believe support patentability?
>
> - Key differences from cited art
> - Examiner errors in reasoning
> - Mischaracterization of references
> - Or say 'help me identify them'"

*Wait for response.*

**What it does:**
1. Reviews full prosecution history
2. Identifies examiner errors and weak reasoning
3. Constructs legal arguments organized by claim grouping
4. Drafts appeal brief following PTAB format:
   - Statement of Real Party in Interest
   - Related Proceedings
   - Statement of Status of Claims
   - Statement of Status of Amendments
   - Summary of Claimed Subject Matter
   - Argument (organized by rejection/claim grouping)
   - Claims Appendix

**Uses agents:** All 5 agents

**Output:** Appeal brief in Markdown + PDF

---

## Specialized Agents

Each agent has a specific focus. The skill uses whichever are needed:

| Agent | What It Does |
|-------|--------------|
| **Office Action Analyzer** | Parses office actions, categorizes rejections, maps claims to references |
| **Prosecution Strategist** | Develops response strategy, recommends amend vs argue vs both |
| **Claim Amendment Drafter** | Rewrites claims with proper amendment markup |
| **Argument Writer** | Drafts legal arguments and remarks distinguishing over prior art |
| **Prior Art Distinguisher** | Deep analysis of cited references, finds meaningful differences |

---

## Output Formats

### Office Action Analysis
```json
{
  "office_action_type": "Non-Final/Final/Restriction/Advisory",
  "mailing_date": "YYYY-MM-DD",
  "response_deadline": "YYYY-MM-DD (3 months, extendable to 6)",
  "rejections": [
    {
      "type": "102/103/101/112",
      "statutory_basis": "35 U.S.C. 103",
      "affected_claims": [1, 2, 3],
      "cited_references": ["Reference 1", "Reference 2"],
      "examiner_reasoning": "Summary of examiner's position",
      "strength": "Strong/Moderate/Weak"
    }
  ],
  "objections": ["Objection 1"],
  "claim_status": {
    "rejected": [1, 2, 3],
    "objected": [],
    "allowed": [],
    "withdrawn": []
  },
  "key_issues": ["Issue 1", "Issue 2"],
  "recommended_priority": "Which rejections to address first"
}
```

### Full Office Action Response
Complete response document with all sections (Remarks, Amended Claims, Arguments) in Markdown format.

**Output files:**
- `office_action_response.pdf` - Final PDF for attorney review
- `office_action_response.md` - Editable source document

---

## Integration with Other Skills

| Skill | Use Case |
|-------|----------|
| `patent-lawyer-agent` | **Original patent drafting** (use before this skill) |
| `patent-lawyer-agent` (Prior Art Searcher) | Search for additional prior art to support arguments |
| `patent-lawyer-agent` (Claims Strategist) | Cross-reference original claim strategy |

---

## Agent Files

| Agent | File |
|-------|------|
| Office Action Analyzer | `agents/office-action-analyzer.md` |
| Prosecution Strategist | `agents/prosecution-strategist.md` |
| Claim Amendment Drafter | `agents/claim-amendment-drafter.md` |
| Argument Writer | `agents/argument-writer.md` |
| Prior Art Distinguisher | `agents/prior-art-distinguisher.md` |

---

## Important Limitations

1. **Not Legal Advice** - This is informational guidance only
2. **Not a Substitute for an Attorney** - Patent prosecution requires licensed counsel
3. **No Attorney-Client Privilege** - Conversations are not privileged
4. **Deadline Sensitivity** - Always verify response deadlines with the actual office action
5. **Jurisdiction Specific** - Primarily focused on USPTO practice; other offices may differ
6. **Laws Change** - Patent law, examination guidelines, and case law evolve over time
7. **No Filing Capability** - This drafts responses but cannot file them with the USPTO

**Always have a licensed patent attorney review and file any office action response.**

---

## Example Prompts

**Full office action response:**
> "I received a non-final office action rejecting claims 1-15 under 103. Help me draft a response."

**Analyze a rejection:**
> "The examiner rejected my claims under 102(a)(1) based on US Patent 10,123,456. Analyze this rejection."

**Amend claims:**
> "My independent claim 1 was rejected under 103 as obvious. Help me narrow it to overcome the rejection while keeping maximum scope."

**Argue without amending:**
> "I think the examiner misread the cited reference. Help me write arguments showing why my claim is different."

**103 obviousness response:**
> "The examiner combined three references to reject my claims. Help me argue there's no motivation to combine."

**101 subject matter eligibility:**
> "My software patent claims were rejected under 101 as abstract ideas. Help me argue they recite a practical application."

**112 rejection:**
> "The examiner says my claims lack written description support. Help me point to the specification support."

**Restriction requirement:**
> "I got a restriction requirement splitting my claims into 3 groups. Which group should I elect?"

**Final rejection options:**
> "I just got a final rejection. Should I file an RCE, appeal, or try an after-final amendment?"

**Appeal brief:**
> "The examiner maintains the 103 rejection after my amendment. I want to appeal to the PTAB."

**Strategy question:**
> "Is it worth fighting this 102 rejection or should I just narrow my claims?"
