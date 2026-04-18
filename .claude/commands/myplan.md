# MyPlan Command (Repo)

## Communication Protocol

- Be direct and matter-of-fact. No flattery, no preamble, no "Great question!"
- If reasoning is flawed, say so immediately with specific evidence
- Don't fold arguments on pushback — maintain position unless new evidence is presented
- Lead with concerns before agreement
- When you agree, explain WHY with specific reasoning — not just validation

Analyze, design, and create implementation plan for a task

## Usage

```bash
/myplan [task-slug]
```

## Arguments

- `task-slug`: Task identifier from TODO.md `[task:: slug]` field
  - Example: `wifi-bt-wakeup-check`, `secure-boot`, `thread-동작-체크`
  - Find it in vault TODO.md: look for `🏷️ {slug}` as sub-item
  - Must match exactly (case-sensitive)

## Implementation

You are an implementation planner working in a project repository. Follow these steps:

1. **Load Configuration**
   ```bash
   source {vault-path}/.claude/hooks/lib/sync-todo.sh
   vault_path=$(get_vault_path)
   project=$(get_project_name)
   ```

2. **Validate Agent System (Optional but Recommended)**
   ```bash
   # Source agent validator library
   if [[ -f ".claude/hooks/lib/agent-validator.sh" ]]; then
       source .claude/hooks/lib/agent-validator.sh
   elif [[ -f "${vault_path}/.claude/hooks/lib/agent-validator.sh" ]]; then
       source "${vault_path}/.claude/hooks/lib/agent-validator.sh"
   fi

   # Note: /myplan can work without reviewer agent, but it's recommended
   # Uncomment to enforce:
   # require_multiagent_system "myplan" "reviewer"
   ```

3. **Find Task in TODO**
   - Read `${vault_path}/TODO.md`
   - Find task under project section matching task-name
   - Extract task description, priority, due date

4. **🔍 Knowledge Retrieval (MANDATORY)**

   Before creating a new plan, ALWAYS search for prior relevant work:

   **Step 4.1: Search for Similar Plans**
   ```bash
   # Find plans with similar keywords from task description
   Grep "{key-terms-from-task}" --glob "${vault_path}/work-docs/**/plans/*.md"
   ```

   **Step 4.2: Find Related Sessions (Past Solutions)**
   ```bash
   # Search for sessions that solved similar problems
   Grep "{problem-keywords}" --glob "${vault_path}/work-docs/**/sessions/*.md"
   ```

   **Step 4.3: Check for Prior Decisions**
   ```bash
   # Look for architectural decisions on this topic
   Grep "{topic}" --glob "${vault_path}/work-docs/**/DECISION-*.md" "${vault_path}/work-docs/**/REVIEW-*.md"
   ```

   **Step 4.4: Query Index for Related Docs**
   ```bash
   # Query RAG index for documents with matching tags/project
   jq '.documents | to_entries[] | select(.value.project == "{project}" and (.value.tags | any(. == "{relevant-tag}")))' ${vault_path}/.claude/rag/index.json
   ```

   **Step 4.5: Follow Links (Graph Traversal)**
   - If relevant documents found, read them
   - Extract [[wiki-links]] from their content
   - Read linked documents for deeper context (max 2-3 hops)

   **Step 4.6: Synthesize Findings**
   Create a "Prior Work" section for the PLAN including:
   - What similar work was done before?
   - What approaches worked/failed?
   - What decisions were made and why?
   - What blockers were encountered?

   **Step 4.7: Auto-Suggest Related Documents**
   ```bash
   # Use suggest-related.sh to find related documents for frontmatter
   source "${vault_path}/.claude/hooks/lib/suggest-related.sh"

   # Get suggested related links (will be used in frontmatter)
   RELATED_LINKS=$(suggest_for_plan "${vault_path}" "${project}" "${task_slug}" "${primary_tags[@]}")
   ```

   This automatically populates the `related` field with:
   - Documents with same task_slug (prior PLAN/SESSION/WRAPUP)
   - Project context docs (TECH_SPEC, MASTER_PLAN)
   - Documents with similar tags

5. **Phase 1: Review & Context Analysis**
   - **Understand the Problem**
     - What needs to be done?
     - Why is this needed?
     - What are the acceptance criteria?

   - **Code Review**
     - Read relevant files
     - Understand current implementation
     - Identify affected components

   - **Constraints & Dependencies**
     - Technical constraints
     - Dependencies on other tasks/systems
     - Timeline and priority

5. **Phase 2: Technical Design**
   - **Architecture**
     - Component changes needed
     - Data flow
     - API changes

   - **Design Decisions**
     - Why this approach?
     - What alternatives were considered?
     - Trade-offs

   - **Risk Assessment**
     - What could go wrong?
     - How to mitigate?

6. **Phase 3: Implementation Plan**
   - **Break into Phases**
     - Phase 1: Core implementation
     - Phase 2: Testing
     - Phase 3: Integration
     - etc.

   - **File Changes**
     - List files to modify/create
     - Specific changes per file

   - **Testing Strategy**
     - Unit tests needed
     - Integration tests
     - Manual testing steps

   - **Success Criteria**
     - How to verify it works?
     - Performance benchmarks if applicable

7. **Generate PLAN Document**
   Save to: `${vault_path}/work-docs/${project}/plans/PLAN-${task-slug}.md`

   **Important:**
   - Create `${vault_path}/work-docs/${project}/plans/` directory if it doesn't exist
   - Use task-slug (not task-name) for filename
   - Document will be visible in Obsidian vault
   - **MUST include YAML frontmatter** for RAG indexing

   ```markdown
   ---
   type: plan
   project: {project}
   task_slug: {task-slug}
   status: planning
   created: {YYYY-MM-DD}
   tags: [{generated-tags}]
   related:
     # AUTO-POPULATED from Step 4.7 suggest-related.sh output
     - "[[work-docs/{project}/context/TECH_SPEC]]"
     - "[[work-docs/{project}/context/MASTER_PLAN]]"
     # Add more from RELATED_LINKS variable
   summary: "{AUTO: Extract from TL;DR in Executive Summary section}"
   ---
   ```

   **Summary Generation (AUTO):**
   - Extract the TL;DR sentence from "## 🎯 Executive Summary" section
   - Keep it under 100 characters
   - Example: "Implement MQTT retry logic with exponential backoff for weather data ingestion"

   **Related Links (AUTO from suggest-related.sh):**
   - Run `suggest_for_plan` from Step 4.7
   - Include all suggested links in the `related` field
   - At minimum: TECH_SPEC, MASTER_PLAN, any prior related documents

   **Tag Generation (MANDATORY - LLM Required):**

   **MUST include at minimum:**
   1. **Project tag**: The project name (e.g., `edge-ai`, `uniep`, `bsp`, `checkup`)
   2. **Document type**: Always include `plan` for PLAN documents
   3. **Primary tech stack**: At least one (e.g., `python`, `c`, `cpp`, `typescript`)

   **SHOULD include 2-5 additional tags from:**
   - **Domain**: `ess`, `ems`, `embedded`, `iot`, `security`, `matter`, `cyber-security`
   - **Technologies**: `mqtt`, `docker`, `yocto`, `sqlite`, `ipc`, `bootloader`, `kernel`
   - **Topics**: `testing`, `performance`, `optimization`, `documentation`, `process`
   - **Activities**: `refactoring`, `integration`, `deployment`, `factory-test`, `firmware-update`

   **Standard tag vocabulary (prefer these over creating new tags):**
   - Languages: `python`, `c`, `cpp`, `typescript`, `rust`, `go`
   - Infrastructure: `embedded`, `bootloader`, `kernel`, `storage`, `networking`
   - Domains: `ess`, `ems`, `matter`, `bsp`, `uniep`, `checkup`
   - Tools: `yocto`, `docker`, `mqtt`, `ipc`, `sqlite`, `pytest`, `cvxpy`
   - Topics: `security`, `testing`, `performance`, `optimization`, `observability`

   **Target:** 5-8 tags total (minimum 3: project + type + tech-stack)

   **Examples:**
   - ✅ GOOD: `[edge-ai, plan, python, ess, forecasting, optimization, testing]` (7 tags, specific, from vocabulary)
   - ✅ GOOD: `[uniep, plan, c, mqtt, ipc, system]` (6 tags, concise, relevant)
   - ❌ BAD: `[plan, important, L75, define]` (meaningless, not from vocabulary)
   - ❌ BAD: `[edge-ai]` (too few, missing tech-stack and type)

   ```markdown

   # PLAN: {Task Name}

   **Project:** {project}
   **Task:** {full-description}
   **Priority:** {priority}
   **Due:** {due-date}
   **Created:** {timestamp}

   ---

   ## 🎯 Executive Summary

   > **TL;DR:** {One-sentence summary of what this task accomplishes}

   ### What We're Doing
   {2-3 sentences: The core change being made}

   ### Why It Matters
   {1-2 sentences: Business/technical value}

   ### Key Decisions
   - **Decision 1:** {Brief description} - Chosen because {reason}
   - **Decision 2:** {Brief description} - Chosen because {reason}

   ### Estimated Impact
   - **Complexity:** Low | Medium | High
   - **Risk Level:** Low | Medium | High
   - **Files Changed:** ~N files
   - **Estimated Time:** X hours

   ---

   ## ⚠️ REVIEW CHECKLIST - Action Required

   > **📌 These items require your explicit verification before /execute**

   ### Critical Decisions to Verify
   - [ ] **Architecture:** Is the proposed component design correct?
   - [ ] **API Changes:** Are the proposed API changes backward compatible?
   - [ ] **Security:** Have security implications been considered?
   - [ ] **Performance:** Will this meet performance requirements?

   ### Code Impact to Review
   - [ ] **File: {critical-file-1}** - Verify {what to check}
   - [ ] **File: {critical-file-2}** - Verify {what to check}
   - [ ] **Dependencies:** Check if new dependencies are acceptable

   ### Testing Coverage
   - [ ] Are all edge cases covered in the test plan?
   - [ ] Do we need additional integration tests?
   - [ ] Is manual testing scope sufficient?

   ### Business Logic
   - [ ] Does this match the acceptance criteria?
   - [ ] Are there any missed requirements?
   - [ ] Should we break this into smaller tasks?

   **✋ Stop here if ANY checkbox is unclear - ask questions before proceeding!**

   ---

   ## 📚 Prior Work (Knowledge Retrieval)

   > **Based on knowledge base search - include relevant findings here**

   ### Related Documents Found
   - [[work-docs/{project}/plans/PLAN-related-task]] - {why it's relevant}
   - [[work-docs/{project}/sessions/SESSION-related-task-YYYY-MM-DD]] - {key insight}

   ### What Worked Before
   {Summary of successful approaches from prior work}

   ### Known Blockers & Solutions
   {Blockers encountered in similar tasks and how they were resolved}

   ### Decisions to Reuse/Reconsider
   {Prior architectural decisions relevant to this task}

   ---

   ## 📋 Problem Analysis

   ### What
   {What needs to be done}

   ### Why
   {Why this is needed}

   ### Success Criteria
   - [ ] Criterion 1
   - [ ] Criterion 2

   ---

   ## 🔍 Code Review

   ### Current State
   {Current implementation review}

   ### Affected Components
   - Component 1: {file-path}
   - Component 2: {file-path}

   ### Dependencies
   - Dependency 1
   - Dependency 2

   ---

   ## 🏗️ Technical Design

   ### Architecture
   {Design overview}

   ### Design Decisions
   1. **Decision:** {description}
      - **Rationale:** {why}
      - **Alternatives:** {what else was considered}

   ### Data Flow
   {How data flows through the system}

   ### API Changes
   {If applicable}

   ---

   ## 📝 Implementation Plan

   ### Phase 1: Core Implementation
   - [ ] Task 1 - {file}: {changes}
   - [ ] Task 2 - {file}: {changes}

   ### Phase 2: Testing
   - [ ] Unit tests for X
   - [ ] Integration tests for Y

   ### Phase 3: Integration
   - [ ] Integrate with component A
   - [ ] Update documentation

   ---

   ## 🧪 Testing Strategy

   ### Unit Tests
   - Test case 1
   - Test case 2

   ### Integration Tests
   - Scenario 1
   - Scenario 2

   ### Manual Testing
   1. Step 1
   2. Step 2

   ---

   ## ⚠️ Risks & Mitigation

   | Risk | Impact | Mitigation |
   |------|--------|------------|
   | Risk 1 | High | Mitigation strategy |

   ---

   ## ✅ Success Criteria

   - [ ] Functional requirement 1
   - [ ] Functional requirement 2
   - [ ] Performance: {benchmark}
   - [ ] Tests pass
   - [ ] Documentation updated

   ---

   ## 📊 Estimated Effort

   - **Complexity:** Low | Medium | High
   - **Estimated Time:** X hours
   - **Files Changed:** ~N files

   ```

8. **Sync to Vault TODO**
   ```bash
   sync_todo_update "plan" "${task-slug}" "work-docs/${project}/plans/PLAN-${task-slug}.md"
   ```

9. **Update RAG Index**
   ```bash
   # Run janitor to update RAG index with new PLAN document
   if command -v python3 &> /dev/null; then
       python3 "${vault_path}/.claude/rag/janitor.py" --project "${project}" 2>/dev/null || true
   fi
   ```

10. **Output Summary**
   ```markdown
   ## ✅ Plan Created

   **Task:** {task-slug}
   **Document:** PLAN-{task-slug}.md

   ## 📁 Location (Visible in Obsidian)
   - {vault-path}/work-docs/{project}/plans/PLAN-{task-slug}.md
   - Open in Obsidian: [[work-docs/{project}/plans/PLAN-{task-slug}]]

   ## 🎯 Executive Summary

   **TL;DR:** {One-sentence summary}

   **Complexity:** {level}
   **Risk Level:** {level}
   **Estimated Effort:** {hours} hours
   **Files to Change:** {count}

   ## ⚠️ YOUR ACTION REQUIRED

   **📌 Review Checklist:** The PLAN includes a highlighted checklist of critical items you MUST verify:

   - Critical Decisions (Architecture, API, Security, Performance)
   - Code Impact (Specific files to review)
   - Testing Coverage (Edge cases, integration tests)
   - Business Logic (Acceptance criteria, requirements)

   **✋ DO NOT run /execute until you've checked all review items!**

   ## ➡️ Next Steps

   1. **REVIEW FIRST:** Open PLAN-{task-slug}.md
   2. **Check the "⚠️ REVIEW CHECKLIST" section** - Verify each item
   3. **Ask questions** if anything is unclear
   4. **Check vault TODO.md** (task status → planning, PLAN link added)
   5. **When ready:** `/execute {task-slug}`
   ```

## Important Notes

- This combines review + design + planning into ONE command
- Creates ONE comprehensive PLAN document with:
  - **🎯 Executive Summary** - Quick overview for stakeholder review
  - **⚠️ Review Checklist** - Highlighted items requiring user verification
  - Detailed analysis and implementation phases
- Auto-updates vault TODO.md with:
  - PLAN document link
  - Status: planning
  - Updated timestamp
- Should complete in 5-10 minutes depending on complexity
- Use code reading tools extensively - understand before planning
- **Key Feature:** The review checklist ensures critical decisions are explicitly verified before execution

## Error Handling

- If task not found in TODO: List tasks and ask for clarification
- If obsidian.json missing: Show setup instructions
- If vault path inaccessible: Show error with path
- If PLAN already exists: Ask to overwrite or append
