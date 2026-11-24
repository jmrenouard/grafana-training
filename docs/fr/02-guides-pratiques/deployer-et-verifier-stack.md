# Déployer et vérifier la stack de monitoring

Cette procédure valide le fichier Docker Compose, démarre les cinq conteneurs et vérifie les cibles Prometheus.

## Prérequis

- Docker Engine et Docker Compose V2 fonctionnent sur l'hôte.
- Les ports `3000`, `8080`, `8081`, `9090` et `9100` sont libres.
- Bash et `curl` existent sur l'hôte.

## Procédure

1. Validez la syntaxe du fichier Compose avant le démarrage des conteneurs.

```bash
docker compose -f docker-compose.yml config -q
```

2. Validez la syntaxe YAML de Prometheus et des règles d'alerte.

```bash
python3 -c "import yaml, pathlib; [yaml.safe_load(pathlib.Path(p).read_text()) for p in ('configs/prometheus/prometheus.yml', 'configs/prometheus/rules/basic-alerts.yml')]"
```

3. Ajoutez les droits d'exécution sur le script de gestion.

```bash
chmod +x scripts/setup.sh
```

4. Démarrez les cinq conteneurs en arrière-plan.

```bash
./scripts/setup.sh start
```

5. Affichez l'état des conteneurs après dix secondes.

```bash
./scripts/setup.sh status
```

## Vérification

1. Interrogez le point de vérification Grafana sur le port `3000`.

```bash
curl -fsS http://localhost:3000/api/health
```

2. Interrogez le point de vérification Prometheus sur le port `9090`.

```bash
curl -fsS http://localhost:9090/-/ready
```

3. Listez les cibles actives sur le port `9090`.

```bash
curl -fsS http://localhost:9090/api/v1/targets
```

Confirmez que chaque cible retourne l'état `up`.

## Retour arrière

ATTENTION : Ajoutez `-v` uniquement si vous voulez supprimer les volumes de données Grafana.

Pour arrêter et retirer les conteneurs du laboratoire, exécutez la commande d'arrêt :

```bash
./scripts/setup.sh stop
```
