# Epic Events CRM

## Présentation

Epic Events CRM est une application CLI de gestion de la relation client (CRM) développée pour l'entreprise Epic Events, spécialisée dans l'organisation d'événements professionnels et privés.

L'application permet de centraliser et de gérer les clients, contrats et événements des différents pôles de l'entreprise.

## Fonctionnalités principales

- Authentification et gestion des utilisateurs
- Gestion des rôles et des permissions
- Gestion des clients
- Gestion des contrats
- Gestion des événements
- Attribution des événements aux membres de l'équipe support
- Validation des données et gestion des erreurs
- Contrôle des accès aux différentes ressources selon les rôles et permissions

## Stack technique

### Langage et gestion du projet

- **Python** — langage de programmation
- **uv** — gestionnaire de projet et d'environnement Python

### Base de données et persistance

- **PostgreSQL** — base de données relationnelle
- **SQLAlchemy** — ORM et gestion de la persistance
- **Alembic** — gestion des migrations de base de données

### Interface CLI

- **Click** — framework pour l'interface en ligne de commande
- **Rich** — affichage et mise en forme de l'interface CLI

### Validation et sécurité

- **Pydantic** — validation des données et de la configuration
- **cryptography** — chiffrement des données sensibles
- **argon2-cffi** — hachage sécurisé des mots de passe

### Monitoring et qualité

- **Sentry** — monitoring et suivi des erreurs
- **pytest** — tests automatisés
- **Ruff** — linting et formatage du code

## Prérequis

L'application nécessite d'avoir ces technologies installées au préalable :

- [Python](https://www.python.org/) `3.12+` ;
- [uv](https://pypi.org/project/uv/) ;
- [PostgreSQL](https://www.postgresql.org) ;
- (Optionnel) Git pour cloner le dépôt.

## Installation

Après avoir cloné ou téléchargé le dépôt, ouvrez un terminal dans le dossier `epicevents`. Toutes les commandes présentées ci-dessous, ainsi que l'utilisation de l'application, doivent être effectuées depuis ce dossier.

### Environnement Python

Créez l'environnement virtuel :

    uv venv

Activez-le :

- Linux ou Mac :
```bash
source .venv/bin/activate
```

- Windows :
```bash
.venv\Scripts\activate
```

Une fois votre environnement virtuel activé, installez les dépendances :

    uv sync --no-dev

L'environnement virtuel doit être activé pour exécuter l'application et ses commandes.

### Base de données

Epic Events utilise actuellement **PostgreSQL**.

Si PostgreSQL n'est pas encore installé sur votre machine, consultez la [documentation officielle](https://www.postgresql.org/docs/) pour suivre les instructions correspondant à votre système d'exploitation.

Une base de données dédiée à Epic Events doit être créée. Les informations de connexion devront ensuite être renseignées dans le fichier `.env`.

## Configuration

L'application nécessite certaines configurations avant de pouvoir être utilisée.

### Variables d'environnement

Le fichier `.env.example` contient les variables d'environnement nécessaires au fonctionnement de l'application.

Copiez-le vers `.env` :

    cp .env.example .env

Puis modifiez `.env` avec vos propres valeurs, notamment :
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `SECRET_KEY`
- `ENCRYPTION_KEY`

La variable `SENTRY_DSN` est optionnelle et peut rester vide si Sentry n'est pas utilisé.

### Clés de sécurité

L'application utilise deux clés distinctes :

- `SECRET_KEY` est utilisée pour la signature des tokens JWT ;
- `ENCRYPTION_KEY` est utilisée pour le chiffrement des données sensibles stockées en base de données.

Les deux clés doivent être générées aléatoirement et ne doivent jamais être versionnées dans le dépôt.

La `SECRET_KEY` doit contenir une clé de 256 bits (32 octets, soit 64 caractères hexadécimaux). Elle peut être générée avec :

    python -c "import secrets; print(secrets.token_hex(32))"

La `ENCRYPTION_KEY` doit contenir une clé de 512 bits (64 octets, soit 128 caractères hexadécimaux), nécessaire pour le chiffrement AES-SIV utilisé par l'application. Elle peut être générée avec :

    python -c "import secrets; print(secrets.token_hex(64))"

Copiez ensuite les clés générées dans votre fichier `.env`.

### Migrations de la base de données

Les migrations sont gérées avec Alembic :

    alembic upgrade head

Cette commande applique l'ensemble des migrations disponibles, crée le schéma de la base de données et initialise les données nécessaires au fonctionnement de l'application, notamment les rôles par défaut.

### Stockage des tokens

Par défaut, les tokens d'authentification sont stockés dans `.epicevents/tokens.json` à la racine du projet.

Cet emplacement est adapté à une utilisation en développement. Pour utiliser un autre emplacement, notamment dans un environnement de déploiement, définissez la variable `TOKEN_PATH` dans le fichier `.env` :

    TOKEN_PATH="/chemin/vers/tokens.json"

## Commandes CLI

Une fois votre environnement virtuel activé, l'application est accessible via la commande `epicevents`.

Vous pouvez également utiliser l'application sans activer manuellement l'environnement virtuel en préfixant chaque commande avec uv run :

    uv run epicevents <commande>

Pour vérifier que l'installation est correctement configurée et afficher le menu principal :

    epicevents

Chaque commande dispose d'une aide détaillée accessible avec l'option `--help` :

    epicevents --help
    epicevents user --help
    epicevents event list --help

Lors de la saisie d'un formulaire ou de l'exécution d'une commande, `Ctrl+C` permet d'annuler l'opération en cours.

### Première utilisation

Lors de la première installation, un superutilisateur doit être créé avant de pouvoir utiliser les fonctionnalités nécessitant une authentification :

    epicevents user create-superuser

Cette commande ouvre un formulaire permettant de renseigner les informations du superutilisateur.

Une fois le compte créé, d'autres collaborateurs peuvent être ajoutés et l'application peut être utilisée normalement.

### Organisation des commandes

Les commandes sont organisées par ressource :

    epicevents <resource> <command> [options]

Les principales ressources disponibles sont :

- `auth` — gestion de l'authentification
- `user` — gestion des utilisateurs
- `client` — gestion des clients
- `contract` — gestion des contrats
- `event` — gestion des événements

Les commandes disponibles dépendent de la ressource et suivent principalement les opérations CRUD :

- `create` — création d'une ressource
- `update` — modification d'une ressource
- `list` — affichage de l'ensemble des éléments d'une ressource
- `show` — affichage d'une ressource

Certaines commandes disposent d'options ou d'arguments spécifiques permettant notamment de filtrer ou d'assigner des ressources.

Pour connaître les commandes et options disponibles pour une ressource :

    epicevents <resource> --help

Et pour obtenir l'aide d'une commande spécifique :

    epicevents <resource> <command> --help

## Journalisation

La journalisation et le suivi des erreurs sont assurés par Sentry.

Pour activer cette fonctionnalité, renseignez un DSN Sentry dans la variable d'environnement `SENTRY_DSN` du fichier `.env`.

Les erreurs inattendues de l'application sont automatiquement remontées à Sentry.

Certains événements métier sont également journalisés, notamment :

- la création d'un nouveau collaborateur ;
- la modification d'un collaborateur ;
- la signature d'un contrat ;
- la création d'un nouvel événement.

La configuration de `SENTRY_DSN` est optionnelle. En son absence, l'application reste fonctionnelle, mais les erreurs et événements ne sont pas transmis à Sentry.

## Tests

L'application est couverte par des tests unitaires, d'intégration et fonctionnels afin de vérifier le comportement de ses différentes couches.

Un environnement de test dédié peut être configuré pour exécuter les tests.

### Configuration

Une base de données PostgreSQL dédiée aux tests doit être créée au préalable.

> **Attention :** n'utilisez pas une base de données de développement ou de production pour les tests. Les données de la base de test peuvent être supprimées ou réinitialisées lors de l'exécution de la suite de tests.

Le fichier `.env.test.example` contient les variables d'environnement nécessaires à l'environnement de test.

Copiez-le vers `.env.test` :

    cp .env.test.example .env.test

Renseignez ensuite les paramètres de connexion à la base de données de test.

### Dépendances de développement

Les dépendances nécessaires aux tests et aux outils de développement peuvent être installées avec :

    uv sync --group dev

### Exécution des tests

L'ensemble des tests peut être exécuté avec Pytest :

    pytest

Le taux de couverture peut être affiché avec :

    pytest --cov=.

Un rapport HTML détaillé peut également être généré :

    pytest --cov=. --cov-report=html

## Architecture

L'application suit une **architecture en couches**, visant à maintenir l'indépendance des différentes responsabilités tout en facilitant son extensibilité.

La CLI constitue actuellement la seule interface de l'application. Les Controllers constituent le point d'entrée de l'application et permettent d'envisager l'intégration d'une autre interface, comme une API, sans remettre en cause l'ensemble de la logique métier.

Les principales couches sont :

- **Interface (CLI)** : `Click` et `Rich` gèrent les interactions avec l'utilisateur et l'affichage.
- **Controllers** : assurent la coordination entre l'interface et les services et valident les données d'entrée à l'aide des schémas Pydantic.
- **Services** : centralisent la logique métier et appliquent les règles métier et de sécurité.
- **Infrastructure** : gère la persistance et les interactions avec les services externes. Les `Repositories` gèrent l'accès à la base de données via `SQLAlchemy`, tandis que le `Unit of Work` gère les transactions.

Les `Models` et les `Schemas` sont utilisés transversalement par les différentes couches.

Le `Bootstrap` assure l'injection des dépendances et le cycle de vie des sessions de base de données via une `ApplicationFactory`.

Les contrôles effectués au niveau de la CLI peuvent anticiper certaines erreurs afin d'améliorer l'expérience utilisateur, tandis que les services conservent leurs propres validations métier et de sécurité.

### Modèle de données

Le modèle de données est disponible dans le [diagramme ERD](docs/erd.png).

## Sécurité

- **Authentification** : JWT avec access tokens et refresh tokens, avec durée d'expiration configurable.
- **Mots de passe** : hachage sécurisé avec `Argon2`, aucun mot de passe n'est stocké en clair.
- **Autorisation** : système de rôles et permissions permettant de contrôler l'accès aux différentes fonctionnalités.
- **Validation** : les données entrantes et la configuration sont validées avec `Pydantic`.
- **Chiffrement des données** : les données sensibles stockées en base de données sont chiffrées avec `AES-SIV` via la bibliothèque `cryptography`.
- **Secrets** : clés et informations sensibles configurées via les variables d'environnement.
- **Contrôles métier** : les règles de sécurité sont également appliquées au niveau des services, indépendamment de l'interface utilisée.

## Conventions de code

Le projet suit les conventions de style définies par `Ruff`, notamment :

- respect des conventions **PEP 8** avec une longueur de ligne maximale de 88 caractères ;
- tri des imports avec **isort** ;
- détection des erreurs courantes avec **flake8-bugbear** ;
- utilisation des syntaxes Python modernes avec **pyupgrade** ;
- respect des conventions de nommage avec **pep8-naming** ;
- analyse statique avec **Pyflakes**.