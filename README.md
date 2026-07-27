# Umzugsplaner

Web-App zur Umzugsplanung: Checkliste mit Terminen (festes Datum oder Kalenderwoche),
Aufgaben-Zuweisung an Personen, eine Wochenübersicht und ein mehrstöckiger
Grundriss-Editor mit Kisten-Beschriftung zum Ausdrucken.

## Nutzung

Einfach `index.html` im Browser öffnen — keine Installation, keine Abhängigkeiten,
kein Build-Schritt.

Für den gemeinsamen Gebrauch (z.B. per Link teilen), am einfachsten via **GitHub Pages**
hosten:
1. Repo auf GitHub pushen
2. Settings → Pages → Branch `main`, Ordner `/` (root)
3. Fertig — die Seite ist unter `https://<user>.github.io/<repo>/` erreichbar

## Aktueller Stand

Alle Daten (Aufgaben, Personen, Räume, Kisten) werden aktuell **nur lokal im Browser**
gespeichert (`localStorage`). Das heisst: kein automatischer Sync zwischen Geräten —
öffnet man die Seite auf einem zweiten Gerät, sieht man einen leeren/eigenen Stand.

Geplant ist ein kleines Backend, damit mehrere Personen/Geräte denselben Stand sehen.
Die Persistenz ist im Code bereits so abstrahiert (`DataStore`), dass sich das ohne grosse
Umbauten nachrüsten lässt. Details dazu stehen in [`CLAUDE.md`](./CLAUDE.md).

## Struktur

```
umzugsplaner/
├── index.html   # die komplette App (HTML/CSS/JS, keine externen Abhängigkeiten
│                #  außer Google Fonts)
├── README.md    # diese Datei
└── CLAUDE.md    # technischer Kontext für die Weiterentwicklung mit Claude Code
```
