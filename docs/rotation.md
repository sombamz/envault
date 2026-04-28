# Key Rotation

envault supports **key rotation** — re-encrypting a profile's secrets under a
new master password without losing any data.

## Why rotate?

- A team member who knew the old password has left the project.
- Routine security hygiene / compliance requirements.
- The old password was accidentally exposed.

## Usage

```bash
# Interactive (recommended — passwords are not echoed)
envault rotation rotate myapp

# Non-interactive (e.g. in a CI script — use with care)
envault rotation rotate myapp \
  --old-password "$OLD_PASS" \
  --new-password "$NEW_PASS"
```

### What happens internally

1. The profile vault file is **decrypted** with the old password.
2. The plaintext data is immediately **re-encrypted** with the new password.
3. The vault file is **overwritten** — the old ciphertext is gone.
4. An **audit log** entry is written recording the event (but never the passwords).

## Audit trail

Every rotation attempt — successful or not — is recorded in the audit log:

```bash
envault audit log
```

Example output:

```
2024-06-01T12:34:56+00:00  rotate_key  myapp  success=True
```

## Error handling

| Situation | Behaviour |
|---|---|
| Wrong old password | Command exits with code 1; vault unchanged |
| Profile not found | Command exits with code 1 |
| Old == new password | Command exits with code 1 before touching the vault |

## Notes

- The `--new-password` flag uses `confirmation_prompt` in interactive mode so
  you must type the new password **twice** to prevent typos.
- Rotation is **atomic at the file level** — the vault is only overwritten once
  the new ciphertext has been successfully produced.
