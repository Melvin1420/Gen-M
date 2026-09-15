# Contibuting to Gen-M

## Branching
- 'main' is protected - never commit directly to it'
- work happens on 'feature/GEN-<n>-<short-slug>' branches, cut from 'main' (or the active rewrite branch).
- Merge via Pull Request only.

## Commit messages (Conventional Commits)
Format: '<type>: <description>'


Types: 'feat' , 'fix' , 'docs' , 'chore' , 'test' ,'refactor'

 Example: 'feat: add ticket creation endpoint'

 ## Before opening a PR
 - [ ] 'black . '-code is formatted
 - [ ] 'ruff check .' - no lint errors
 - [ ] 'pytest' - all tests pass
 