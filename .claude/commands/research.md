# /research - Research & Best Practices

Research a feature, problem, or technology before planning. This is **Step 1** of the 5-stage workflow.

## Model Configuration

```
model: opus
thinking: ultrathink
```

**IMPORTANT:** Use extended thinking mode for thorough research. Gather comprehensive information before making recommendations.

## Usage

```bash
/research $ARGUMENTS
```

## Arguments

`$ARGUMENTS` - Topic, feature, problem, or technology to research

## Workflow Position

```
[1. RESEARCH] → 2. Plan → 3. Execute → 4. Review → 5. Wrapup
     ↑
   YOU ARE HERE
```

## Implementation

You are a research specialist. Follow these steps:

### Phase 1: Context Gathering

**1. Web Search for Best Practices:**

```
WebSearch("$ARGUMENTS best practices 2025 2026")
WebSearch("$ARGUMENTS implementation patterns")
WebSearch("$ARGUMENTS common pitfalls mistakes")
```

**2. Explore Codebase for Related Patterns:**

```
Task(
  subagent_type="Explore",
  description="Find related code for $ARGUMENTS",
  prompt="Search for existing patterns, implementations, and dependencies related to: $ARGUMENTS. Look for similar features, related modules, and code that might be affected.",
  model="opus"
)
```

**3. Check Official Documentation (Context7):**

For library/framework topics:
```
mcp__context7__resolve-library-id(libraryName: "{relevant library}", query: "$ARGUMENTS")
mcp__context7__query-docs(libraryId: "{id}", query: "$ARGUMENTS best practices")
```

**4. Search Knowledge Base:**

```bash
# Search for prior learnings on this topic
Grep "{topic-keywords}" --glob "{vault-path}/knowledge-base/**/*.md"

# Search for related LEARNING documents
Grep "{topic-keywords}" --glob "{vault-path}/work-docs/**/LEARNING-*.md"

# Search for related SESSION solutions
Grep "{topic-keywords}" --glob "{vault-path}/work-docs/**/SESSION-*.md"

# Search for relevant PLANs
Grep "{topic-keywords}" --glob "{vault-path}/work-docs/**/PLAN-*.md"
```

**5. Check Project Context (if in repo):**

```bash
# Load vault path if available
if [[ -f ".claude/obsidian.json" ]]; then
    vault_path=$(jq -r '.vault_path' .claude/obsidian.json)
    project=$(jq -r '.project_name' .claude/obsidian.json)

    # Check project-specific context
    Read "${vault_path}/work-docs/${project}/context/README.md"
    Read "${vault_path}/work-docs/${project}/context/TECH_SPEC.md"
fi
```

### Phase 2: Analysis

Analyze findings with ultrathink depth:

**1. Problem Understanding:**
- What exactly needs to be solved?
- What are the constraints?
- What are the success criteria?
- What's the scope (narrow vs broad)?

**2. Approach Identification:**
- Identify 2-3 possible approaches
- List pros/cons for each
- Evaluate complexity and risk
- Consider maintenance burden

**3. Compatibility Check:**
- How does this fit with existing architecture?
- What dependencies are required?
- Are there conflicts with current patterns?
- What's the migration/integration path?

**4. Prior Art Review:**
- What worked in similar projects?
- What pitfalls have others encountered?
- Are there industry standards?

### Phase 3: Research Summary Output

Generate a structured research summary:

```markdown
## Research Summary: $ARGUMENTS

**Date:** {YYYY-MM-DD}
**Researcher:** Claude (Opus + Ultrathink)

---

### Problem Understanding

**What:** {concise problem description}
**Why:** {business/technical motivation}
**Constraints:** {limitations, requirements, boundaries}
**Success Criteria:** {how we'll know it works}

---

### Best Practices Found

| Source | Key Recommendation | Relevance |
|--------|-------------------|-----------|
| {source 1} | {recommendation} | High/Medium/Low |
| {source 2} | {recommendation} | High/Medium/Low |
| {source 3} | {recommendation} | High/Medium/Low |

---

### Recommended Approaches

#### Option A: {name} (Recommended)

**Description:** {approach details}

**Pros:**
- {advantage 1}
- {advantage 2}
- {advantage 3}

**Cons:**
- {disadvantage 1}
- {disadvantage 2}

**Complexity:** Low/Medium/High
**Risk:** Low/Medium/High
**Estimated Effort:** {rough estimate}

#### Option B: {name}

**Description:** {approach details}

**Pros:** {list}
**Cons:** {list}
**Complexity:** {level}
**Risk:** {level}

#### Option C: {name} (if applicable)

**Description:** {approach details}
**Pros:** {list}
**Cons:** {list}

---

### Existing Code Patterns

| File | Pattern | Relevance |
|------|---------|-----------|
| `{path}` | {pattern description} | {how it relates} |
| `{path}` | {pattern description} | {how it relates} |

---

### Dependencies Required

| Dependency | Purpose | Version | Notes |
|------------|---------|---------|-------|
| {dep 1} | {why needed} | {version} | {any concerns} |
| {dep 2} | {why needed} | {version} | {any concerns} |

---

### Potential Pitfalls

1. **{Pitfall 1}:** {description and how to avoid}
2. **{Pitfall 2}:** {description and how to avoid}
3. **{Pitfall 3}:** {description and how to avoid}

---

### Prior Knowledge (from vault)

**Related Sessions:**
- [[SESSION-related-task]] - {relevant insight}

**Learnings Applied:**
- {what we learned from similar work}

---

### Sources

- [{title 1}]({url})
- [{title 2}]({url})
- [{title 3}]({url})
- Context7: {library-id} (official docs)

---

## Recommendation

**Proceed with:** Option {A/B/C}

**Rationale:** {2-3 sentence explanation of why this approach is best}

**Key Considerations:**
1. {important consideration 1}
2. {important consideration 2}

---

## Next Step

Ready to plan implementation:
```
/myplan {suggested-task-slug-based-on-research}
```
```

### Phase 4: Validation

**STOP and validate with user:**

```markdown
## Research Complete

**Topic:** $ARGUMENTS
**Approaches Found:** {N}
**Recommended:** {Option name}

**Questions for you:**
1. Does this research address your needs?
2. Should I explore any approach in more detail?
3. Are there constraints I missed?
4. Ready to proceed with `/myplan`?
```

## Quick Research Mode

For faster research on familiar topics:

```bash
/research --quick $ARGUMENTS
```

This skips deep exploration and focuses on:
1. Quick web search (1-2 queries)
2. Codebase pattern check
3. Brief recommendation
4. Skip Context7 and knowledge base search

## Integration with MCP Servers

| MCP Server | When to Use |
|------------|-------------|
| Context7 | Official library documentation, API references |
| Sequential | Complex multi-step analysis requiring structured thinking |
| WebSearch | Current best practices, tutorials, blog posts |
| Playwright | Research requiring live website interaction |

## Best Practices

- **Ultrathink research** - Deep information gathering with extended thinking
- **Multiple sources** - Web, official docs, codebase, knowledge base
- **Structured output** - Clear recommendations with pros/cons
- **Human-in-the-loop** - Validation before planning
- **Source attribution** - Always cite references
- **Prior art search** - Check vault for related work

## Error Handling

- **No relevant results:** Broaden search terms, try alternative queries
- **Context7 unavailable:** Fall back to web search for documentation
- **Vault not linked:** Skip knowledge base search, note limitation
- **Ambiguous topic:** Ask clarifying questions before researching

## Output Location

Research output is displayed directly (no document created).

To save research for later reference:
1. Copy output to clipboard
2. Create note in `knowledge-base/research/` if valuable
3. Reference in PLAN document when created

## Next Steps

After research approval:
```bash
/myplan {feature-based-on-research-findings}
```

## Notes

- Always use Opus model for comprehensive research
- Enable ultrathink for thorough analysis
- Cite sources for all recommendations
- Consider existing codebase patterns
- Research before planning, not during
- This command does NOT create documents - it informs the next step
