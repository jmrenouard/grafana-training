# Ports, fichiers de configuration et scripts

## Services Docker Compose racine (`docker-compose.yml`)

| Service | Image | Port hôte | Volumes principaux |
| :--- | :--- | :--- | :--- |
| `prometheus` | `prom/prometheus:latest` | `9090:9090` | `./configs/prometheus/prometheus.yml`, `./configs/prometheus/rules` |
| `grafana` | `grafana/grafana:latest` | `3000:3000` | `grafana-storage`, `./configs/grafana/provisioning`, `./examples/dashboards` |
| `node-exporter` | `prom/node-exporter:latest` | `9100:9100` | `/proc:/host/proc:ro`, `/sys:/host/sys:ro`, `/:/rootfs:ro` |
| `cadvisor` | `gcr.io/cadvisor/cadvisor:latest` | `8080:8080` | `/`, `/var/run`, `/sys`, `/var/lib/docker/` |
| `sample-app` | `prom/prometheus-example-app` | `8081:8080` | Aucun (réseau `monitoring`) |

- Réseau Docker : `monitoring` (`bridge`) ; identifiants Grafana par défaut : `admin` / `admin`.

## Générateur de métriques (`scripts/generate-metrics.py`)

| Option | Valeur par défaut | Description |
| :--- | :--- | :--- |
| `--port` | `8082` | Port HTTP exposant `/metrics` |
| `--verbose`, `-v` | `False` | Active les journaux détaillés |

## Inventaire des fichiers de configuration et scripts

- **Configuration Prometheus :** `configs/prometheus/prometheus.yml` (`scrape_interval: 15s`, `rules/*.yml`)
- **Règles d'alerte :** `configs/prometheus/rules/basic-alerts.yml`, `examples/alerts/sample-alerts.yml`
- **Provisionnement Grafana :** `configs/grafana/provisioning/datasources/prometheus.yml`, `configs/grafana/provisioning/dashboards/dashboards.yml`
- **Tableau de bord :** `examples/dashboards/system-overview.json` (`System Overview`, `schemaVersion: 30`)
- **Générateur `grafana.ini` :** `configuration/grafana_config.html`, `grafana_enhanced.json` (FR), `grafana_enhanced_en.json` (EN)
- **Scripts racine (`scripts/`) :** `setup.sh`, `generate-metrics.py`, `backup.sh`, `backup_prometheus.sh`, `check_openalerts_prom.sh`, `check_virtualbox_prom.sh`, `config_minikube.sh`, `install_cadvisor.sh`, `install_influxdb.sh`, `install_node_exporter.sh`, `install_ubuntu.sh`
- **Scripts Ubuntu (`scripts/grafana/`) :** `run_all.sh`, `01_install_grafana.sh` à `04_configure_firewall.sh`
- **Ansible (`ansible/`) :** `playbooks/{monitoring,grafana,prometheus,loki,exporter,metricbeat}.yml` et documentation bilingue dans `ansible/doc/`
