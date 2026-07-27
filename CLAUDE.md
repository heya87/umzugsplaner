# CLAUDE.md — Kontext für Claude Code

Diese Datei ist für dich (Claude Code), nicht für den Menschen. Sie fasst zusammen, was in diesem
Projekt schon entschieden wurde, damit du nicht von Null anfangen musst.

## Projekt in einem Satz
Umzugsplaner: eine Single-Page-App (aktuell **eine** Datei, `index.html`, kein Build-Schritt,
kein Framework) zur Planung eines Umzugs — Checkliste, Wochenübersicht, mehrstöckiger
Grundriss-Editor mit Kisten-Beschriftung.

## Architektur (Stand jetzt)
- Alles in `index.html`: inline `<style>` + inline `<script>` (IIFE, `"use strict"`).
  Kein React, kein Build-Tool, kein `package.json`.
- Sprache der UI: **Deutsch**, Kontext ist ein Umzug in der Schweiz/DACH-Region (Kalenderwochen,
  „Ummeldung", „Endreinigung durch Firma", etc.).
- **Persistenz-Abstraktion**: Es gibt ein `DataStore`-Objekt mit `load(collection, fallback)`
  und `save(collection, data)`. Aktuell ist das ein dünner localStorage-Wrapper
  (Key-Prefix `umzugsplaner:`). Die Collections sind: `tasks`, `rooms`, `boxes`, `people`,
  `floors`, `settings` — jede Collection ist genau ein JSON-Dokument.
  - **Das ist bewusst so gebaut**, damit man `load`/`save` später 1:1 durch `fetch()`-Calls an
    eine REST-API ersetzen kann, ohne den Rest der App (Rendering, State, Events) anzufassen.
    Die Kommentare direkt im Code zeigen die vorgesehenen Endpunkte
    (`GET/PUT /api/umzug/<collection>`).
- State: ein einfaches globales `state`-Objekt (`{ moveDate, tasks, rooms, boxes, people, floors }`).
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
   relativ zum Umzugstermin berechnet werden (`offsetWeeks`, negativ = vorher).
2. **KW-Übersicht** — alle Kalenderwochen von heute bis Umzugstermin (+ Puffer), pro Woche
   die zugehörigen Aufgaben, inline neue Aufgabe pro Woche anlegbar. Alle Wochen sind
   standardmässig aufgeklappt (Nutzerwunsch).
3. **Grundriss & Kisten** — mehrere Stockwerke (Standard: 4, umbenennbar/löschbar/neu
   anlegbar über Tabs). Pro Stockwerk beliebig viele Räume, frei verschiebbar/skalierbar
   (Pointer-Events, Koordinaten in %). Kisten-Manifest: jede Kiste bekommt Nummer, Zielraum
   (Dropdown gruppiert nach Stockwerk), Inhalt, Zerbrechlich-Flag. Druckbare Etiketten via
   `window.print()` + `@media print`.

## Bewusst entfernte Features (nicht ohne Rückfrage wieder einbauen)
Der Nutzer hat im Verlauf explizit gebeten, folgendes **zu entfernen**:
- Prioritäts-Feld bei Aufgaben
- Kategorien/Phasen (Frühphase, Vorbereitung, Umzugstag, …)
- Import/Export als JSON-Datei
- Kalender-Export-Tab (.ics-Export, Google-Kalender-Links)
- „Termine neu berechnen" / „Standardaufgaben ergänzen" Buttons — stattdessen wurden Aufgaben
  direkt inline editierbar gemacht

Auch der Umzugsfirma-Task wurde bewusst durch „Transporter/Fahrzeug mieten" ersetzt
(Nutzer macht Umzug selbst, mietet nur ein Fahrzeug) und zwei Aufgaben für eine externe
Reinigungsfirma wurden hinzugefügt (Endreinigung wird nicht selbst gemacht).

## Offene Punkte / nächster grosser Schritt
Der Nutzer hat angekündigt, dass reines `localStorage` **zu mühsam** ist, weil es keinen
Sync zwischen Geräten gibt. Wunsch: **Server-Deployment via GitHub + CI/CD** (vermutlich
GitHub Actions). Das bedeutet konkret:
1. Ein kleines Backend bauen (z.B. Node/Express, Cloudflare Workers + KV/D1, oder Supabase/
   Firebase), das dieselben Collection-Namen wie `DataStore` bedient — je ein Endpunkt für
   `GET`/`PUT` pro Collection reicht für den aktuellen Datenumfang.
2. In `index.html` nur die `DataStore.load`/`save`-Methoden umstellen (siehe die
   auskommentierten REST-Beispiele direkt im Code) — der Rest der App braucht keine Änderung.
3. Auth ist noch nicht besprochen — vermutlich reicht fürs Erste ein einzelner geteilter
   „Haushalt"-Datensatz ohne Login, da es sich um ein privates Haushalts-Tool handelt. Falls
   mehrere Haushalte/Nutzer unterstützt werden sollen, braucht es einen einfachen Login.
4. GitHub Actions Workflow für Deployment (Frontend z.B. weiterhin GitHub Pages oder
   zusammen mit dem Backend containerisiert deployen).

## Weitere Kontext-Notizen
- Umzugstermin-Standardwert ist hart codiert: `DEFAULT_MOVE_DATE = '2026-10-31'`.
- Das Farbschema wurde mehrfach wegen Kontrast-/Lesbarkeitsproblemen angepasst: der Header ist
  jetzt ein dunkler Balken (`--ink`) mit weissem Titel. Es gibt `color-scheme: light` (Meta-Tag
  + CSS) plus `!important` auf der `h1`-Farbe, weil vermutet wurde, dass eine mobile WebView/App
  automatisch Dark-Mode-Farben injiziert hat.
- Kein Test-Framework vorhanden. Bisheriger „Test" war lediglich `node --check` auf den
  extrahierten `<script>`-Inhalt, um Syntaxfehler vor dem Deployment zu erkennen — das sollte
  bei jeder Änderung an `index.html` wiederholt werden, solange es kein echtes Build-/Test-Setup
  gibt.
