# Ports, Configuration Files, Ansible, and Scripts

## Root Docker Compose Stack (`docker-compose.yml`)

| Service | Image | Host Port | Key Volume Mounts |
| :--- | :--- | :--- | :--- |
| `prometheus` | `prom/prometheus:latest` | `9090:9090` | `./configs/prometheus/prometheus.yml`, `./configs/prometheus/rules` |
| `grafana` | `grafana/grafana:latest` | `3000:3000` | `grafana-storage`, `./configs/grafana/provisioning`, `./examples/dashboards` |
| `node-exporter` | `prom/node-exporter:latest` | `9100:9100` | `/proc:/host/proc:ro`, `/sys:/host/sys:ro`, `/:/rootfs:ro` |
| `cadvisor` | `gcr.io/cadvisor/cadvisor:latest` | `8080:8080` | `/`, `/var/run`, `/sys`, `/var/lib/docker/` |
| `sample-app` | `prom/prometheus-example-app` | `8081:8080` | None (`monitoring` network) |

- Compose network: `monitoring` (`bridge`); default Grafana login: `admin` / `admin`.

## Synthetic Metrics Generator (`scripts/generate-metrics.py`)

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--port` | `8082` | HTTP port exposing `/metrics` |
| `--verbose`, `-v` | `False` | Enable request and metric generation logging |

## Provisioning & Configuration Inventory

- **Prometheus config:** `configs/prometheus/prometheus.yml` (`scrape_interval: 15s`, `rules/*.yml`)
- **Prometheus alert rules:** `configs/prometheus/rules/basic-alerts.yml`, `examples/alerts/sample-alerts.yml`
- **Grafana provisioning:** `configs/grafana/provisioning/datasources/prometheus.yml`, `configs/grafana/provisioning/dashboards/dashboards.yml`
- **Sample dashboard:** `examples/dashboards/system-overview.json` (`System Overview`, `schemaVersion: 30`)
- **Config generator (`configuration/`):** `grafana_config.html`, `grafana_enhanced.json` (FR), `grafana_enhanced_en.json` (EN), `grafana.json`, `grafana.txt`

## Automation Scripts & Ansible Playbooks

- **Compose lifecycle (`scripts/setup.sh`):** subcommands `start`, `stop`, `restart`, `logs`, `status`
- **Grafana + Nginx on Ubuntu (`scripts/grafana/`):** `run_all.sh`, `01_install_grafana.sh`, `02_install_nginx.sh`, `03_configure_nginx_proxy.sh`, `04_configure_firewall.sh`
- **Host / Exporter scripts (`scripts/`):** `backup.sh`, `backup_prometheus.sh`, `check_openalerts_prom.sh`, `check_virtualbox_prom.sh`, `config_minikube.sh`, `install_cadvisor.sh`, `install_influxdb.sh`, `install_node_exporter.sh`, `install_ubuntu.sh`, `generate-metrics.py`
- **Ansible playbooks (`ansible/playbooks/`):** `monitoring.yml`, `grafana.yml`, `prometheus.yml`, `loki.yml`, `exporter.yml`, `metricbeat.yml` (documented in `ansible/doc/doc_*.md` EN and `doc_*_fr.md` FR)
- **Standalone Docker builds (`docker/`):** 15 service folders (`grafana`, `prometheus`, `loki`, `node_exporter`, `cadvisor`, plus 10 exporters) and `docker/docker-compose.yml`
