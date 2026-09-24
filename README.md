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
python -m pip install --user --upgrade pip setuptools wheel
python -m pip install . --no-build-isolation

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


####################################
# XlsWhisper

**Enterprise-grade host, IP and FQDN lookup utility for Excel inventories**

XlsWhisper is a robust Python utility designed to search hosts, IP addresses and FQDNs across large multi-sheet Excel inventories.

It is designed for infrastructure, operations, automation and audit use cases where inventory data is distributed across multiple Excel worksheets and search inputs may come from Excel files, text files or command-line lists.

The application uses **Python standard library only at runtime** and processes `.xlsx` workbooks using streaming XML parsing, without requiring pandas, openpyxl or any other third-party runtime dependency.

---

## Key capabilities

* Multi-sheet `.xlsx` inventory processing
* Automatic detection of:

  * hostname columns
  * IP address columns
  * DNS/FQDN columns
* Hostname and FQDN normalization
* Search from:

  * another multi-sheet Excel workbook
  * TXT files
  * command-line host lists
* Multiple separators supported for direct host lists:

  * comma `,`
  * semicolon `;`
  * pipe `|`
  * whitespace
* Search occurrences preserved by source sheet and row
* Detection of conflicting inventory information
* Per-search-sheet CSV output
* Global result and source reports
* Streaming XLSX processing
* Controlled memory usage
* ZIP-bomb and malformed archive protections
* Strict input validation
* No network access
* No macro execution
* No formula execution
* No runtime third-party dependencies

---

## Architecture

XlsWhisper follows a lightweight layered architecture:

```text
src/excel_host_lookup/
│
├── cli.py
├── models.py
├── limits.py
├── normalization.py
├── detector.py
├── xlsx_reader.py
├── parser.py
├── index.py
├── lookup.py
└── exporter.py
```

### Responsibilities

| Module             | Responsibility                            |
| ------------------ | ----------------------------------------- |
| `cli.py`           | Command-line interface and orchestration  |
| `models.py`        | Domain data structures                    |
| `limits.py`        | Security and resource limits              |
| `normalization.py` | Host/FQDN/IP normalization and validation |
| `detector.py`      | Automatic inventory column detection      |
| `xlsx_reader.py`   | Streaming `.xlsx` XML reader              |
| `parser.py`        | Search-input parsing                      |
| `index.py`         | Inventory indexing                        |
| `lookup.py`        | Host lookup and conflict detection        |
| `exporter.py`      | CSV report generation                     |

The architecture deliberately separates file parsing, domain logic and output generation.

---

# Requirements

## Runtime

* Python **3.10 or newer**
* `.xlsx` input format

No external Python package is required at runtime.

The following libraries are intentionally **not required**:

* pandas
* openpyxl
* xlrd
* numpy

## Installation/build tools

Package installation through `pip` requires a standard Python packaging toolchain such as:

* `pip`
* `setuptools`
* `wheel`

These are build/install requirements, not application runtime dependencies.

---

# Supported input formats

## Inventory

The inventory must be an Excel `.xlsx` workbook.

Example:

```text
inventory.xlsx
├── Servers
├── Network
├── Applications
└── Database
```

Each worksheet may contain different columns. XlsWhisper automatically detects relevant columns.

Typical supported column names include variations of:

```text
Hostname
Host Name
Host
Server
Server Name
DNS Name
FQDN
IP
IP Address
IPv4
Address
```

Column detection is case-insensitive and tolerant of accents, spaces and punctuation.

---

## Search input

Three search modes are supported.

### 1. TXT file

```text
hosts.txt
```

Example:

```text
srv-prod-01
srv-prod-02
srv-db-01
srv-web-01
```

Multiple hosts can also be placed on one line:

```text
srv-prod-01;srv-prod-02 srv-db-01|srv-web-01
```

Comments beginning with `#` are ignored.

---

### 2. Direct command-line list

Example:

```powershell
python -m excel_host_lookup inventory.xlsx "srv01,srv02;srv03|srv04 srv05"
```

All of the following separators are accepted:

```text
,
;
|
space
tab
```

Example:

```text
srv01,srv02;srv03|srv04 srv05
```

is interpreted as:

```text
srv01
srv02
srv03
srv04
srv05
```

Duplicate hosts are normalized and removed.

---

### 3. Search Excel workbook

A separate multi-sheet Excel workbook can be used as the search source.

Example:

```text
recherche.xlsx
├── Production
├── Qualification
└── Development
```

Every occurrence is preserved with:

* search sheet
* source row
* hostname

This makes the output traceable to the original search workbook.

---

# Installation

From the project directory:

```powershell
python -m pip install .
```

If the Python environment uses an isolated build environment and Setuptools is not available there:

```powershell
python -m pip install --user --upgrade pip setuptools wheel
python -m pip install . --no-build-isolation
```

Verify the installation:

```powershell
excel-host-lookup --help
```

Alternatively:

```powershell
python -m excel_host_lookup --help
```

---

# Usage

## Search hosts from a TXT file

```powershell
excel-host-lookup inventory.xlsx hosts.txt
```

Example:

```powershell
python -m excel_host_lookup inventory.xlsx hosts.txt
```

---

## Search a direct host list

```powershell
excel-host-lookup inventory.xlsx "srv01,srv02;srv03|srv04 srv05"
```

---

## Search hosts from another Excel workbook

```powershell
excel-host-lookup inventory.xlsx --hosts-excel recherche.xlsx
```

The search workbook may contain multiple worksheets.

---

## Search the complete inventory

If no search source is specified, all hosts detected in the inventory are searched:

```powershell
excel-host-lookup inventory.xlsx
```

---

## Specify an output directory

```powershell
excel-host-lookup inventory.xlsx hosts.txt --output results
```

Example:

```text
results/
├── Production.csv
├── Qualification.csv
├── Development.csv
├── RESULTATS.csv
└── SOURCES.csv
```

---

# Output

XlsWhisper produces CSV files using:

* UTF-8 encoding
* UTF-8 BOM
* `;` as delimiter

This format is particularly convenient for Microsoft Excel in French/European environments.

---

## Result report

The global result file is:

```text
RESULTATS.csv
```

Typical fields include:

```text
Host
IP
FQDN
Status
ConflictIP
ConflictFQDN
```

Possible statuses include:

### `OK`

A unique consistent inventory result was found.

### `NON_TROUVE`

No corresponding host or FQDN was found.

### `CONFLIT`

The inventory contains conflicting information, for example:

```text
srv01 → 10.10.10.10
srv01 → 10.10.10.20
```

XlsWhisper does not silently select one of the conflicting values.

---

# Source traceability

The `SOURCES.csv` report identifies where inventory records were found.

Example:

```text
Hostname;IP;FQDN;Sheet;Row
srv01;10.10.10.10;srv01.example.com;Production;27
```

This makes it possible to trace a result back to the original workbook and worksheet.

---

# Search-sheet reports

When the search source is a multi-sheet Excel workbook, XlsWhisper generates a separate report for each search worksheet.

For example:

```text
recherche.xlsx
├── Production
├── Qualification
└── Development
```

produces:

```text
results/
├── Production.csv
├── Qualification.csv
├── Development.csv
├── RESULTATS.csv
└── SOURCES.csv
```

Spaces in worksheet names are removed from generated filenames.

---

# Normalization

Before lookup, hostnames and FQDNs are normalized.

The normalization process includes:

* trimming surrounding whitespace
* Unicode normalization
* case normalization
* hostname validation
* FQDN validation
* IPv4 validation
* duplicate elimination where appropriate

For example:

```text
 SRV-01
srv-01
Srv-01
```

are treated as the same logical hostname.

---

# Conflict detection

Inventory data is not assumed to be authoritative merely because a value exists.

For example:

```text
Hostname     IP
----------   ------------
srv01        10.10.10.10
srv01        10.10.10.20
```

produces:

```text
Status = CONFLIT
```

This prevents accidental selection of an arbitrary IP address.

The same principle applies to conflicting FQDN information.

---

# Security model

XlsWhisper is designed to process potentially large or untrusted inventory files safely.

## XLSX archive validation

`.xlsx` files are ZIP archives containing XML documents.

Before processing, XlsWhisper validates archive members and rejects unsafe paths such as:

```text
../../file
```

or absolute paths.

---

## ZIP-bomb protection

The reader enforces:

* maximum archive size
* maximum member size
* maximum decompressed size
* maximum compression ratio

This prevents pathological ZIP archives from consuming uncontrolled resources.

---

## XML processing

Workbook XML is processed using streaming parsing.

The application does not execute:

* Excel macros
* VBA
* formulas
* external programs
* external network resources

Only cached XML values are read.

---

# Resource limits

Default limits are deliberately conservative for enterprise workloads.

| Resource           | Default limit |
| ------------------ | ------------: |
| XLSX file size     |       256 MiB |
| ZIP member size    |       128 MiB |
| XML member size    |        64 MiB |
| Worksheets         |           512 |
| Rows per worksheet |     1,000,000 |
| Columns            |        16,384 |
| Cells per row      |        16,384 |
| Shared strings     |     2,000,000 |
| String size        |         1 MiB |
| Search hosts       |     2,000,000 |
| Sources per host   |       100,000 |
| Compression ratio  |         200:1 |

These limits are intended to prevent uncontrolled memory and CPU consumption.

---

# Large-file processing

XlsWhisper uses `xml.etree.ElementTree.iterparse()` to process worksheet XML progressively.

The application does not load an entire worksheet into memory.

Conceptually:

```text
XLSX
 │
 ├── workbook.xml
 ├── sharedStrings.xml
 └── worksheet.xml
          │
          ▼
    Streaming parser
          │
          ▼
      Inventory
          │
          ▼
        Index
          │
          ▼
        Lookup
          │
          ▼
        CSV
```

This approach allows large inventories to be processed without the memory overhead normally associated with loading an entire workbook into pandas or openpyxl.

---

# Supported Excel format

XlsWhisper currently supports:

```text
.xlsx
```

The legacy binary Excel format:

```text
.xls
```

is intentionally not supported.

Supporting `.xls` without third-party libraries would require implementing or embedding a reader for Microsoft's legacy binary BIFF format, which is outside the scope of the project.

For legacy workbooks, convert them to `.xlsx` before processing.

---

# Error handling

XlsWhisper follows a fail-closed approach.

Invalid or unsafe input is rejected instead of being partially processed silently.

Examples include:

* invalid file extension
* malformed XLSX archive
* unsafe ZIP member path
* excessive archive compression ratio
* excessive file size
* excessive worksheet size
* invalid hostname
* invalid IP address
* malformed search input
* unsupported `.xls` files

Errors return a non-zero exit code.

Typical operational result:

```text
0 = successful execution
2 = input, validation or processing error
```

---

# Example workflow

A typical infrastructure inventory workflow may look like:

```text
              Inventory
            inventory.xlsx
                  │
                  ▼
        ┌───────────────────┐
        │ XLSX validation    │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Column detection   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Streaming parser  │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Inventory index   │
        └─────────┬─────────┘
                  │
                  │
        Search input
       TXT / Excel / CLI
                  │
                  ▼
        ┌───────────────────┐
        │ Host normalization │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Lookup & conflicts │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ CSV reports        │
        └───────────────────┘
```

---

# Development

Clone or obtain the project source and work from the project directory.

Run the application directly from the source tree:

```powershell
python -m excel_host_lookup --help
```

Run the test suite:

```powershell
python -m unittest discover -s tests -v
```

The project intentionally keeps runtime dependencies empty.

---

# Project structure

```text
XlsWhisper/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── src/
│   └── excel_host_lookup/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py
│       ├── limits.py
│       ├── normalization.py
│       ├── detector.py
│       ├── xlsx_reader.py
│       ├── index.py
│       ├── parser.py
│       ├── lookup.py
│       ├── exporter.py
│       └── cli.py
│
└── tests/
    ├── test_normalization.py
    ├── test_limits.py
    └── test_no_dependencies.py
```

---

# Design principles

XlsWhisper follows the following principles:

### No unnecessary dependencies

The runtime relies exclusively on the Python standard library.

### Fail closed

Malformed, ambiguous or unsafe input is rejected.

### Deterministic processing

The same input produces consistent lookup results.

### Traceability

Results can be traced back to their originating worksheet and row.

### Explicit conflicts

Conflicting inventory information is reported rather than silently resolved.

### Controlled resource consumption

File size, XML size, row count, worksheet count and other resources are bounded.

### Separation of concerns

Parsing, normalization, indexing, lookup and reporting are isolated into dedicated components.

### Operational simplicity

The utility can run on an infrastructure administration workstation without installing a large Python dependency stack.

---

# Limitations

Current limitations include:

* `.xls` is not supported
* IPv6 is not currently treated as a search hostname/IP type
* Excel formulas are not evaluated
* Excel date formatting is not interpreted
* the inventory index is maintained in memory

For extremely large inventories beyond the practical memory capacity of the workstation, an on-disk indexing backend such as SQLite would be the natural next scalability step.

---

# Version

Current release:

```text
2.2.0
```

Version 2.2.0 introduces streaming XLSX worksheet processing and additional resource controls for large enterprise inventory files.

---

# License

Add the applicable project license here.

Example:

```text
Copyright © 2026 IRIVEN Group.

All rights reserved.
```

---

# Operational summary

For a standard infrastructure lookup:

```powershell
excel-host-lookup inventory.xlsx hosts.txt
```

For an Excel search source:

```powershell
excel-host-lookup inventory.xlsx --hosts-excel recherche.xlsx
```

For a direct host list:

```powershell
excel-host-lookup inventory.xlsx "srv01,srv02;srv03|srv04"
```

The resulting reports are written to:

```text
results/
```

with:

```text
RESULTATS.csv
SOURCES.csv
```

and, when applicable, one CSV report per search worksheet.
