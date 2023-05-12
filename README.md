# Teamboard
12.05.2023
Frontend: https://github.com/Ben-schlch/Teamboard-Frontend
# Backend

## Allgemeine Struktur

Das Backend nutzt Python aufgrund der einfachen und klaren Syntax. Dabei wird auf die Frameworks FastAPi und Uvicorn gesetzt.

FastAPI ist ein leistungsstarkes und effizientes Framework für die Entwicklung von Webanwendungen mit Python. Es bietet eine einfache und intuitive Syntax, eine hohe Geschwindigkeit und Skalierbarkeit.

Uvicorn hingegen wird als „Asynchronous Server Gateway Interface"-Server für das FastAPI-Projekt verwendet. Uvicorn ist ein schneller Server, der speziell für ASGI-Anwendungen entwickelt wurde und eine hohe Leistung und Skalierbarkeit bietet. Er unterstützt WebSocket-Verbindungen und ermöglicht es der FastAPI-Anwendung, auf mehreren Prozessen zu laufen, um eine effiziente Verarbeitung von Anfragen zu gewährleisten.

Die Struktur des Projektes:

1. **main.py** : Dies ist die Hauptdatei, die den Einstiegspunkt für die Anwendung darstellt. Hier werden die verschiedenen Endpunkte und die Logik für die Verarbeitung von Anfragen definiert. Es wird der FastAPI-Anwendungsobjekt erstellt.
2. **services** : Dieser Ordner enthält verschiedene Unterordner und Dateien, die Dienste für die Anwendung bereitstellen.
  - **users.py** : Dieses Modul enthält Funktionen für die Benutzerverwaltung, wie z.B. die Registrierung von Benutzern, die Überprüfung von Anmeldeinformationen und die Verwaltung von Passwortrücksetzungen.
  - **connectionmanager.py** : Hier wird der ConnectionManager implementiert, der für das Verwalten von WebSocket-Verbindungen zuständig ist.
  - **boardedit.py** : Dieses Modul enthält Funktionen zur Bearbeitung von Boards, Aufgaben, Spalten und Unteraufgaben. Hier wird die eigentliche Logik für das Bearbeiten und Verwalten der Boards implementiert.
3. **Weitere Dateien** : z.B. logging oder ein shell-Skript zum Starten

## Die Endpunkte

- WebSocket-Endpunkt: /ws/{token} [WebSocket]

Handelt die WebSocket-Verbindung und ermöglicht die Kommunikation für alles rund um die Teamboards. Die Authentifizierung erfolgt über ein JWT-Token, das im Login-Endpunkt erhalten wird.

- HTTP-Endpunkt: /login [POST]

Generiert ein JWT-Token anhand einer E-Mail und eines Passworts.

- HTTP-Endpunkt: /register/ [POST]

Registriert einen neuen Benutzer und sendet eine Bestätigungs-E-Mail, die vor dem Login bestätigt werden muss.

- HTTP-Endpunkt: /confirm/{token} [GET]

Bestätigt die E-Mail-Adresse des Benutzers anhand eines Bestätigungstokens.

- HTTP-Endpunkt: /send\_reset\_mail/{email} [GET]

Sendet eine E-Mail zum Zurücksetzen des Passworts an den Benutzer.

- HTTP-Endpunkt: /reset/{token} [GET]

Zeigt die Passwort-Reset-Seite an und ermöglicht das Resetten vom Password mit einem bestimmten Token, den der Client per Mail bekommt.

## Datenbank PostgreSQL

Das RDBMS PostgreSQL speichert die die User, Teamboards und ihre Editoren. Dem UML kann man die grobe Struktur entnehmen (mittlerweile veraltet).

[Bild ist in word Datei]

Besonderes Augenmerk lag auf der Sicherheit:

Die Passwörter der User werden gehasht und dann nochmal mit Salt gehasht und abgespeichert. Dadurch sollte selbst nach einem Datenbankleak eine gewisse Absicherung bestehen.

# Reverse Proxy

Ursprünglich war Backend auf Port :8000 und Frontend auf Port :443. → Fehler: Cross-Origin Resource Sharing (CORS)

Durch Reverse Proxy mit NGINX, eine Art von Middleware können wir Frontend auf 443 Port erreichen mit: [https://teamboard.server-welt.com/](https://teamboard.server-welt.com/)

Das Backend dagegen unter [https://teamboard.server-welt.com/api](https://teamboard.server-welt.com/api)
