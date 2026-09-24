# excel-host-lookup 2.2.0

Outil robuste de recherche de hosts dans des classeurs `.xlsx` multi-feuilles, **sans bibliothèque Python externe**.

## 2.2 — traitement mémoire maîtrisé

Le lecteur XLSX traite maintenant les feuilles avec `xml.etree.ElementTree.iterparse()` directement sur le flux ZIP au lieu de charger tout le XML d'une feuille en mémoire.

Le traitement est donc :

```text
XLSX
 └── ZIP
      └── feuille XML
           └── ligne par ligne
                └── index / recherche
```

Les feuilles ne sont plus conservées intégralement en mémoire.

### Sécurité et robustesse

- Python standard library uniquement ;
- `.xlsx` uniquement ;
- validation ZIP ;
- refus des chemins absolus et traversal ;
- limites de taille comprimée/non comprimée ;
- limite de ratio de compression pour réduire le risque de ZIP bomb ;
- XML traité en streaming ;
- limites feuilles/lignes/colonnes/cellules ;
- validation hostname/FQDN/IPv4 ;
- déduplication contrôlée de l'index ;
- conservation des occurrences de recherche ;
- CSV écrit en streaming ;
- aucune macro, formule ou connexion réseau exécutée.

## Entrées

```bash
python -m excel_host_lookup inventory.xlsx "srv01,srv02;srv03|srv04 srv05"
python -m excel_host_lookup inventory.xlsx hosts.txt
python -m excel_host_lookup inventory.xlsx --hosts-excel recherche.xlsx
```

Séparateurs : `, ; | espace`.

## Sorties

```text
results/
├── LISTE.csv
├── RESULTATS.csv
└── SOURCES.csv
```

Pour un Excel de recherche multi-feuilles, un CSV est produit par feuille.

## Limites

Les limites sont centralisées dans `limits.py`. Elles sont volontairement conservatrices et peuvent être adaptées à l'environnement.
