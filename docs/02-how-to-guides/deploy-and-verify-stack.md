# Deploy and Verify the Monitoring Stack

This procedure validates the Docker Compose manifest, starts the five containers, and checks Prometheus targets.

## Prerequisites

- Docker Engine and Docker Compose V2 exist on the host.
- Ports `3000`, `8080`, `8081`, `9090`, and `9100` are free on localhost.
- Bash and `curl` exist on the host.

## Procedure

1. Validate the Compose file syntax before you start the containers.

```bash
docker compose -f docker-compose.yml config -q
```

2. Validate the YAML syntax of the Prometheus scrape file and alert rules.

```bash
python3 -c "import yaml, pathlib; [yaml.safe_load(pathlib.Path(p).read_text()) for p in ('configs/prometheus/prometheus.yml', 'configs/prometheus/rules/basic-alerts.yml')]"
```

3. Grant execute permissions to the stack helper script.

```bash
chmod +x scripts/setup.sh
```

4. Start the five containers in detached mode.

```bash
./scripts/setup.sh start
```

5. Check container status after 10 seconds.

```bash
./scripts/setup.sh status
```

## Verification

1. Probe the Grafana health endpoint on port `3000`.

```bash
curl -fsS http://localhost:3000/api/health
```

2. Probe the Prometheus readiness endpoint on port `9090`.

```bash
curl -fsS http://localhost:9090/-/ready
```

3. Query active targets on port `9090` to confirm that scrapes succeed.

```bash
curl -fsS http://localhost:9090/api/v1/targets
```

## Rollback

CAUTION: Add `-v` only if you want to remove local Grafana storage volumes.

To stop and remove all lab containers, run the stop command:

```bash
./scripts/setup.sh stop
```
