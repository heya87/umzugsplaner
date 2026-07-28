# Umzugsplaner

Web-App zur Umzugsplanung: Checkliste mit Terminen (festes Datum oder Kalenderwoche),
Aufgaben-Zuweisung an Personen, eine Wochenübersicht und ein mehrstöckiger
Grundriss-Editor mit Kisten-Beschriftung zum Ausdrucken.

## Nutzung

### Lokal (ohne Sync)

Einfach `index.html` im Browser öffnen — dann laufen die API-Calls ins Leere und nichts wird
gespeichert. Für echten Betrieb den Server lokal starten:

```bash
pip install -r server/requirements.txt
python server/app.py
```

Danach die App unter `http://localhost:8000` öffnen. Alternativ mit Docker:

```bash
docker compose up --build
```

## Aktueller Stand

Alle Daten (Aufgaben, Personen, Räume, Kisten) werden vom Server gespeichert (`server/app.py`,
je Collection eine JSON-Datei unter `data/`). Mehrere Geräte im selben Haushalt sehen denselben
Stand. Es gibt kein Login — der Server ist für einen einzelnen geteilten Haushalt gedacht.

Deployment läuft containerisiert über Coolify (self-hosted): Push auf `main` triggert per
GitHub Actions (`.github/workflows/deploy.yml`) einen Coolify-Webhook, der das Docker-Image neu
baut und deployt. Details dazu stehen in [`CLAUDE.md`](./CLAUDE.md).

## Struktur

```
umzugsplaner/
├── index.html              # die komplette Frontend-App (HTML/CSS/JS, keine externen
│                            #  Abhängigkeiten außer Google Fonts)
├── server/
│   ├── app.py               # Flask-Server: liefert index.html + GET/PUT /api/umzug/<collection>
│   └── requirements.txt
├── Dockerfile
├── docker-compose.yml        # lokale Entwicklung
├── .github/workflows/deploy.yml
├── README.md    # diese Datei
└── CLAUDE.md    # technischer Kontext für die Weiterentwicklung mit Claude Code
```
