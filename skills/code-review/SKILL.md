---
name: code-review
description: Perform thorough code reviews with security, performance, and maintainability analysis. Use when user asks to review code, check for bugs, or audit a codebase.
---

# Code Review Skill

You now have expertise in conducting comprehensive code reviews. Follow this structured approach and prefer fast, repo-wide searches with `rg` (ripgrep).

## Review Checklist

### 1. Security (Critical)

Check for:
- [ ] **Injection vulnerabilities**: SQL, command, XSS, template injection
- [ ] **Authentication issues**: Hardcoded credentials, weak auth
- [ ] **Authorization flaws**: Missing access controls, IDOR
- [ ] **Data exposure**: Sensitive data in logs, error messages
- [ ] **Cryptography**: Weak algorithms, improper key management
- [ ] **Dependencies**: Known vulnerabilities (check with `npm audit`, `pip-audit`)

```bash
# Quick security scans
npm audit                    # Node.js
pip-audit                    # Python
cargo audit                  # Rust
rg -n "password|secret|api[_-]?key|token" --glob="*.py" --glob="*.js"
```

### 2. Correctness

Check for:
- [ ] **Logic errors**: Off-by-one, null handling, edge cases
- [ ] **Race conditions**: Concurrent access without synchronization
- [ ] **Resource leaks**: Unclosed files, connections, memory
- [ ] **Error handling**: Swallowed exceptions, missing error paths
- [ ] **Type safety**: Implicit conversions, any types

### 3. Performance

Check for:
- [ ] **N+1 queries**: Database calls in loops
- [ ] **Memory issues**: Large allocations, retained references
- [ ] **Blocking operations**: Sync I/O in async code
- [ ] **Inefficient algorithms**: O(n^2) when O(n) possible
- [ ] **Missing caching**: Repeated expensive computations

### 4. Maintainability

Check for:
- [ ] **Naming**: Clear, consistent, descriptive
- [ ] **Complexity**: Functions > 50 lines, deep nesting > 3 levels
- [ ] **Duplication**: Copy-pasted code blocks
- [ ] **Dead code**: Unused imports, unreachable branches
- [ ] **Comments**: Outdated, redundant, or missing where needed

### 5. Testing

Check for:
- [ ] **Coverage**: Critical paths tested
- [ ] **Edge cases**: Null, empty, boundary values
- [ ] **Mocking**: External dependencies isolated
- [ ] **Assertions**: Meaningful, specific checks

## Review Output Format

```markdown
## Code Review: [file/component name]

### Summary
[1-2 sentence overview]

### Critical Issues
1. **[Issue]** (line X): [Description]
   - Impact: [What could go wrong]
   - Fix: [Suggested solution]

### Improvements
1. **[Suggestion]** (line X): [Description]

### Positive Notes
- [What was done well]

### Verdict
[ ] Ready to merge
[ ] Needs minor changes
[ ] Needs major revision
```

## Common Patterns to Flag

### Python
```python
# Bad: SQL injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# Good:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Bad: Command injection
os.system(f"ls {user_input}")
# Good:
subprocess.run(["ls", user_input], check=True)

# Bad: Mutable default argument
def append(item, lst=[]):  # Bug: shared mutable default
# Good:
def append(item, lst=None):
    lst = lst or []
```

### JavaScript/TypeScript
```javascript
// Bad: Prototype pollution
Object.assign(target, userInput)
// Good:
Object.assign(target, sanitize(userInput))

// Bad: eval usage
eval(userCode)
// Good: Never use eval with user input

// Bad: Callback hell
getData(x => process(x, y => save(y, z => done(z))))
// Good:
const data = await getData();
const processed = await process(data);
await save(processed);
```

## Review Commands

```bash
# Show recent changes
git diff HEAD~5 --stat
git log --oneline -10

# Find potential issues
rg -n "TODO|FIXME|HACK|XXX" .
rg -n "password|secret|token|api[_-]?key" . --glob="*.py"

# Check complexity (Python)
pip install radon && radon cc . -a

# Check dependencies
npm outdated  # Node
pip list --outdated  # Python
```

## Review Workflow

1. **Understand context**: Read PR description, linked issues
2. **Run the code**: Build, test, run locally if possible
3. **Read top-down**: Start with main entry points
4. **Check tests**: Are changes tested? Do tests pass?
5. **Security scan**: Run automated tools
6. **Manual review**: Use checklist above
7. **Write feedback**: Be specific, suggest fixes, be kind
