# Snapshots

The snapshot feature lets you capture the state of a profile's variables at a
point in time and restore them later.

## Commands

### Create a snapshot

```bash
envault snapshot create <profile> [--label <label>]
```

You will be prompted for the profile password.  
An optional `--label` makes the snapshot easier to identify.

```
Snapshot created: prod_1718000000_pre-deploy
```

### List snapshots

```bash
# All snapshots
envault snapshot list

# Only snapshots for a specific profile
envault snapshot list prod
```

Output example:

```
prod_1718000000_pre-deploy  [pre-deploy]  (prod)
prod_1718001234             (prod)
```

### Restore a snapshot

```bash
envault snapshot restore <snapshot_id>
```

The profile is overwritten with the variables stored in the snapshot.  
You must supply the **current** encryption password — the restored data is
re-encrypted with the same password.

### Delete a snapshot

```bash
envault snapshot delete <snapshot_id>
```

You will be asked to confirm before the snapshot file is removed.

## Storage

Snapshots are stored as plain JSON files (unencrypted) under:

```
~/.envault/snapshots/<snapshot_id>.json
```

> **Note:** Snapshot files are not encrypted. Avoid storing sensitive values
> in profiles if your `~/.envault` directory is not otherwise protected.

## Audit log

Every `create`, `restore`, and `delete` action is recorded in the envault
audit log so you have a full history of snapshot activity.
