# Wrapup Command (Repo)

Finalize task: test, Jira draft, mark complete

## Usage

```bash
/wrapup [task-slug]
```

## Arguments

- `task-slug`: Task identifier from TODO.md `[task:: slug]` field
  - Example: `wifi-bt-wakeup-check`, `secure-boot`, `thread-동작-체크`
  - Must have completed `/myplan`, `/execute`, and optionally `/analyse`
  - Must match exactly (case-sensitive)
  - Will mark task complete in TODO.md after successful wrapup

## Project Context

**Project:** vault-system
**Build Command:** N/A (documentation/config project)
**Test Command:** python3 .claude/rag/janitor.py --validate
**Jira Project:** N/A

## Implementation

You are a task finalizer for vault-system project. Follow these steps:

1. **Load Configuration**
   ```bash
   source {vault-path}/.claude/hooks/lib/sync-todo.sh
   vault_path=$(get_vault_path)
   project=$(get_project_name)
   ```

2. **Pre-Flight Checks**
   - PLAN document exists
   - SESSION document exists
   - ANALYSIS completed (or skip if not needed)
   - No critical issues in ANALYSIS

3. **Final Testing**

   **For vault-system:**
   ```bash
   # Validate RAG index
   python3 .claude/rag/janitor.py --validate

   # Check for broken wiki-links
   # (validation script if available)

   # Verify command templates
   ls -la .claude/commands/
   ```

4. **REVIEWER Analysis (Quality Gate)**

   After TESTER passes, invoke REVIEWER for AI-on-AI verification:

   **Mandatory For:**
   - Tasks modifying >3 files
   - Tasks touching security-sensitive code
   - Architecture changes
   - New feature implementations

   **May Skip For:**
   - Documentation-only changes
   - Single-file bug fixes
   - Configuration updates
   - User explicitly requests skip with documented reason

   ### Detection Guidance

   To determine if REVIEWER is mandatory:

   1. **File Count Check:**
      ```bash
      # Count files changed in this task
      git diff --name-only HEAD~1 2>/dev/null | wc -l
      # Or check SESSION document "Files Changed" count
      ```
      - If >3 files changed → REVIEWER mandatory

   2. **Security-Sensitive Check:**
      - Files matching: `auth`, `security`, `crypto`, `password`, `token`, `secret`
      - If any match → REVIEWER mandatory

   3. **Architecture Check:**
      - New modules or significant refactoring
      - Changes to core abstractions or APIs
      - If yes → REVIEWER mandatory

   4. **Documentation-Only Check:**
      ```bash
      # Check if all changes are .md files
      git diff --name-only HEAD~1 | grep -vE "\.md$" | wc -l
      ```
      - If result is 0 → REVIEWER optional (doc-only)

   ### REVIEWER Invocation

   ```
   Task tool with subagent_type=reviewer
   Prompt: """
   Perform code review on the following implementation:

   **Task:** {task-slug}
   **Files Changed:** {list from SESSION or TESTER output}
   **TESTER Result:** PASS

   Focus on:
   1. Security vulnerabilities
   2. Architecture alignment with project patterns
   3. Edge cases not covered by tests
   4. Code quality and maintainability
   5. Performance implications

   Output: APPROVED | CHANGES_REQUESTED | NEEDS_WORK
   """
   ```

   ### REVIEWER Results Handling

   - **APPROVED**: Continue to next step
   - **CHANGES_REQUESTED**: Present issues to user, decide whether to fix now or defer
   - **NEEDS_WORK**: Block wrapup, return to /execute with identified issues

   ### Skip Documentation

   If skipping REVIEWER, document in WRAPUP:
   ```markdown
   ## REVIEWER Status
   **Skipped:** Yes
   **Reason:** {Documentation-only | Single-file fix | User request: {reason}}
   ```

5. **Sync Master Documents to Vault** (Repo → Vault)
   ```bash
   # For vault-system, master docs ARE in the vault already
   # No sync needed - this IS the vault
   echo "✓ Master docs already in vault (self-referential project)"
   ```

6. **Generate Jira Content** (Optional for vault-system)

   Since vault-system is an internal project, Jira content is optional.
   Skip if no Jira ticket associated.

7. **Generate WRAPUP Document**
   Save to: `${vault_path}/work-docs/${project}/wrapups/WRAPUP-${task-slug}.md`

   **MUST include YAML frontmatter** for RAG indexing:

   ```markdown
   ---
   type: wrapup
   project: vault-system
   task_slug: {task-slug}
   status: completed
   created: {YYYY-MM-DD}
   tags: [{generated-tags}]
   related:
     - "[[work-docs/vault-system/plans/PLAN-{task-slug}]]"
     - "[[work-docs/vault-system/sessions/SESSION-{task-slug}-{date}]]"
   summary: "{one-line-summary-of-completion}"
   ---
   ```

   **Tag Generation (MANDATORY - LLM Required):**

   **MUST include at minimum:**
   1. **Project tag**: `vault-system`
   2. **Document type**: Always include `wrapup`
   3. **Status**: Always include `completed`
   4. **Primary tech stack**: `markdown`, `shell`, `python`

   **SHOULD include 2-4 additional tags from:**
   - **Domain**: `documentation`, `workflow`, `automation`
   - **Technologies**: `obsidian`, `claude-code`, `mcp`, `rag`
   - **Topics**: `process`, `productivity`, `ai-assistant`

   **Target:** 6-9 tags total (minimum 4: project + type + completed + tech-stack)

   ```markdown

   # WRAPUP: {Task Name}

   **Project:** vault-system
   **Task:** {task-name}
   **Completed:** {date}

   ---

   ## ✅ Summary

   {1-2 paragraph summary of what was accomplished}

   ---

   ## 📋 References

   - [PLAN](../plans/PLAN-{task-name}.md)
   - [SESSION](../sessions/SESSION-{task-name}-{date}.md)
   - [ANALYSIS](../analysis/ANALYSIS-{task-name}-{date}.md)

   ---

   ## 🧪 Testing

   **Validation:** ✅ PASS
   **RAG Index:** ✅ Valid
   **Wiki-Links:** ✅ No broken links

   **Test Summary:**
   ```
   {validation output}
   ```

   **vault-system-Specific Validation:**
   - [x] Commands work correctly
   - [x] Templates follow standards
   - [x] Frontmatter is valid YAML

   ---

   ## 📊 Metrics

   - **Development Time:** {hours}
   - **Files Changed:** {count}
   - **Templates Updated:** {count}

   ---

   ## 💡 Learnings

   {What went well, what could be improved, lessons learned}

   ---

   ## ➡️ Follow-up

   - [ ] Update documentation if needed
   - [ ] Notify team of changes
   ```

8. **Generate Meta-Learning Document** (MANDATORY)

   > **Why mandatory?** Industry research shows ~40% retrospective capture rate correlates with
   > significantly better AI-assisted productivity. Our system had 0% LEARNING generation despite
   > 36+ completed tasks. This is a critical gap that prevents knowledge accumulation.

   **Auto-generate LEARNING (no user prompt):**
   ```
   🧠 Generating meta-learning analysis... [~2 min]

   Captures:
   ✓ Mental model updates (what you learned)
   ✓ AI collaboration improvements (what worked/failed)
   ✓ Reusable patterns (apply to future tasks)
   ✓ Process metrics (planning accuracy, agent efficiency)
   ```

   **Implementation:**

   a. **Load Artifacts**
   ```bash
   plan_file="${vault_path}/work-docs/${project}/plans/PLAN-${task_slug}.md"
   session_file="${vault_path}/work-docs/${project}/sessions/SESSION-${task_slug}-$(date +%Y-%m-%d).md"
   wrapup_file="${vault_path}/work-docs/${project}/wrapups/WRAPUP-${task_slug}.md"
   ```

   b. **Analyze Using Sequential MCP**

   Generate analysis covering:

   **📚 Mental Model Updates**
   - Compare PLAN assumptions vs SESSION reality
   - Extract system behavior insights
   - Identify domain knowledge gained

   **🤖 AI Collaboration Improvements**
   - Parse SESSION for agent interactions (CODER/TESTER/REVIEWER/STUCK)
   - Identify effective vs ineffective prompts
   - Extract context management insights

   **🔄 Reusable Patterns**
   - Identify implementation patterns from code changes
   - Extract testing strategies that worked
   - Capture workflow patterns (agent sequences)

   **📊 Process Metrics**
   - Compare PLAN time estimates vs SESSION actuals
   - Calculate agent efficiency (iterations, pass rates)
   - Identify complexity indicators

   c. **Generate LEARNING Document**
   ```bash
   learning_dir="${vault_path}/knowledge-base/learnings/${project}"
   mkdir -p "$learning_dir"
   learning_file="${learning_dir}/LEARNING-${task_slug}.md"

   # Generate from template with AI analysis
   # Save to learning_file
   echo "✅ Generated: knowledge-base/learnings/${project}/LEARNING-${task_slug}.md"
   ```

   d. **Link from WRAPUP**

   Add to WRAPUP document after "## ➡️ Follow-up" section:
   ```markdown
   ## 🧠 Meta-Learning

   **Learning Document**: [[../../knowledge-base/learnings/vault-system/LEARNING-{task_slug}]]

   **Quick Takeaways:**
   - Mental Model: {one-liner from analysis}
   - AI Collaboration: {one-liner from analysis}
   - Reusable Pattern: {one-liner from analysis}
   ```

   **Note:** LEARNING generation is no longer optional. If for any reason the
   LEARNING document cannot be generated (missing PLAN/SESSION, etc.), log the
   reason and continue with WRAPUP, but flag it for manual follow-up:
   ```
   ⚠️ LEARNING generation incomplete: {reason}

   💡 Generate manually later with:
      /reflect {task-slug}
   ```

9. **Update CLAUDE.md Corrections (Self-Learning)**

   Reflect on mistakes made during this session and append corrections to CLAUDE.md:

   **What Qualifies as a Correction:**
   - ❌ Incorrect API usage patterns that were corrected
   - ❌ Wrong command syntax that caused failures
   - ❌ Misunderstanding of project conventions
   - ❌ Build/test patterns that failed and needed fixing
   - ❌ Security practices that needed correction
   - ❌ Tool usage mistakes (e.g., Edit without Read, wrong grep flags)
   - ❌ Workflow violations (e.g., skipped validation steps)

   **What Does NOT Qualify:**
   - ✅ User preference changes (not mistakes)
   - ✅ Expected errors during normal development
   - ✅ Normal debugging iterations
   - ✅ Design decisions that evolved
   - ✅ Performance optimizations (not mistakes)

   **Implementation:**

   a. **Review Session Artifacts**
   ```bash
   session_file="${vault_path}/work-docs/${project}/sessions/SESSION-${task_slug}-$(date +%Y-%m-%d).md"
   ```

   b. **Identify Corrections**

   Review SESSION document for:
   - "TESTER FAILED" events → what was the mistake?
   - "STUCK escalations" → what assumption was wrong?
   - Error messages that required fix → what was incorrect?
   - Rework or backtracking → what didn't work?

   c. **Append to Appropriate CLAUDE.md**

   **Global mistakes** (apply to all projects):
   ```bash
   global_claude="${HOME}/.claude/CLAUDE.md"
   # Append to "## Learned Corrections" → "### 2026" section
   ```

   **Project-specific mistakes** (apply only to this project):
   ```bash
   project_claude="${PWD}/.claude/CLAUDE.md"
   # Append to "## Learned Corrections" → "### 2026" section (if exists)
   ```

   d. **Format**
   ```markdown
   - YYYY-MM-DD: [project-name] Description of mistake and correct approach
   ```

   **Examples:**
   ```markdown
   - 2026-01-11: [uniep] sys_manager_tester requires --host flag before --service, not after
   - 2026-01-11: [bsp] devtool modify must be run from build directory, not meta-layer
   - 2026-01-10: [vault-system] TodoWrite must update status before invoking agents
   ```

   e. **Document in WRAPUP**

   Add to "## 💡 Learnings" section:
   ```markdown
   **CLAUDE.md Corrections Added:**
   - [Global] {correction-summary}
   - [Project] {correction-summary}
   ```

   **If no corrections found:**
   ```markdown
   **CLAUDE.md Corrections:** None - no mistakes requiring documentation
   ```

   **Important:** This step is non-blocking. If no corrections are identified, simply note that in the WRAPUP and continue.

10. **Sync to Vault TODO**
   ```bash
   # Add LEARNING link if generated
   if [ -f "$learning_file" ]; then
       sync_todo_update "learning" "${task-slug}" "knowledge-base/learnings/${project}/LEARNING-${task-slug}.md"
   fi

   # Add WRAPUP link and mark complete
   sync_todo_update "wrapup" "${task-slug}" "work-docs/${project}/wrapups/WRAPUP-${task-slug}.md"
   ```

   This will:
   - Add WRAPUP link
   - Add LEARNING link (if generated)
   - Check the task checkbox (mark complete)
   - Update timestamp

11. **Update RAG Index**
   ```bash
   # Run janitor to update RAG index with all new documents (WRAPUP + LEARNING)
   if command -v python3 &> /dev/null; then
       python3 "${vault_path}/.claude/rag/janitor.py" --project "${project}" 2>/dev/null || true
   fi
   ```

12. **Update Prompt Effectiveness** (Knowledge Evolution)
    ```bash
    # Find latest SESSION document for this task
    session_file=$(ls -t "${vault_path}/work-docs/${project}/sessions/SESSION-${task_slug}-"*.md 2>/dev/null | head -1)

    if [[ -n "$session_file" ]] && command -v python3 &> /dev/null; then
        echo "📊 Updating prompt effectiveness tracking..."
        python3 "${vault_path}/.claude/hooks/lib/prompt-tracker.py" "$session_file" --update-prompts 2>/dev/null || true
    fi
    ```

    This step:
    - Parses the "Prompts Used" table from SESSION document
    - Updates `last_used` and `effectiveness` fields in prompt frontmatter
    - Generates usage analytics for `/meta` integration
    - Closes the knowledge evolution feedback loop

13. **Output Summary**
    ```markdown
    ## ✅ Task Complete!

    **Task:** {task-name}

    ## 📁 Documents
    - PLAN: {link}
    - SESSION: {link}
    - ANALYSIS: {link}
    - WRAPUP: {link}
    - LEARNING: {link} (if generated)

    ## ✅ Checklist

    - [x] Implementation complete
    - [x] Validation passing
    - [x] Meta-learning captured (if generated)
    - [x] TODO updated

    ## ➡️ Next Steps

    1. Check vault TODO.md (task marked complete ✅)
    2. Review LEARNING document for insights
    ```

## Important Notes

- **Final step** in task lifecycle
- Runs **validation** instead of build/test (documentation project)
- Auto-updates TODO.md:
  - WRAPUP document link
  - Task checked ✅ (complete)
  - Moved to "Completed This Week"
- Should complete in 5-10 minutes

## Error Handling

- If validation fails: Show errors, suggest fixes
- If TODO update fails: Show manual update instructions
- If PLAN/SESSION missing: Warn but continue (may be manual task)

## AI Branch Tagging Convention

When creating commits for AI-assisted work, follow the branch naming convention:

### Branch Naming Pattern

```
agent/{task-slug}/{date}
```

**Examples:**
```bash
agent/fix-timeout-bug/2025-12-19
agent/add-mqtt-retry/2025-12-15
agent/refactor-auth-module/2025-11-20
```

### When to Create Agent Branches

1. **New feature implementation** via `/execute`
2. **Bug fixes** generated by AI agents
3. **Refactoring** performed by CODER agent

### Branch Creation in /wrapup

If not already on an agent branch, wrapup can optionally create one:
```bash
# Check current branch
current_branch=$(git branch --show-current)

# If on main/master, suggest agent branch
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
    echo "⚠️ Working on main branch. Consider creating agent branch:"
    echo "   git checkout -b agent/${task_slug}/$(date +%Y-%m-%d)"
fi
```

### Commit Message Attribution

All AI-generated commits include:
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Quality Gates

**Do NOT proceed if:**
- ❌ Validation failing
- ❌ Critical issues in ANALYSIS unresolved
- ❌ Uncommitted changes that shouldn't be committed

**OK to proceed if:**
- ✅ Validation successful
- ✅ Code review clean or minor warnings only
- ✅ Changes match PLAN scope
