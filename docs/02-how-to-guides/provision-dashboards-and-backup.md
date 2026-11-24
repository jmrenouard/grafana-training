# Provision Dashboards and Back Up Grafana

This procedure validates dashboard JSON files, reloads Grafana dashboard configuration, and runs a local backup archive.

## Prerequisites

- The five containers run on the host (`./scripts/setup.sh status`).
- `jq` and `curl` exist on the host.
- Grafana responds on `http://localhost:3000`.

## Procedure

1. Validate JSON syntax across the dashboard examples before container reload.

```bash
python3 -c "import json, pathlib; json.loads(pathlib.Path('examples/dashboards/system-overview.json').read_text())"
```

2. Inspect the provisioned dashboard path inside the Grafana container.

```bash
docker compose exec grafana ls -la /var/lib/grafana/dashboards
```

3. Restart the Grafana container so it loads new dashboard files.

```bash
docker compose restart grafana
```

4. Grant execute permissions to the backup script and run it.

```bash
chmod +x scripts/backup.sh
./scripts/backup.sh
```

NOTE: `scripts/backup.sh` writes timestamped JSON exports and tar archives into `./backups/`.

## Verification

1. List the `./backups/` directory to confirm that the archive file exists.

```bash
ls -lh backups/
```

2. Check Grafana startup logs for errors.

```bash
docker compose logs grafana | grep -i provision
```

## Rollback

WARNING: Do not keep backup files with unencrypted credentials or tokens on shared hosts.

If a malformed JSON file breaks dashboard import, restore the prior file and restart Grafana:

```bash
git checkout -- examples/dashboards/system-overview.json
docker compose restart grafana
```
