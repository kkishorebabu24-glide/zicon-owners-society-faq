# Commit Conventions

This project follows **Conventional Commits** specification for consistent, structured commit messages. This enables automated changelog generation, semantic versioning, and clear project history.

## Format

```
<type>(<scope>): <description>

<body>

<footer>
```

### Type

Must be one of:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes only
- **style**: Changes that don't affect code meaning (formatting, semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding or updating tests
- **chore**: Changes to build process, dependencies, tools, or CI configuration
- **ci**: Changes to CI/CD configuration files and scripts
- **revert**: Reverts a previous commit

### Scope (Optional but Recommended)

The scope indicates the part of the codebase affected. Choose from:
- **auth**: Authentication and authorization
- **telegram**: Telegram bot integration
- **digest**: AI digest generation
- **demand-supply**: Offers/requests matching
- **api**: API endpoints
- **db**: Database related changes
- **frontend**: React/UI changes
- **ui**: User interface
- **security**: Security improvements
- **performance**: Performance optimizations
- **test**: Test infrastructure
- **docker**: Docker/containerization
- **docs**: Documentation
- **ci**: CI/CD pipeline
- **config**: Configuration files
- **deps**: Dependency updates

### Description

- Use imperative mood ("add feature" not "added feature" or "adds feature")
- Don't capitalize first letter
- No period (.) at the end
- Max 50 characters (excluding scope and type)
- Be specific and concise

### Body

- Optional but encouraged for non-trivial changes
- Explain **what** and **why**, not **how**
- Wrap at 72 characters
- Separate from description by blank line
- Use bullet points or paragraphs

### Footer

- Optional
- Used for breaking changes and issue references
- Breaking changes start with `BREAKING CHANGE:`
- Close issues with `Closes #issue-number` or `Fixes #issue-number`

## Examples

### Simple Feature
```
feat(auth): add JWT token refresh endpoint
```

### Feature with Body
```
feat(telegram): implement group message listener

- Monitor multiple Telegram groups simultaneously
- Parse message metadata and user information
- Queue messages for processing in background worker
- Add reconnection logic with exponential backoff
```

### Bug Fix
```
fix(digest): correct timestamp in daily summary

Timestamps were displayed in UTC instead of user timezone.
Updated to use user's configured timezone for all digest times.

Closes #456
```

### Breaking Change
```
feat(api)!: change digest API response format

BREAKING CHANGE: The digest endpoint now returns an array instead of object.
Old: { digest: "..." }
New: [{ id: 1, content: "..." }]

Migration required: Update client code to access items by index.

Closes #789
```

### Fix with Breaking Change
```
fix(db)!: migrate user table to new schema

BREAKING CHANGE: User.phone_number field renamed to User.contact_phone

Migration script: python scripts/migrate_users.py

Closes #234
```

### Performance Improvement
```
perf(api): optimize digest query with database indexing

- Added composite index on (user_id, created_at)
- Reduced query time from 2s to 150ms for most users
- Benchmark results: see PR description

Closes #567
```

### Documentation Update
```
docs: add setup instructions for PostgreSQL

- Added step-by-step installation guide
- Included Windows, macOS, and Linux procedures
- Added troubleshooting section
```

### Dependency Update
```
chore(deps): upgrade fastapi to 0.104.0

- Fixes security vulnerability in query parsing
- Includes performance improvements for large payloads
```

### Refactor with Test
```
refactor(digest): extract summarization logic to service

- Move AI summarization from route to service layer
- Improves testability and code reusability
- Add unit tests for summarization edge cases
```

### CI/CD Update
```
ci: add CodeQL security scanning to GitHub Actions

- Scan for common vulnerability patterns
- Run on every push to develop/main
- Generate security report in GitHub Security tab
```

### Multiple Changes (Rare)
```
feat(auth, api): add user logout and session management

- Implement logout endpoint
- Add session token expiration
- Clear refresh tokens on logout
- Add comprehensive test coverage
```

## Rules

### DO ✅
- Use imperative mood
- Be specific and concise
- Capitalize scope properly: `auth`, `telegram`, `api`
- Reference issues: `Closes #123`
- Use breaking change footer for API changes
- Keep subject line under 50 characters
- Include body for complex changes
- Use lowercase for type and scope
- Use exclamation mark for breaking changes: `feat!:` or `feat(scope)!:`

### DON'T ❌
- Don't use capitalization in description
- Don't add period at end of description
- Don't write "Fixed bug in authentication" (use imperative)
- Don't put multiple issues in one commit (when possible)
- Don't force unrelated changes into one commit
- Don't use vague descriptions like "fix bugs" or "update code"
- Don't make subject line too long

## Automatic Changelog Generation

Commits following this convention generate changelogs automatically:

```bash
# View upcoming changes for new version
git log develop..HEAD --oneline --format="%h %s"

# View all changes since last release
git log v1.0.0..HEAD --oneline
```

Changelog groups:
- **Features**: All `feat:` commits
- **Bug Fixes**: All `fix:` commits
- **Performance**: All `perf:` commits
- **Breaking Changes**: All commits with `BREAKING CHANGE:`

## Pre-commit Validation

This project uses pre-commit hooks to validate commit messages.

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks
pre-commit install --hook-type commit-msg

# The hook validates your commit message before allowing the commit
```

If your commit message doesn't follow conventions, the commit will fail:
```
✓ Commit message follows Conventional Commits
✗ Commit message does not follow Conventional Commits

Example of correct format:
  feat(auth): add login endpoint
  fix(api): handle null responses
  docs: update README
```

## Commit Message Template

Use this template to help write commits:

```bash
# Set up commit message template
git config commit.template .gitmessage
```

Template file (`.gitmessage`):
```
# <type>(<scope>): <description>
# |<----   Preferred max width (50 chars)    --->|
#
# Explain why this change is being made
# |<----   Max width (72 chars)                -->|
#
# Provide examples of the change
#
# Closes #(issue)
```

## Interactive Rebase for Fixup

Clean up commits before merging:

```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Use 'reword' to edit commit message
# Use 'squash' to combine with previous commit
# Use 'fixup' to combine without keeping message
```

Example:
```
pick abc1234 feat(auth): add login endpoint
pick def5678 fix: update variable name
pick ghi9012 fix: correct import

# Change to:
pick abc1234 feat(auth): add login endpoint
fixup def5678 fix: update variable name
fixup ghi9012 fix: correct import

# Result: single commit with message "feat(auth): add login endpoint"
```

## Integration with GitHub

### Auto-linking Issues

Commit message automatically links to issue:
```
fix(api): handle empty responses

Closes #456  <- This closes issue #456 automatically
```

### Release Notes

GitHub automatically generates release notes from conventional commits:
- Features and enhancements
- Bug fixes
- Breaking changes

## Tools

- **[Commitizen](http://commitizen.github.io/)**: Interactive CLI for writing commits
- **[Husky](https://typicode.github.io/husky/)**: Git hooks for validation
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Official specification

## FAQ

**Q: My commit has multiple unrelated changes. What should I do?**
A: Split into multiple commits. You can use `git add -p` (patch mode) to stage specific changes.

**Q: Can I use `feat:` for both frontend and backend?**
A: Use scope to clarify: `feat(backend):` or `feat(frontend):`

**Q: Should I include issue number in description or footer?**
A: Use footer: `Closes #123` links the issue automatically.

**Q: What if I made a typo in commit message?**
A: Amend the commit: `git commit --amend` (if not pushed yet)

**Q: Can I revert a commit?**
A: Yes: `git revert <commit-hash>` creates a new commit that undoes changes.

## References

- [Conventional Commits Spec](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)
- [Semantic Versioning](https://semver.org/)
