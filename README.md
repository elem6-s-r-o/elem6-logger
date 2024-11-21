# ELEM6 Logger

Thread-safe singleton logger implementation s rozšířenými možnostmi pro Python 3.9+.

## Vlastnosti

- Thread-safe singleton pattern
- Flexibilní konfigurace (konzole/soubor)
- Podpora pro extra pole v log zprávách
- Automatické čištění starých logů
- Dynamická změna úrovně logování za běhu
- Plně typované (mypy)
- 98% test coverage

## Instalace

```bash
pip install elem6-logger
```

## Použití

### Základní použití

```python
from elem6_logger import Elem6Logger, LoggerConfig

# Konfigurace loggeru
config = LoggerConfig(
    log_level="INFO",
    log_dir="logs",
    add_console_handler=True,
    add_file_handler=True
)

# Inicializace loggeru
Elem6Logger.initialize(config)

# Získání instance loggeru
logger = Elem6Logger.get_logger("my_app")

# Logování
logger.info("Aplikace spuštěna")
logger.debug("Debug informace")
logger.warning("Varování")
logger.error("Chyba")
```

### Extra pole v logu

```python
config = LoggerConfig(
    log_level="INFO",
    extra_fields={
        "app": "my_app",
        "version": "1.0.0",
        "environment": "production"
    }
)

Elem6Logger.initialize(config)
logger = Elem6Logger.get_logger("my_app")

# Log bude obsahovat extra pole
logger.info("Zpráva")  # Obsahuje: app=my_app version=1.0.0 environment=production
```

### Dynamická změna úrovně logování

```python
logger = Elem6Logger.get_logger("my_app")
logger.info("Viditelná zpráva")
logger.debug("Neviditelná debug zpráva")

# Změna úrovně na DEBUG
Elem6Logger.set_log_level("DEBUG")

logger.debug("Nyní viditelná debug zpráva")
```

### Čištění starých logů

```python
config = LoggerConfig(
    log_dir="logs",
    retention_days=7  # Automaticky smaže logy starší než 7 dní
)

Elem6Logger.initialize(config)
```

## Vývoj

Pro vývoj nainstalujte závislosti pro development:

```bash
pip install -e ".[dev]"
```

### Spuštění testů

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Kontrola kódu

```bash
# Formátování
black .
isort .

# Typová kontrola
mypy src tests
```

## Přispívání

Přečtěte si [CONTRIBUTING.md](CONTRIBUTING.md) pro informace o tom, jak přispívat do projektu.

## Licence

Tento projekt je licencován pod MIT licencí - viz [LICENSE](LICENSE) soubor pro detaily.
