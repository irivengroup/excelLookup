# Excel Host Lookup

Recherche locale de `Hostname -> IPv4 + FQDN` dans un classeur Excel multi-feuilles.

## Fonctionnement

- détecte automatiquement les colonnes Hostname, IP et DNS Name/FQDN ;
- accepte un fichier texte de hosts à rechercher ;
- conserve les doublons et signale les conflits IP/FQDN ;
- produit un CSV par feuille ;
- supprime les espaces des noms de feuilles dans les noms de fichiers ;
- produit aussi un CSV global ;
- aucun accès réseau n'est effectué.

## Installation

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -e ".[dev,xls]"
```

`xls` est nécessaire uniquement pour les anciens fichiers `.xls`.

## Utilisation

Avec détection automatique du premier Excel :

```bash
excel-host-lookup hosts.txt
```

Avec fichiers explicites :

```bash
excel-host-lookup inventory.xlsx hosts.txt
```

Répertoire de sortie :

```bash
excel-host-lookup inventory.xlsx hosts.txt --output-dir results
```

Sans fichier hosts, tous les hostnames détectés dans l'Excel sont recherchés :

```bash
excel-host-lookup inventory.xlsx
```

## Format hosts.txt

```text
srv-app-01
srv-db-01
srv-web-01.example.com
# commentaire
```

Les lignes vides et commentaires sont ignorés.

## Sorties

Pour les feuilles :

```text
Production Servers
Database
```

les fichiers deviennent :

```text
inventory_ProductionServers.csv
inventory_Database.csv
inventory_RESULTATS.csv
```

Colonnes :

```text
Hostname
IP_Trouvee
FQDN_Trouve
Statut
Conflit_IP
Conflit_FQDN
Sources
```

`Statut` vaut `OK`, `CONFLIT` ou `NON_TROUVE`.

## Validation

```bash
ruff check .
ruff format --check .
mypy src
bandit -r src
pytest --cov=excel_host_lookup --cov-report=term-missing
```
