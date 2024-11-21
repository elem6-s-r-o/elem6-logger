# Contributing to elem6-logger

## Pravidla pro přispívání

1. **Nepřímé commity do main větve**
   - Všechny změny musí jít přes pull requesty
   - Přímé commity do main větve jsou zakázány
   - Každý pull request musí projít code review

2. **Proces vývoje**
   - Vytvořte novou větev pro vaše změny: `git checkout -b feature/nazev-zmeny`
   - Proveďte změny a otestujte je
   - Commitněte změny s popisným commit message
   - Vytvořte pull request do main větve

3. **Požadavky na pull request**
   - Musí projít všechny testy
   - Musí mít 100% test coverage pro nový kód
   - Musí projít kontrolou formátování (black)
   - Musí projít kontrolou importů (isort)
   - Musí projít typovou kontrolou (mypy)

4. **Code review**
   - Každý pull request musí být schválen alespoň jedním reviewerem
   - Reviewer by měl zkontrolovat:
     - Funkcionalitu
     - Testy
     - Dokumentaci
     - Kvalitu kódu

5. **Testy**
   - Všechny nové funkce musí být otestovány
   - Testy musí být čitelné a udržovatelné
   - Používejte pytest fixtures pro sdílení test setup kódu

6. **Dokumentace**
   - Každá nová funkce musí být dokumentována
   - Dokumentace musí obsahovat příklady použití
   - Udržujte README.md aktuální

## Nastavení vývojového prostředí

1. **Instalace závislostí**
```bash
# Instalace projektu a vývojových závislostí
pip install -e ".[dev]"

# Instalace a nastavení pre-commit hooks
pre-commit install
```

2. **Pre-commit hooks**
Projekt používá pre-commit hooks pro automatické formátování kódu při commitu:
- black: formátování Python kódu
- isort: řazení importů

Pre-commit hooks se spustí automaticky při každém commitu. Pokud je potřeba formátování opravit:
1. Hook selže a zobrazí chyby
2. Změny jsou automaticky opraveny
3. Přidejte opravené soubory znovu do stage (`git add`)
4. Opakujte commit

## Spuštění testů a kontrol manuálně

```bash
# Spuštění testů
pytest tests/ --cov=src --cov-report=term-missing

# Manuální spuštění formátování
black .
isort .

# Typová kontrola
mypy src tests

# Spuštění všech pre-commit hooks
pre-commit run --all-files
```

## Commit messages

Používejte konvenci:

```
<typ>: <popis>

<detailní popis>

<číslo ticketu>
```

Typy:
- feat: nová funkce
- fix: oprava chyby
- docs: změny v dokumentaci
- style: formátování, chybějící středníky, atd.
- refactor: refaktoring kódu
- test: přidání nebo úprava testů
- chore: úpravy buildu, pomocné nástroje, atd.

Příklad:
```
feat: přidání podpory pro extra pole v logu

- Přidána možnost konfigurace extra polí v LoggerConfig
- Extra pole jsou přidána do každé log zprávy
- Přidány testy pro ověření funkčnosti

Ticket: #123
