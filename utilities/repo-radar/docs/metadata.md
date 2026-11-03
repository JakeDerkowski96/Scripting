# `.project.toml`

Lives at the root of each repo and holds the facts git cannot know.

```toml
summary = "Backs up portfolio folders into a git repo as timestamped commits"
stage = "active"
next = "Add dry-run flag"
blockers = []
tags = ["powershell", "automation"]
```

| Key | Type | Notes |
|---|---|---|
| `summary` | string | What the project is, in one line |
| `stage` | string | One of the stages below. Unset triggers the `no-meta` flag |
| `visibility` | string | Expected GitHub visibility: `public`, `private` or `internal`. repo-radar flags `visibility-mismatch` if GitHub disagrees, and `visibility-unknown` if it could not check (`gh` missing, skipped or failing). Ignored for repos with no remote |
| `next` | string | The next concrete step |
| `blockers` | list of strings | What is in the way |
| `tags` | list of strings | Free-form, searchable |

## Stages

| Stage | Meaning |
|---|---|
| `idea` | Not started; a note to self |
| `prototype` | Exploring; may be thrown away |
| `active` | Being worked on now |
| `maintenance` | Works; only occasional fixes |
| `paused` | Intentionally on hold |
| `archived` | Abandoned or superseded |
| `done` | Finished |

An unknown stage makes the file invalid (`bad-meta`) rather than being silently accepted.
