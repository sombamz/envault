# envault

> A CLI tool to securely manage and inject environment variables across multiple project profiles.

---

## Installation

```bash
pip install envault
```

Or install from source:

```bash
git clone https://github.com/yourname/envault.git && cd envault && pip install .
```

---

## Usage

```bash
# Initialize a new vault in your project
envault init

# Add an environment variable to a profile
envault set --profile production DATABASE_URL="postgres://user:pass@host/db"

# List all variables in a profile
envault list --profile production

# Inject variables into a command
envault run --profile production -- python app.py

# Export variables to a .env file
envault export --profile staging > .env
```

Profiles are stored encrypted locally at `~/.envault/` and can be shared across projects by referencing a named profile at runtime.

---

## Profiles

| Command | Description |
|---|---|
| `envault init` | Initialize a new vault |
| `envault set` | Add or update a variable |
| `envault get` | Retrieve a variable |
| `envault run` | Inject variables and run a command |
| `envault export` | Export profile to stdout |

---

## License

[MIT](LICENSE) © 2024 Your Name