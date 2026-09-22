# Claude Code: Restricting Access to the Project Folder and Limiting Commands

Guidance for running Claude Code (CLI) on this repo with least-privilege permissions. Two layers are needed: **permission rules** and the **OS-level sandbox**. Neither is sufficient alone.

## Why both layers

| Layer | What it governs | Enforced by |
|---|---|---|
| Permission rules | Built-in file tools (Read, Edit, Write, Grep, Glob). Also gate every other tool, including Bash, before it runs. | Claude Code process |
| Sandbox | Bash and every child process it spawns (`cat`, `python`, `npm`, `git`, ...). Does **not** govern the built-in Read tool. | OS kernel |

A `Read(./.env)` deny rule blocks the Read tool but does **not** stop `cat .env` in Bash. The sandbox is what actually enforces folder boundaries for shell commands.

## Setup

1. **Launch from the project root.** Everything is scoped relative to the working directory. With the sandbox enabled, writes are limited to the current directory and its subdirectories. Reads, however, default to the whole machine except certain denied directories, so explicitly deny reads of `~/.aws`, `~/.ssh`, and similar.
2. **Enable the sandbox** by running `/sandbox` inside Claude Code. Supported on macOS, Linux and WSL2 (not native Windows).
3. **Commit project settings** to `.claude/settings.json` so the whole team shares the same rules.

### Example `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(pytest *)",
      "Bash(python -m pytest *)",
      "Bash(ruff *)",
      "Bash(docker build *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(terraform plan *)",
      "Bash(docker push *)"
    ],
    "deny": [
      "Bash(sudo *)",
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(aws *)",
      "Bash(terraform apply *)",
      "Bash(terraform destroy *)",
      "Read(.env*)",
      "Read(~/.aws/**)",
      "Read(~/.ssh/**)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/.aws", "~/.ssh"]
    }
  }
}
```

### How rules are evaluated

Rules are evaluated in order: **deny → ask → allow**, and the first match wins. A deny rule blocks a call even if a broader allow rule would match. If nothing matches, Claude Code falls back to the session's default mode (a prompt in normal mode).

### Verify

- Run `/permissions` to audit the active rules. Pattern syntax has shifted between Claude Code versions, so confirm your rules show up as expected.
- Run `/sandbox` to confirm the sandbox is enabled.

## Caveats for a DevOps / AWS workflow

- **Bash patterns are not a security boundary.** They are string matches, and there are public bug reports of deny patterns (e.g. `Bash(*gcloud*)`) not being honored in some configurations. Treat the sandbox and IAM as the real controls; command lists mainly reduce prompts and accidents.
- **Credentials are the biggest risk.** `AWS_*` environment variables or a default profile in your shell are inherited by every subprocess. Either:
  - launch Claude from a shell with no AWS credentials, or
  - give it a separate read-only / plan-only profile scoped to a sandbox account.

  Run the actual `terraform apply` and ECS deploys yourself or from CI.
- **Keep network isolation on.** The sandbox routes traffic through a proxy that only allows approved domains and prompts on new ones. Filesystem isolation without network isolation still leaves an exfiltration path.
- **Avoid `--dangerously-skip-permissions`** on your host machine. It is only reasonable inside an isolated container with no internet access.
- **For a hard boundary**, run Claude Code in a devcontainer or Docker container with only the repo mounted. That holds regardless of settings.

## References

- Sandboxing: https://docs.claude.com/en/docs/claude-code/sandboxing
- Permissions: https://code.claude.com/docs/en/permissions
