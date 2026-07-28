# CLAUDE.md — Kontext für Claude Code

Diese Datei ist für dich (Claude Code), nicht für den Menschen. Sie fasst zusammen, was in diesem
Projekt schon entschieden wurde, damit du nicht von Null anfangen musst.

## Projekt in einem Satz
Umzugsplaner: eine Single-Page-App (Frontend weiterhin **eine** Datei, `index.html`, kein
Build-Schritt, kein Framework, plus ein minimaler Flask-Server für den Daten-Sync) zur Planung
eines Umzugs — Checkliste, Wochenübersicht, mehrstöckiger Grundriss-Editor mit
Kisten-Beschriftung.

## Architektur (Stand jetzt)
- Frontend weiterhin **eine** Datei, `index.html`: inline `<style>` + inline `<script>` (IIFE,
  `"use strict"`). Kein React, kein Build-Tool für das Frontend selbst.
- Sprache der UI: **Deutsch**, Kontext ist ein Umzug in der Schweiz/DACH-Region (Kalenderwochen,
  „Ummeldung", „Endreinigung durch Firma", etc.).
- **Persistenz-Abstraktion**: Es gibt ein `DataStore`-Objekt mit `load(collection, fallback)`
  und `save(collection, data)`. Das ruft `fetch()` gegen `GET/PUT /api/umzug/<collection>` auf
  (kein localStorage mehr). Die Collections sind: `tasks`, `rooms`, `boxes`, `people`,
  `floors`, `settings`, `furniture` — jede Collection ist genau ein JSON-Dokument.
- **Backend**: `server/app.py`, ein minimaler Flask-Server. Kein Datenbank — jede Collection
  wird als eigene Datei `data/<collection>.json` auf der Disk abgelegt (atomic write via
  tmp-Datei + `os.replace`). Der Server validiert Collection-Namen gegen eine feste Whitelist
  und liefert `index.html` selbst aus (`GET /` und `/index.html`). Kein Auth — ein einzelner
  geteilter Haushalt-Datensatz, kein Login (bewusste Entscheidung, siehe unten).
- **Deployment**: Dockerfile (Python 3.12-slim + gunicorn) + `docker-compose.yml` für lokale
  Entwicklung (mountet `./data` nach `/app/data`). `.github/workflows/deploy.yml` triggert bei
  Push auf `main` einen Coolify-Webhook (Secrets `COOLIFY_WEBHOOK`/`COOLIFY_TOKEN`); Coolify
  baut das Image selbst und deployt es auf dem self-hosted Infomaniak-VPS — analog zum
  Deployment-Setup des Schwesterprojekts `../edu/koemerle` (dort allerdings mit
  SvelteKit+Postgres+Drizzle, was für diese App bewusst zu schwer wäre). **Wichtig**: In
  Coolify muss ein persistentes Volume auf `/app/data` gemountet sein, sonst gehen die Daten
  bei jedem Redeploy verloren.
- State: ein einfaches globales `state`-Objekt (`{ moveDate, tasks, rooms, boxes, people, floors, furniture }`).
  Kein virtuelles DOM — jede `render*()`-Funktion baut `innerHTML` neu und hängt danach
  Event-Listener an die frisch erzeugten Elemente.
- Datumslogik: eigene ISO-Wochen-Helper (`isoWeekYear`, `mondayOfISOWeek`, …), alles in UTC
  gerechnet, um Zeitzonen-Bugs zu vermeiden. Eine Aufgabe hat entweder `dateType:'date'`
  (festes Datum) oder `dateType:'kw'` (Kalenderwoche + Jahr, wird intern auf den Montag
  dieser Woche gemappt).

## Features (aktueller Stand)
1. **Checkliste** — Aufgaben mit Titel, Zuweisung (Person aus einer selbst gepflegten Liste),
   Termin (Datum oder KW), Status. Jede Zeile ist über einen „Bearbeiten"-Button inline
   editierbar (kein Modal). 27 vorausgefüllte Standardaufgaben (`SEED_TASKS`), deren Termine
   relativ zum Umzugstermin berechnet werden (`offsetWeeks`, negativ = vorher). Zusätzlich gibt
   es „Checkliste exportieren"/„importieren" (JSON-Datei-Download bzw. -Upload, ersetzt bei
   Import komplett `state.tasks`) — gedacht, um die Aufgabenliste ausserhalb der App
   z.B. mit Claude zu bearbeiten und dann per Import zurückzuspielen.
2. **KW-Übersicht** — alle Kalenderwochen von heute bis Umzugstermin (+ Puffer), pro Woche
   die zugehörigen Aufgaben, inline neue Aufgabe pro Woche anlegbar. Alle Wochen sind
   standardmässig aufgeklappt (Nutzerwunsch).
3. **Grundriss & Kisten** — mehrere Stockwerke (Standard: 4, umbenennbar/löschbar/neu
   anlegbar über Tabs). Pro Stockwerk beliebig viele Räume, frei verschiebbar/skalierbar
   (Pointer-Events, Koordinaten in %). Zusätzlich **Möbel**: analog zu Räumen frei
   verschiebbar/skalierbar auf demselben Grundriss (grobe Planung, kein exakter Massstab,
   optisch unterscheidbar durch gestrichelten Rand statt Vollfarbe); pro Möbelstück ist eine
   Anzahl Etiketten einstellbar (Möbel-Liste unter dem Grundriss), für mehrteilige Möbel. Ein
   echtes Grundriss-Foto als Hintergrund ist bewusst (noch) nicht umgesetzt.
   **Kisten-Etiketten**: bewusst *keine* Inhalts-/Zerbrechlich-Erfassung in der App — pro Raum
   wird nur eine Anzahl benötigter Etiketten festgelegt (`state.boxes` ist `{id, roomId,
   count}`, keine Kistennummern mehr). Jede gedruckte Etikette hat ein leeres Feld zum
   Beschriften beim Packen sowie eine „☐ Zerbrechlich"-Zeile zum Ankreuzen von Hand.
   Ein einziger „Alle Etiketten drucken"-Button erzeugt Kisten- und Möbel-Etiketten gemeinsam
   (`renderGrundriss`-Button `printLabelsBtn`) über `window.print()` + `@media print`.
   **Wichtig**: der `#printLabels`-Container muss ein **direktes Kind von `.wrap`** sein — die
   Print-CSS-Regel (`.wrap > *:not(.print-labels){display:none}`) versteckt sonst den
   gesamten Elternknoten inkl. der Etiketten (führte zu einem leeren Ausdruck, bevor das
   gefixt wurde).

## Bewusst entfernte Features (nicht ohne Rückfrage wieder einbauen)
Der Nutzer hat im Verlauf explizit gebeten, folgendes **zu entfernen**:
- Prioritäts-Feld bei Aufgaben
- Kategorien/Phasen (Frühphase, Vorbereitung, Umzugstag, …)
- Kalender-Export-Tab (.ics-Export, Google-Kalender-Links)
- „Termine neu berechnen" / „Standardaufgaben ergänzen" Buttons — stattdessen wurden Aufgaben
  direkt inline editierbar gemacht

Auch der Umzugsfirma-Task wurde bewusst durch „Transporter/Fahrzeug mieten" ersetzt
(Nutzer macht Umzug selbst, mietet nur ein Fahrzeug) und zwei Aufgaben für eine externe
Reinigungsfirma wurden hinzugefügt (Endreinigung wird nicht selbst gemacht).

## Offene Punkte
Der Server-Sync (Flask + flat JSON files + Docker/Coolify, siehe Architektur oben) ist
umgesetzt. Was noch aussteht, ist reine Infra-Konfiguration auf Seiten des Nutzers (nicht im
Code lösbar):
1. In Coolify eine neue Resource anlegen (Dockerfile-basierte App, kein DB-Service), die auf
   das `heya87/umzugsplaner`-Repo zeigt, inkl. persistentem Volume auf `/app/data`.
2. Deploy-Webhook-URL + Token aus Coolify holen und als `COOLIFY_WEBHOOK`/`COOLIFY_TOKEN`
   Secrets im GitHub-Repo hinterlegen, damit `.github/workflows/deploy.yml` greift.
3. Auth ist weiterhin bewusst nicht vorhanden — ein einzelner geteilter „Haushalt"-Datensatz
   ohne Login, da es sich um ein privates Haushalts-Tool handelt. Falls das je mehrere
   Haushalte/Nutzer unterstützen soll, braucht es einen einfachen Login (aktuell nicht geplant).

## Weitere Kontext-Notizen
- Umzugstermin-Standardwert ist hart codiert: `DEFAULT_MOVE_DATE = '2026-10-31'`.
- Das Farbschema wurde mehrfach wegen Kontrast-/Lesbarkeitsproblemen angepasst: der Header ist
  jetzt ein dunkler Balken (`--ink`) mit weissem Titel. Es gibt `color-scheme: light` (Meta-Tag
  + CSS) plus `!important` auf der `h1`-Farbe, weil vermutet wurde, dass eine mobile WebView/App
  automatisch Dark-Mode-Farben injiziert hat.
- Kein Test-Framework vorhanden. Bisheriger „Test" war lediglich `node --check` auf den
  extrahierten `<script>`-Inhalt, um Syntaxfehler vor dem Deployment zu erkennen — das sollte
  bei jeder Änderung an `index.html` wiederholt werden, solange es kein echtes Build-/Test-Setup
  gibt. Für `server/app.py` analog: `python -m py_compile server/app.py` als schneller
  Syntax-Check vor dem Deployment.
