# Provisionner les dashboards et sauvegarder Grafana

Cette procédure valide les fichiers JSON, recharge les tableaux de bord Grafana et crée une sauvegarde locale.

## Prérequis

- Les conteneurs de supervision tournent sur l'hôte (`./scripts/setup.sh status`).
- `jq` et `curl` existent sur l'hôte.
- Grafana répond sur le port `3000`.

## Procédure

1. Validez la syntaxe JSON du tableau de bord avant le rechargement.

```bash
python3 -c "import json, pathlib; json.loads(pathlib.Path('examples/dashboards/system-overview.json').read_text())"
```

2. Listez les fichiers de tableaux de bord dans le conteneur Grafana.

```bash
docker compose exec grafana ls -la /var/lib/grafana/dashboards
```

3. Redémarrez le conteneur Grafana pour charger les modifications.

```bash
docker compose restart grafana
```

4. Ajoutez les droits d'exécution sur le script de sauvegarde puis lancez la sauvegarde.

```bash
chmod +x scripts/backup.sh
./scripts/backup.sh
```

NOTE : Le script `scripts/backup.sh` écrit une archive datée dans `./backups/`.

## Vérification

1. Listez le répertoire `./backups/` pour confirmer la présence de l'archive.

```bash
ls -lh backups/
```

2. Examinez les journaux Grafana pour détecter une erreur de provisionnement.

```bash
docker compose logs grafana | grep -i provision
```

## Retour arrière

AVERTISSEMENT : Ne laissez aucune sauvegarde non chiffrée avec des jetons sur un hôte partagé.

Si un fichier JSON invalide bloque le chargement, restaurez l'état initial puis redémarrez Grafana :

```bash
git checkout -- examples/dashboards/system-overview.json
docker compose restart grafana
```
