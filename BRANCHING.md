# Branching Strategy

This document describes the Git branching strategy used in the Society App project, following **Git Flow** with modifications for CI/CD best practices.

## Branch Types

### 1. **Main Branch** (`main`)
- **Purpose**: Production-ready code only
- **Protection**: Requires PR review and all CI checks must pass
- **Deployment**: Automatically deployed to production
- **Naming**: `main`
- **Creation**: Never created directly; only via release branches
- **Deletion**: Never deleted

### 2. **Develop Branch** (`develop`)
- **Purpose**: Integration branch for features; always in a working state
- **Protection**: Requires PR review and CI checks
- **Deployment**: Deployed to staging environment
- **Naming**: `develop`
- **Source**: Created from `main` at project start
- **Deletion**: Never deleted

### 3. **Feature Branches** (`feature/*`)
- **Purpose**: Develop new features or enhancements
- **Naming Convention**: `feature/short-description` or `feature/issue-number-description`
  - ✅ `feature/telegram-integration`
  - ✅ `feature/123-ai-digest-engine`
  - ✅ `feature/user-authentication`
  - ❌ `feature` (too vague)
  - ❌ `telegram` (missing prefix)
- **Source**: Created from `develop`
- **Target for PR**: `develop`
- **Deletion**: Delete after merge (enable auto-delete in GitHub)
- **Lifetime**: Should be short-lived (1-4 weeks max)

### 4. **Bug Fix Branches** (`bugfix/*`)
- **Purpose**: Fix bugs in development/staging
- **Naming Convention**: `bugfix/issue-number-description` or `bugfix/short-description`
  - ✅ `bugfix/456-digest-timestamp-error`
  - ✅ `bugfix/telegram-message-parsing`
- **Source**: Created from `develop`
- **Target for PR**: `develop`
- **Deletion**: Delete after merge
- **Note**: If bug is critical in production, use `hotfix/*` instead

### 5. **Hotfix Branches** (`hotfix/*`)
- **Purpose**: Patch critical production bugs
- **Naming Convention**: `hotfix/issue-number-description`
  - ✅ `hotfix/789-security-vulnerability`
  - ✅ `hotfix/database-connection-crash`
- **Source**: Created from `main`
- **Target for PR**: `main` (then merge back to `develop`)
- **Deletion**: Delete after merge
- **Lifetime**: Should be completed ASAP (1-2 days max)
- **Process**:
  1. Create from `main`
  2. Merge PR into `main`
  3. Create PR from `main` to `develop`
  4. Delete branch

### 6. **Release Branches** (`release/*`)
- **Purpose**: Prepare production release; only bug fixes and version updates
- **Naming Convention**: `release/v1.0.0` or `release/1.0.0`
  - ✅ `release/v1.0.0`
  - ✅ `release/v1.1.0-rc.1` (release candidate)
- **Source**: Created from `develop` when ready for release
- **Target for PR**: `main`
- **Deletion**: Delete after merge
- **No new features**: Only critical bugfixes allowed
- **Process**:
  1. Create from `develop`
  2. Update version numbers, CHANGELOG
  3. Merge PR into `main`
  4. Tag version on `main`: `git tag -a v1.0.0 -m "Release v1.0.0"`
  5. Merge back to `develop`
  6. Delete branch

### 7. **Experimental/WIP Branches** (`experimental/*`, `wip/*`)
- **Purpose**: Exploratory work, spike investigations (not production code)
- **Naming Convention**: `experimental/ai-model-testing`, `wip/performance-optimization`
- **Source**: Can be created from any branch
- **Target for PR**: `develop` (after review and testing)
- **Deletion**: Delete after completion or abandonment
- **Note**: These branches should never be merged without explicit review

## Workflow Diagram

```
main (production)
  ↑
  ├─── release/v1.0.0
  │      ├─ Update version
  │      ├─ Update CHANGELOG
  │      └─ Merge to main (tag v1.0.0)
  │
develop (staging)
  ↑
  ├─── feature/telegram-integration ──┐
  │      ├─ Code development          │
  │      ├─ Tests                     │
  │      └─ PR to develop ────────────┘
  │
  ├─── feature/ai-digest-engine ──────┐
  │      ├─ Code development          │
  │      ├─ Tests                     │
  │      └─ PR to develop ────────────┘
  │
  └─── bugfix/issue-fix ──────────────┐
         ├─ Bug fix                    │
         ├─ Tests                     │
         └─ PR to develop ────────────┘

main ← hotfix branch (emergency fix)
  ↑
  └─── hotfix/security-issue
         ├─ Critical fix
         ├─ Tests
         └─ PR to main (then to develop)
```

## Commit Message Format

See [COMMIT_CONVENTIONS.md](./COMMIT_CONVENTIONS.md) for detailed commit message standards.

## Pull Request Process

### Before Creating a PR

1. **Update your branch with latest develop**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run local tests**:
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm test
   ```

3. **Run linting**:
   ```bash
   # Backend
   black .
   flake8 .

   # Frontend
   npm run lint -- --fix
   ```

### Creating a PR

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature
   ```

2. **Create PR on GitHub**:
   - **Target**: `develop` (or `main` for hotfix)
   - **Title**: Follow conventional commit format
   - **Description**: Include:
     - What changes were made
     - Why these changes are needed
     - Link to related issue (e.g., `Closes #123`)
     - Testing done
     - Screenshots (if applicable)

3. **Link to Issue**:
   ```
   Closes #123
   ```
   or
   ```
   Related to #456
   ```

### PR Review Checklist

Reviewers must verify:
- [ ] Code follows project standards
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes to APIs
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Commit messages follow conventions
- [ ] No secrets or sensitive data exposed

### Merging a PR

- **Squash and merge** for feature branches to keep history clean
- **Create a merge commit** for release branches
- **Rebase and merge** only if branch has single logical commit

```bash
# Squash and merge (recommended for features)
git checkout develop
git merge --squash feature/your-feature
git commit -m "feat: add telegram integration (#123)"
git push origin develop

# Or use GitHub UI button "Squash and merge"
```

## Branch Naming Conventions Summary

| Type | Pattern | Example | Source | Target |
|------|---------|---------|--------|--------|
| Feature | `feature/*` | `feature/user-auth` | develop | develop |
| Bugfix | `bugfix/*` | `bugfix/123-date-bug` | develop | develop |
| Hotfix | `hotfix/*` | `hotfix/456-crash` | main | main → develop |
| Release | `release/*` | `release/v1.0.0` | develop | main |
| Experimental | `experimental/*` | `experimental/ai-test` | any | develop |

## Local Setup

```bash
# Clone repository
git clone https://github.com/yourusername/society-app.git
cd society-app

# Set up Git hooks for pre-commit checks
pre-commit install

# Create a feature branch
git checkout -b feature/your-feature develop

# Work, commit, push, create PR
```

## Git Configuration Tips

```bash
# Show branch names in terminal prompt
# Add to your .bashrc or .zshrc:
# PS1='$(__git_ps1 "(%s)") > '

# Set up branch deletion after merge
git config --global branch.autosetuprebase always

# Always rebase when pulling
git config pull.rebase true

# Create aliases for common operations
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.features "branch -r | grep feature"
git config --global alias.hotfixes "branch -r | grep hotfix"
```

## FAQ

**Q: How do I sync my branch with the latest develop?**
```bash
git fetch origin
git rebase origin/develop
```

**Q: Can I merge `main` into my feature branch?**
A: No. Always rebase from `develop` only.

**Q: What if my feature takes longer than expected?**
A: Keep your branch updated with `git rebase origin/develop` regularly (at least weekly).

**Q: When should I use hotfix vs bugfix?**
A: Use `hotfix` only for critical production bugs. Use `bugfix` for issues in staging/development.

**Q: Can I push to develop directly?**
A: No. Branch protection requires PRs and CI checks.

## References

- [Git Flow Cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow vs Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows)
