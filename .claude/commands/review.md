# Review Command (Repo)

## Communication Protocol

- Be direct and matter-of-fact. No flattery, no preamble, no "Great question!"
- If reasoning is flawed, say so immediately with specific evidence
- Don't fold arguments on pushback — maintain position unless new evidence is presented
- Lead with concerns before agreement
- When you agree, explain WHY with specific reasoning — not just validation

## Input Processing

Before analyzing, mentally reframe the submission as a question:
"Does this code/plan meet the stated requirements without issues?"
This reframing reduces confirmation bias toward the author's intent.

Code review and quality analysis. This is **Step 4** of the 5-stage workflow.

## Usage

```bash
/review [task-slug]
/review              # review entire recent changes
```

## Arguments

- `task-slug`: Optional task identifier from TODO.md `[task:: slug]` field
  - Example: `wifi-bt-wakeup-check`, `secure-boot`, `thread-동작-체크`
  - If provided: Reviews files related to this task
  - If omitted: Reviews recent Git changes (uncommitted + last commit)
  - Must match exactly (case-sensitive)

## Workflow Position

```
1. Research → 2. Plan → 3. Execute → [4. REVIEW] → 5. Wrapup
                                          ↑
                                       YOU ARE HERE
```

## Project Context

**Project:** Determined from `.claude/obsidian.json`
**Tech Stack:** Determined from project files
**Code Standards:** See CLAUDE.md in this repo

## Implementation

You are a code reviewer for this project. Follow these steps:

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

   # Enforce reviewer agent for /review
   require_multiagent_system "review" "reviewer"
   ```

3. **Determine Scope**
   - If task-slug provided: Review files related to that task
   - If no task-slug: Review recent Git changes (uncommitted + last commit)

4. **Invoke REVIEWER Agent**
   ```
   Task(
     subagent_type="reviewer",
     description="Code review for {task-slug | recent-changes}",
     prompt="{
       Project: {project}
       Focus: {task-specific or recent changes}
       Standards: {from CLAUDE.md}
       Analysis mode: deep
     }"
   )
   ```

5. **Analysis Focus**

   **General Review Areas:**
   - **Code Quality**: Readability, maintainability, naming, duplication
   - **Architecture**: Separation of concerns, coupling, cohesion
   - **Robustness**: Error handling, edge cases, defensive programming
   - **Security**: Input validation, injection risks, data handling
   - **Performance**: Algorithm complexity, resource usage, bottlenecks
   - **Testing**: Coverage, test quality, testability

   **Recurring Bug Patterns to Check (from past reviews):**
   - **Redundant function calls**: Is extracted data being re-extracted? (e.g., _extract_code on already-extracted field)
   - **Missing test coverage**: New CLI options/modules without corresponding tests?
   - **Substring matching bugs**: Does `"copy_to_user" in code` also match `__copy_to_user`?
   - **Error field is None vs empty string**: Which one does the upstream return? Is the caller checking correctly?
   - **Date/format validation**: String comparison without format enforcement?
   - **Duplicate checks**: Same logic implemented twice under different names?

   **Project-Specific Checks:**
   - Follow patterns in project CLAUDE.md (especially Quality Gates section)
   - Verify consistency with existing codebase
   - Check for project-specific anti-patterns
   - **New features MUST have tests** — flag if missing

6. **Generate REVIEW Document**
   Save to: `${vault_path}/work-docs/${project}/reviews/REVIEW-${task-slug}-${date}.md`

   **Important:**
   - Create `${vault_path}/work-docs/${project}/reviews/` directory if it doesn't exist
   - Use task-slug (not task-name) for filename
   - Document will be visible in Obsidian vault
   - **MUST include YAML frontmatter** for RAG indexing

   ```markdown
   ---
   type: review
   project: {project}
   task_slug: {task-slug}
   status: review
   created: {YYYY-MM-DD}
   tags: [{project}, review, {tech-stack}, {domain}]
   related:
     - "[[work-docs/{project}/sessions/SESSION-{task-slug}-{date}]]"
     - "[[work-docs/{project}/plans/PLAN-{task-slug}]]"
   summary: "{Grade} review - {N} critical, {M} warnings - {APPROVED|CHANGES_REQUESTED}"
   ---

   # REVIEW: {Task Name | Recent Changes}

   **Project:** {project}
   **Date:** {date}
   **Scope:** {files-analyzed}
   **Analysis Mode:** Deep

   ---

   ## 📊 Summary

   **Grade:** A | B | C | D | F
   **Critical Issues:** {count}
   **Warnings:** {count}
   **Suggestions:** {count}

   ### Grading Criteria
   - **A (Excellent):** No critical issues, minimal warnings, follows best practices
   - **B (Good):** No critical issues, some warnings, generally well-written
   - **C (Acceptable):** Minor critical issues, several warnings, needs polish
   - **D (Marginal):** Critical issues present, many warnings, needs work
   - **F (Fail):** Major critical issues, not ready for merge

   ---

   ## 🔍 Detailed Findings

   ### Critical Issues (Must Fix)

   #### Issue 1: {title}
   **File:** {file}:{line}
   **Severity:** Critical
   **Category:** {Security | Performance | Correctness | Architecture}

   **Problem:**
   {Description}

   **Code:**
   ```{lang}
   {problematic-code}
   ```

   **Why This Matters:**
   {Impact explanation}

   **Recommendation:**
   ```{lang}
   {fixed-code}
   ```

   ---

   ### Warnings (Should Fix)

   #### Warning 1: {title}
   **File:** {file}:{line}
   **Category:** {category}

   {Description and recommendation}

   ---

   ### Suggestions (Nice to Have)

   #### Suggestion 1: {title}
   **File:** {file}:{line}

   {Description}

   ---

   ## ✅ Positive Observations

   - Good practice 1
   - Good practice 2
   - Well-implemented pattern

   ---

   ## 📋 Project-Specific Checks

   ### {Check Category 1}
   - [x] Check 1: PASS
   - [ ] Check 2: FAIL - {reason}

   ### {Check Category 2}
   - [x] Check 1: PASS

   ---

   ## 🧪 Test Coverage

   **Coverage:** {percentage}%
   **Missing Tests:**
   - Function 1
   - Function 2

   ---

   ## 📊 Code Metrics

   - **Files Reviewed:** {count}
   - **Lines Changed:** +{added} -{removed}
   - **Complexity:** {assessment}
   - **Maintainability:** {assessment}

   ---

   ## ✅ Action Items

   **Must Do (Before Commit):**
   - [ ] Fix critical issue 1
   - [ ] Fix critical issue 2

   **Should Do (This PR):**
   - [ ] Address warning 1
   - [ ] Add tests for X

   **Nice to Have (Future):**
   - [ ] Refactor Y
   - [ ] Improve documentation

   ---

   ## ➡️ Recommendation

   **Status:** APPROVED | CHANGES_REQUESTED | NEEDS_WORK

   {Explanation}
   ```

7. **Sync to Vault TODO**
   ```bash
   sync_todo_update "review" "${task-slug}" "work-docs/${project}/reviews/REVIEW-${task-slug}-${date}.md"
   ```

8. **Update RAG Index**
   ```bash
   if command -v python3 &> /dev/null; then
       python3 "${vault_path}/.claude/rag/janitor.py" --project "${project}" 2>/dev/null || true
   fi
   ```

9. **Output Summary**
   ```markdown
   ## ✅ Review Complete

   **Grade:** {grade}
   **Critical Issues:** {count}
   **Recommendation:** {status}

   ## 📁 Document
   - REVIEW: [[work-docs/{project}/reviews/REVIEW-{task-slug}-{date}]]

   ## 🚨 Action Required

   {If critical issues:}
   Must fix before proceeding:
   - Issue 1: {file}:{line}
   - Issue 2: {file}:{line}

   {If no critical issues:}
   Code quality looks good! Minor improvements suggested.

   ## ➡️ Next Steps

   {If changes needed:}
   1. Review REVIEW document
   2. Fix critical issues
   3. Run `/execute {task-slug}` to apply fixes
   4. Re-run `/review {task-slug}` to verify

   {If approved:}
   1. Review REVIEW document
   2. Proceed to `/wrapup {task-slug}` when ready
   ```

## Important Notes

- Uses **REVIEWER agent** for consistent analysis
- Review is **project-aware** based on CLAUDE.md context
- Creates detailed findings with **file:line** references
- Provides **actionable recommendations** with code examples
- Auto-updates TODO.md with:
  - REVIEW document link
  - Status: review
  - Updated timestamp
- Can run **multiple times** (iterative review)
- Should complete in 3-5 minutes
- This is Step 4 of 5 - run after `/execute` and before `/wrapup`

## Error Handling

- If no changes to review: Show message
- If task-slug provided but not found: List tasks
- If REVIEWER agent unavailable: Fall back to basic analysis
- If vault path inaccessible: Show error

## Relationship to /execute

The `/review` command can be used:

1. **After /execute** - Review implementation before wrapup (recommended)
2. **Standalone** - Review any code changes, not tied to a task
3. **Multiple times** - Iterative review after fixes

```
/execute task-slug    # Implement
/review task-slug     # Review implementation
# Fix issues if any
/review task-slug     # Re-review (optional)
/wrapup task-slug     # Finalize
```
