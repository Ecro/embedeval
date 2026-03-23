# Execute Command (Repo)

Implement and test based on the plan

## Usage

```bash
/execute [task-slug]
```

## Arguments

- `task-slug`: Task identifier from TODO.md `[task:: slug]` field (must match existing PLAN document)
  - Example: `wifi-bt-wakeup-check`, `secure-boot`, `thread-동작-체크`
  - Must have run `/myplan [task-slug]` first
  - Must match exactly (case-sensitive)

## Implementation

You are an implementation executor working in a project repository. Follow these steps:

1. **Load Configuration**
   ```bash
   source {vault-path}/.claude/hooks/lib/sync-todo.sh
   vault_path=$(get_vault_path)
   project=$(get_project_name)
   ```

2. **Validate Agent System**
   ```bash
   # Source agent validator library
   if [[ -f ".claude/hooks/lib/agent-validator.sh" ]]; then
       source .claude/hooks/lib/agent-validator.sh
   elif [[ -f "${vault_path}/.claude/hooks/lib/agent-validator.sh" ]]; then
       source "${vault_path}/.claude/hooks/lib/agent-validator.sh"
   else
       echo "Error: agent-validator.sh not found" >&2
       exit 1
   fi

   # Enforce required agents for /execute
   require_multiagent_system "execute" "coder" "tester" "stuck"
   ```

3. **Load PLAN Document**
   - Read `${vault_path}/work-docs/${project}/plans/PLAN-${task-slug}.md`
   - If not found: Error - must run `/myplan {task-slug}` first
   - Extract:
     - Implementation phases
     - Files to modify
     - Success criteria
     - Testing strategy

4. **🔍 Knowledge Retrieval for Solutions (MANDATORY)**

   Before implementing, search for solutions to similar problems:

   **Step 4.1: Find Related SESSION Documents**
   ```bash
   # Search for sessions that implemented similar features
   Grep "{key-implementation-terms}" --glob "${vault_path}/work-docs/**/sessions/*.md"
   ```

   **Step 4.2: Search for Known Blockers & Solutions**
   ```bash
   # Find past blockers and how they were resolved
   Grep "blocker\|blocked\|issue\|error\|fixed\|resolved" --glob "${vault_path}/work-docs/**/SESSION-*.md"
   ```

   **Step 4.3: Find Code Patterns Used Before**
   ```bash
   # Search for similar implementation patterns
   Grep "{technology-or-pattern}" --glob "${vault_path}/work-docs/**/SESSION-*.md" "${vault_path}/work-docs/**/WRAPUP-*.md"
   ```

   **Step 4.4: Check LEARNING Documents**
   ```bash
   # Find accumulated learnings on this topic
   Grep "{topic}" --glob "${vault_path}/knowledge-base/learnings/**/*.md"
   ```

   **Step 4.5: Synthesize Before Implementation**
   - What solutions worked for similar problems?
   - What pitfalls to avoid?
   - What patterns to follow?
   - Include key findings in SESSION document under "Prior Knowledge Applied"

   **Step 4.6: Auto-Suggest Related Documents**
   ```bash
   # Use suggest-related.sh to find related documents for frontmatter
   source "${vault_path}/.claude/hooks/lib/suggest-related.sh"

   # Get suggested related links for SESSION (includes PLAN automatically)
   RELATED_LINKS=$(suggest_for_session "${vault_path}" "${project}" "${task_slug}" "${primary_tags[@]}")
   ```

   This automatically populates the `related` field with:
   - The PLAN document for this task (always included)
   - Project context docs (TECH_SPEC, MASTER_PLAN)
   - Related SESSION documents with similar tags

5. **🔗 Context7 Auto-Query (Library Documentation)**

   Before implementation, automatically fetch documentation for external libraries.

   ### When to Query Context7

   Query Context7 when the task involves:
   - External libraries not previously used in the project
   - Libraries with version-specific APIs (e.g., React 18 vs 17)
   - Complex frameworks requiring specific patterns (e.g., Next.js, FastAPI)
   - Libraries where official docs differ from common tutorials

   ### Dependency Detection

   1. **Scan files to modify for imports:**
      ```bash
      # Detect import statements in affected files
      Grep "import|require|from|use" in files from PLAN
      ```

   2. **Identify libraries needing documentation:**
      - Libraries not in project's existing dependencies
      - Libraries without cached documentation in `external-refs/`
      - Libraries mentioned in PLAN that may have API changes

   3. **Auto-query Context7:**
      ```
      For each unknown/complex library:

      # Step 1: Resolve library ID
      mcp__context7__resolve-library-id(
        libraryName="{library}",
        query="{what we need from this library}"
      )

      # Step 2: Query specific documentation
      mcp__context7__query-docs(
        libraryId="{resolved-id}",
        query="{specific API or pattern needed}"
      )
      ```

   4. **Cache results (optional):**
      - Save to: `work-docs/{project}/external-refs/frameworks/{library}.md`
      - Use template: `99_Meta/templates/external-ref-framework.md`
      - Include: API patterns, best practices, gotchas

   ### Graceful Fallback

   **Error Detection:**
   Context7 may fail in several ways - handle each appropriately:

   | Error Type | Detection | Action |
   |------------|-----------|--------|
   | MCP Unavailable | Tool call fails/times out | Use native knowledge |
   | Rate Limited | 429 response or rate limit error | Use cache if available, else native |
   | Partial Results | Query succeeds but incomplete | Use what's available + native |
   | Library Not Found | resolve-library-id returns empty | Skip library, use native |

   **Fallback Strategy:**
   1. **Check cache first:** If `external-refs/{library}.md` exists and is <7 days old, use it
   2. **Query Context7:** Single attempt per library (no retries)
   3. **On any failure:** Fall back to Claude's native knowledge
   4. **Never block:** Context7 is advisory, not required - execution continues

   **No Retry Logic:**
   - Do NOT retry Context7 queries on failure
   - Single attempt per library, then fallback
   - Prevents timeout cascades in background execution

   **SESSION Document Marking:**
   Mark Context7 status in SESSION document:
   ```markdown
   ## Context7 Status
   - fastapi: ✅ Fetched (cached)
   - pydantic: ✅ Fetched (live query)
   - unknown-lib: ⚠️ Not found, using native knowledge
   - rate-limited-lib: ⚠️ Rate limited, using native knowledge
   ```

   If Context7 completely unavailable:
   - Log warning: "Context7 unavailable, using native knowledge"
   - Continue with Claude's built-in knowledge
   - Mark in SESSION doc: "External docs: Not fetched (MCP unavailable)"

   ### Skip Conditions

   Skip Context7 for:
   - **Standard library imports:** `os`, `sys`, `path`, `fs`, `util`, etc.
   - **Project-internal imports:** Imports from within the same codebase
   - **Already cached libraries:** If `external-refs/{library}.md` exists and is <7 days old
   - **Trivial libraries:** Simple utilities that don't need reference docs
   - **Non-code tasks:** Documentation, configuration, or refactoring only

   ### Example Usage

   ```markdown
   ## Context7 Documentation Fetched

   | Library | Query | Source |
   |---------|-------|--------|
   | fastapi | "dependency injection patterns" | /tiangolo/fastapi |
   | pydantic | "model validation with custom types" | /pydantic/pydantic |

   **Cached to:** work-docs/edge-ai/external-refs/frameworks/
   ```

6. **Implementation Process**
   Use multi-agent orchestration (coder + tester):

   **For each implementation phase:**

   a) **Invoke CODER Agent**
      ```
      Task(
        subagent_type="coder",
        description="{phase-description}",
        prompt="{detailed phase context from PLAN}"
      )
      ```

   b) **CODER Completes → Auto-invoke TESTER**
      ```
      Task(
        subagent_type="tester",
        description="Validate {phase}",
        prompt="{success criteria from PLAN}"
      )
      ```

   c) **TESTER Result:**
      - PASS: Continue to next phase
      - FAIL: Invoke STUCK agent → User decides

## Checkpoint & Recovery

Claude Code 2.0 automatically creates checkpoints before significant changes.

### Recovery Options

| Trigger | How | Result |
|---------|-----|--------|
| Quick Rewind | Press `Esc` twice | Opens rewind interface |
| Command Rewind | Type `/rewind` | Select checkpoint to restore |

### Restore Choices
- **Code only**: Restore files without affecting conversation
- **Conversation only**: Restore conversation without affecting files
- **Both**: Full restoration to previous state

### When to Use Checkpoints

Use checkpoint recovery when:
- TESTER validation fails and approach needs revision
- Phase implementation goes wrong unexpectedly
- Before attempting risky refactoring within a phase
- After agent produces unexpected results

### SESSION Document Integration

When using checkpoints during execution:
1. Record checkpoint usage in SESSION document under "Recovery Actions" section
2. Note which checkpoint was used and why
3. Document what was restored and the outcome

**Example SESSION entry:**
```markdown
## 🔄 Recovery Actions

| Time | Checkpoint | Reason | Restored |
|------|------------|--------|----------|
| 14:30 | Pre-Phase-2 | TESTER failed, wrong approach | Code only |
| 15:45 | Pre-Refactor | Unexpected side effects | Both |
```

## Parallel Execution Pattern

Claude Code 2.0 supports parallel agent invocation for independent tasks without data dependencies.

### Sequential vs Parallel

**Sequential (Default - Required for Validation)**
```
CODER → wait → TESTER → wait → Next phase
```
This is **mandatory** for implementation phases where TESTER validates CODER output.

**Parallel (When Safe)**
```
CODER completes → [TESTER + DOC_GENERATOR] parallel → Next phase
```
Use when multiple agents can work on CODER output simultaneously without conflicts.

### Safe Parallel Combinations

| Agent 1 | Agent 2 | Safe? | Rationale |
|---------|---------|-------|-----------|
| TESTER | DOC_GENERATOR | ✅ | Both read-only analysis of CODER output |
| REVIEWER | DOC_GENERATOR | ✅ | Independent analysis tasks |
| CODER | CODER | ❌ | File modification conflicts |
| TESTER | TESTER | ❌ | Redundant, wasteful |
| REVIEWER | REVIEWER | ❌ | Redundant, wasteful |
| CODER | TESTER | ❌ | TESTER needs CODER output first |

### Implementation Guidance

**When to use parallel:**
1. After CODER completes, if both testing AND documentation needed
2. For independent review tasks on separate file sets
3. For parallel analysis of different code areas

**How to invoke parallel agents:**
```
Task(
  subagent_type="tester",
  description="Validate Phase 1",
  prompt="..."
)
Task(
  subagent_type="doc_generator",
  description="Update docs for Phase 1",
  prompt="..."
)
// Both invoked in same message = parallel execution
```

**Critical rule:** CODER → TESTER validation cycle remains **sequential and mandatory**. Never skip TESTER validation by running CODER in parallel with anything else.

### Parallel Execution in SESSION Document

When using parallel execution, document in SESSION:
```markdown
## 🔀 Parallel Execution Log

### Phase 2: Post-Implementation
**Parallel Agents:** TESTER + DOC_GENERATOR
**Duration:** 3m (vs 5m sequential)
**Results:** Both passed independently
```

7. **Track Progress**
   Use TodoWrite to track implementation phases:
   ```
   TodoWrite([
     {content: "Phase 1: Core implementation", status: "in_progress"},
     {content: "Phase 2: Testing", status: "pending"},
     {content: "Phase 3: Integration", status: "pending"}
   ])
   ```

8. **Document Changes**
   During execution, log:
   - Files modified
   - Key decisions made
   - Issues encountered
   - Solutions applied

9. **Generate SESSION Document**
   Save to: `${vault_path}/work-docs/${project}/sessions/SESSION-${task-slug}-${date}.md`

   **Important:**
   - Create `${vault_path}/work-docs/${project}/sessions/` directory if it doesn't exist
   - Use task-slug (not task-name) for filename
   - Document will be visible in Obsidian vault
   - **MUST include YAML frontmatter** for RAG indexing

   ```markdown
   ---
   type: session
   project: {project}
   task_slug: {task-slug}
   status: in-progress
   created: {YYYY-MM-DD}
   tags: [{generated-tags}]
   related:
     # AUTO-POPULATED from Step 4.6 suggest-related.sh output
     - "[[work-docs/{project}/plans/PLAN-{task-slug}]]"
     - "[[work-docs/{project}/context/TECH_SPEC]]"
     # Add more from RELATED_LINKS variable
   summary: "{AUTO: Extract from 'What Was Done' in Implementation Summary}"
   ---
   ```

   **Summary Generation (AUTO - Implementation Required):**

   After writing the SESSION document, extract the summary from "### What Was Done":

   ```bash
   # Method 1: Bash extraction (simple)
   session_file="SESSION-${task_slug}-$(date +%Y-%m-%d).md"
   summary=$(grep -A 2 "### What Was Done" "$session_file" | tail -1 | head -c 100)

   # Update frontmatter summary field
   sed -i "s/summary: \".*\"/summary: \"${summary}\"/" "$session_file"
   ```

   ```python
   # Method 2: Python extraction (robust)
   import re
   from pathlib import Path

   def extract_and_update_summary(session_path: str) -> str:
       content = Path(session_path).read_text()

       # Extract "What Was Done" section content
       match = re.search(r'### What Was Done\n+(.+?)(?=\n#|\n---|\Z)', content, re.DOTALL)
       if match:
           # Get first sentence/line, max 100 chars
           summary = match.group(1).strip().split('\n')[0][:100]

           # Update frontmatter
           updated = re.sub(
               r'(summary: ")[^"]*(")',
               f'\\1{summary}\\2',
               content
           )
           Path(session_path).write_text(updated)
           return summary
       return ""
   ```

   **Requirements:**
   - Extract first paragraph from "### What Was Done" section
   - Truncate to 100 characters maximum
   - Update frontmatter `summary` field before saving

   **Example:**
   - Input: "Implemented MQTT retry logic with exponential backoff. Added circuit breaker pattern for resilience. Created 15 unit tests covering all edge cases."
   - Output: `"Implemented MQTT retry logic with exponential backoff. Added circuit breaker pattern for resilien"`

   **Related Links (AUTO from suggest-related.sh):**
   - Run `suggest_for_session` from Step 4.6
   - PLAN document is always included automatically
   - Add context docs and related sessions

   **Tag Generation (MANDATORY - LLM Required):**

   **MUST include at minimum:**
   1. **Project tag**: The project name (e.g., `edge-ai`, `uniep`, `bsp`, `checkup`)
   2. **Document type**: Always include `session` for SESSION documents
   3. **Primary tech stack**: At least one (e.g., `python`, `c`, `cpp`, `typescript`)

   **SHOULD include 2-5 additional tags from:**
   - **Domain**: `ess`, `ems`, `embedded`, `iot`, `security`, `matter`, `cyber-security`
   - **Technologies**: `mqtt`, `docker`, `yocto`, `sqlite`, `ipc`, `bootloader`, `kernel`
   - **Topics**: `testing`, `performance`, `optimization`, `documentation`, `database`
   - **Activities**: `refactoring`, `integration`, `bugfix`, `factory-test`, `firmware-update`

   **Standard tag vocabulary (prefer these over creating new tags):**
   - Languages: `python`, `c`, `cpp`, `typescript`, `rust`, `go`
   - Infrastructure: `embedded`, `bootloader`, `kernel`, `storage`, `networking`
   - Domains: `ess`, `ems`, `matter`, `bsp`, `uniep`, `checkup`
   - Tools: `yocto`, `docker`, `mqtt`, `ipc`, `sqlite`, `pytest`, `cvxpy`
   - Topics: `security`, `testing`, `performance`, `optimization`, `observability`

   **Target:** 5-8 tags total (minimum 3: project + type + tech-stack)

   **Examples:**
   - ✅ GOOD: `[edge-ai, session, python, ess, forecasting, database, pytest]` (7 tags, implementation-specific)
   - ✅ GOOD: `[uniep, session, c, mqtt, ipc, bugfix]` (6 tags, describes what was done)
   - ❌ BAD: `[session, done, stuff, L142]` (meaningless, not from vocabulary)
   - ❌ BAD: `[edge-ai]` (too few, missing tech-stack and type)

   ```markdown

   # SESSION: {Task Name}

   **Project:** {project}
   **Task:** {task-name}
   **Date:** {date}
   **Started:** {start-time}
   **Completed:** {end-time}
   **Duration:** {duration}

   ---

   ## 📋 Plan Reference

   - [PLAN Document](../plans/PLAN-{task-name}.md)

   ---

   ## 📚 Prior Knowledge Applied

   > **From knowledge base search - what prior work informed this implementation**

   ### Related Sessions Referenced
   - [[SESSION-related-task-YYYY-MM-DD]] - {insight applied}

   ### Solutions Reused
   {What approaches from prior work were applied here}

   ### Pitfalls Avoided
   {What known issues from history were proactively addressed}

   ---

   ## ✅ Implementation Summary

   ### What Was Done
   {High-level summary of changes}

   ### Changes Made
   | File | Changes | Lines |
   |------|---------|-------|
   | {file1} | {description} | +X -Y |
   | {file2} | {description} | +X -Y |

   ---

   ## 🔄 Implementation Log

   ### Phase 1: Core Implementation
   **Status:** ✅ Completed

   - Modified {file}: {what-changed}
   - Created {file}: {purpose}
   - Updated {file}: {changes}

   **Testing:** {test-results}

   ### Phase 2: Testing
   **Status:** ✅ Completed

   - Added unit tests: {test-file}
   - All tests passing: ✅

   ### Phase 3: Integration
   **Status:** ✅ Completed

   - Integrated with {component}
   - Manual testing completed

   ---

   ## 🚨 Issues Encountered

   ### Issue 1: {description}
   - **Encountered:** {when}
   - **Impact:** {what-broke}
   - **Solution:** {how-fixed}

   ---

   ## 🧪 Test Results

   ### Unit Tests
   ```
   {test-output}
   ```

   ### Integration Tests
   ```
   {test-output}
   ```

   ### Manual Testing
   - [x] Test case 1: PASS
   - [x] Test case 2: PASS

   ---

   ## ✅ Success Criteria Check

   - [x] Criterion 1: Met
   - [x] Criterion 2: Met
   - [x] All tests passing
   - [ ] Ready for review

   ---

   ## 💾 Git Status

   **Branch:** {current-branch}
   **Files Changed:** {count}

   ```bash
   git status
   {output}
   ```

   ---

   ## 📊 Metrics

   - **Files Changed:** {count}
   - **Lines Added:** +{n}
   - **Lines Removed:** -{n}
   - **Tests Added:** {count}
   - **Duration:** {hours}

   ---

   ## ➡️ Next Steps

   1. Code review: `/analyse {task-name}`
   2. Or finalize: `/wrapup {task-name}`
   ```

10. **Validate SESSION Frontmatter (MANDATORY)**

   After generating SESSION document, validate required frontmatter fields:

   **Required Fields:**
   | Field | Type | Validation |
   |-------|------|------------|
   | type | string | Must be "session" |
   | project | string | Must match project name |
   | task_slug | string | Must match task slug |
   | status | enum | One of: planning, in-progress, completed |
   | created | date | Format: YYYY-MM-DD |
   | tags | array | Minimum 3 tags (project + type + tech-stack) |
   | related | array | At least PLAN document link |
   | summary | string | Max 100 characters, extracted from "What Was Done" |

   **Validation Check:**
   ```bash
   session_file="${vault_path}/work-docs/${project}/sessions/SESSION-${task_slug}-$(date +%Y-%m-%d).md"

   # Validate required fields exist
   required_fields=("type:" "project:" "task_slug:" "status:" "created:" "tags:" "summary:")
   for field in "${required_fields[@]}"; do
       if ! grep -q "^${field}" "$session_file"; then
           echo "ERROR: Missing frontmatter field: ${field}" >&2
           # Add missing field with placeholder
       fi
   done

   # Validate minimum tag count (3)
   tag_count=$(grep "^tags:" "$session_file" | grep -o '\[.*\]' | tr ',' '\n' | wc -l)
   if [[ $tag_count -lt 3 ]]; then
       echo "WARNING: Insufficient tags (${tag_count}/3 minimum)" >&2
   fi
   ```

   **On Validation Failure:**
   - Log warning but don't block execution
   - Add placeholder values for missing fields
   - Mark validation status in SESSION doc

11. **Sync to Vault TODO**
   ```bash
   sync_todo_update "execute" "${task-slug}" "work-docs/${project}/sessions/SESSION-${task-slug}-${date}.md"
   ```

12. **Update RAG Index**
   ```bash
   # Run janitor to update RAG index with new SESSION document
   if command -v python3 &> /dev/null; then
       python3 "${vault_path}/.claude/rag/janitor.py" --project "${project}" 2>/dev/null || true
   fi
   ```

13. **Output Summary**
   ```markdown
   ## ✅ Implementation Complete

   **Task:** {task-name}
   **Duration:** {duration}
   **Files Changed:** {count}

   ## 📁 Documents
   - PLAN: {link}
   - SESSION: {link}

   ## ✅ Status
   - [x] Implementation complete
   - [x] Tests passing
   - [ ] Code review needed

   ## ➡️ Next Steps

   1. Review implementation in SESSION-{task-name}-{date}.md
   2. Check vault TODO.md (task status → in-progress, SESSION link added)
   3. Run code review: `/analyse {task-name}`
   4. Or finalize if confident: `/wrapup {task-name}`
   ```

## Important Notes

- **Requires PLAN document** - fails if not found
- Uses **multi-agent orchestration** (coder + tester + stuck)
- Creates **detailed SESSION log** with all changes
- Auto-updates vault TODO.md with:
  - SESSION document link
  - Status: in-progress
  - Updated timestamp
- Should complete based on complexity (30 min to several hours)
- **Never skip testing** - tester agent validates each phase

## Multi-Agent Flow

```
Execute command starts
  ↓
Load PLAN → Extract phases
  ↓
For each phase:
  ↓
  CODER implements
    ↓
  Reports completion
    ↓
  Auto-invoke TESTER
    ↓
  TESTER validates
    ↓
  ✅ PASS → Next phase
  ❌ FAIL → STUCK → User decides
  ↓
All phases complete
  ↓
Generate SESSION document
  ↓
Update TODO.md
  ↓
Done
```

## Error Handling

- If PLAN not found: Show error, suggest `/myplan {task-name}` first
- If tests fail: Invoke STUCK agent, present options
- If build fails: Invoke STUCK agent
- If obsidian.json missing: Show setup error
- If session document can't be written: Show path error

## Code Quality

- Follow project coding standards from CLAUDE.md
- Write clean, documented code
- Include error handling
- Add appropriate logging
- Maintain consistency with existing code

---

## Background Execution (Claude Code Web)

### Overview

For long-running tasks that exceed typical session duration, Claude Code Web provides background task execution with session persistence. This enables overnight batch processing, complex builds, and cross-device task continuity.

### Use Cases

**When to Use Background Execution:**
- Long compilation cycles (>30 minutes)
- Multi-hour test suites (integration, E2E, performance)
- Database migrations requiring extended downtime
- Batch data processing overnight
- CI/CD pipeline monitoring across builds
- Tasks you want to start and check later from different device

**When NOT to Use Background:**
- Quick implementations (<30 minutes estimated)
- Interactive debugging sessions
- Tasks requiring frequent user decisions
- Rapid iteration workflows

### Background Execution Mode

**Starting Background Task:**
```bash
# In Claude Code Web interface:
/execute task-slug

# When prompted, select:
"Run in background - I'll check back later"
```

**Technical Implementation:**
- Task runs in isolated container with preserved state
- Session persists across browser/device switches
- Process continues even when interface closed
- Environment variables and file contexts maintained

### Status Monitoring

**Check Task Status:**
```bash
# Resume session in Claude Code Web
# Navigate to project directory
# View background tasks panel (⌘/Ctrl + Shift + B)

# Or check via CLI:
claude code status --project {project-name}
```

**Status Information Provided:**
- Current phase (from TodoWrite tracking)
- Time elapsed since start
- Last agent completion (CODER, TESTER results)
- Any blockers requiring user decision
- Estimated completion (if phases have time estimates)

### Result Retrieval

**When Task Completes:**

1. **Notification** (if configured):
   - Email notification on completion
   - Slack/Discord webhook (if integrated)
   - Mobile push (Claude Code mobile app)

2. **Access Results**:
   - Resume session in Claude Code Web
   - SESSION document auto-generated in vault
   - Review implementation summary
   - Check TESTER validation results

3. **Next Steps**:
   - If all tests passed: Proceed to `/wrapup`
   - If blockers encountered: Review AskUserQuestion prompts
   - If unexpected failures: Review logs in SESSION document

### Session Recovery

**Handling Interruptions:**

If background task encounters blocker requiring user decision:
- Task pauses at AskUserQuestion
- User notified (if notification configured)
- Resume session → Review options → Make decision
- Task continues from exact pause point

**Recovery from Failures:**
- Checkpoint system preserves state before each phase
- Can rewind to last successful checkpoint
- Environment and file changes preserved
- Re-run from checkpoint without losing progress

### Best Practices

**Task Preparation:**
1. Run `/myplan` with detailed phases and time estimates
2. Ensure all dependencies available in environment
3. Configure notifications for completion/blockers
4. Review PLAN for potential blocker points

**During Execution:**
1. Check status periodically (every few hours for overnight tasks)
2. Respond to blocker notifications promptly
3. Review phase completion in TodoWrite tracking
4. Monitor resource usage (disk, memory) for long tasks

**After Completion:**
1. Review SESSION document thoroughly
2. Verify all success criteria met
3. Check for warnings/errors in logs
4. Run `/wrapup` to finalize

### Limitations

**Current Constraints:**
- Maximum task duration: 24 hours (auto-timeout)
- Concurrent background tasks: 3 per project
- Session persistence: 7 days (after completion)
- Network interruptions handled automatically (retry logic)

**Known Issues:**
- Interactive debugger attachment not supported in background mode
- Real-time file watching disabled (performance optimization)
- Git operations may require credential re-entry on resume

### Example: Overnight Test Suite

```markdown
Scenario: Run comprehensive test suite overnight (estimated 6 hours)

1. Preparation (5 PM):
   /myplan run-full-test-suite
   Review PLAN phases:
     - Phase 1: Unit tests (1h)
     - Phase 2: Integration tests (2h)
     - Phase 3: E2E tests (2h)
     - Phase 4: Performance tests (1h)

2. Start Background Execution:
   /execute run-full-test-suite
   → Select "Run in background"
   → Configure email notification on completion

3. Next Morning (9 AM):
   → Receive completion email
   → Resume Claude Code Web session
   → Review SESSION document:
     - All phases completed ✅
     - 247 tests passed, 3 failures identified
     - Performance regression detected in Phase 4

4. Next Steps:
   → Review TESTER output for 3 failures
   → Create follow-up tasks for failures
   → Complete with: /wrapup run-full-test-suite
```

### Session Persistence Details

**What Persists:**
- Process state and execution context
- Environment variables and loaded modules
- File system changes and working directory
- TodoWrite phase tracking state
- Agent invocation history
- Checkpoint snapshots

**What Resets:**
- Active terminal connections (auto-reconnect)
- Debugger attachments (require re-attach)
- File watchers (restart on resume)
- Real-time console output (buffered, replay available)

### Integration with Vault System

**Automatic Synchronization:**
- Background tasks continue vault sync operations
- SESSION document created on completion
- TODO.md status updated automatically
- RAG index updated after completion

**Cross-Device Workflow:**
```
Device A (Office): Start /execute in background → Close laptop
Device B (Home): Resume session → Check status → Respond to blocker
Device A (Office): Next day → Review results → Run /wrapup
```

All work tracked in central vault, accessible from any device with Claude Code Web access.

---
