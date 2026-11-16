# Celestial Ascent auf CurseForge hochladen

Alles, was du brauchst, liegt in diesem Ordner (`release/curseforge`):

| Datei | Wofür |
|---|---|
| `celestialascent-1.0.0.jar` | die Mod-Datei, die du hochlädst |
| `logo.png` | Projekt-Logo (1024×1024) |
| `banner.png` | Banner oben in der Beschreibung (1920×600) |
| `summary.txt` | Kurzbeschreibung für die Projektliste |
| `description.md` / `description.html` | lange Beschreibung (Englisch) |
| `changelog.md` | Changelog für die Datei 1.0.0 |
| `gallery/` + `gallery_captions.txt` | 28 Screenshots mit Titel und Beschreibung |

CurseForge verlangt Englisch für Titel, Kurzbeschreibung und Beschreibung. Deshalb sind diese Texte englisch. Dass die Mod auch Deutsch kann, steht in der Beschreibung.

---

## 1. Konto

1. Auf <https://www.curseforge.com> mit deinem Konto anmelden (oder eins erstellen). Anzeigename wäre passend: **Lonitys**.
2. Die Autorenkonsole öffnen: <https://authors.curseforge.com>.
3. Falls CurseForge danach fragt, die Autoren-Bedingungen akzeptieren.

## 2. Projekt erstellen

In der Autorenkonsole auf **Create Project** klicken und so ausfüllen:

| Feld | Eintrag |
|---|---|
| Game | **Minecraft** |
| Class | **Mods** |
| Project Name | **Celestial Ascent** |
| Summary | Inhalt von `summary.txt` |
| Description | siehe Schritt 3 |
| Main Category | **Adventure and RPG** |
| Additional Categories | **Armor, Tools, and Weapons**, **Mobs**, **Structures**, **Dimensions** |
| License | **All Rights Reserved** |
| Logo / Avatar | `logo.png` |

Falls die Seite eine Option zu Modpacks oder zur Verteilung über Drittanbieter-Apps anzeigt: **erlaubt lassen**. Sonst können Modpacks und Launcher die Mod nicht laden.

Die Felder für Source, Issues und Wiki darfst du leer lassen.

## 3. Beschreibung mit Banner

Im Beschreibungsfeld steht ganz oben der Platzhalter `BANNER_IMAGE_URL`. Er muss durch einen echten Bild-Link ersetzt werden:

1. Projekt zuerst mit der Beschreibung **ohne** Banner speichern: die erste Zeile (`![Celestial Ascent](BANNER_IMAGE_URL)`) einfach weglassen.
2. Im Projekt den Tab **Images** öffnen und `banner.png` hochladen. Titel: `Celestial Ascent`.
3. Auf das hochgeladene Bild klicken und dessen Adresse kopieren (Rechtsklick → *Bildadresse kopieren*). Sie beginnt mit `https://media.forgecdn.net/attachments/…`.
4. Die Beschreibung bearbeiten und das Banner als erstes Element einfügen:
   - **Editor im Markdown-Modus:** den ganzen Inhalt von `description.md` einfügen und `BANNER_IMAGE_URL` durch den kopierten Link ersetzen.
   - **Normaler Editor (WYSIWYG):** über den Knopf *Source code* (`<>`) den Inhalt von `description.html` einfügen und auch dort `BANNER_IMAGE_URL` ersetzen.
   - Oder direkt im Editor mit dem Bild-Knopf `banner.png` hochladen. Dann brauchst du den Link gar nicht.

## 4. Screenshots (Galerie)

Im Tab **Images** die Bilder aus `gallery/` in der Reihenfolge der Nummern hochladen. Titel und Beschreibung für jedes Bild stehen in `gallery_captions.txt`.

Das erste Bild (`01_astral_seraph.png`) als **Featured** markieren, falls diese Option angeboten wird. Es erscheint dann als Vorschaubild.

## 5. Die Mod-Datei hochladen

Im Projekt **Files → Upload File** öffnen und `celestialascent-1.0.0.jar` hineinziehen.

| Feld | Eintrag |
|---|---|
| Display Name | **Celestial Ascent 1.0.0** |
| Release Type | **Release** |
| Changelog | Inhalt von `changelog.md`; als Format **Markdown** wählen |
| Game Version | **1.21.1** |
| Mod Loader | **NeoForge** |
| Environment | **Client** und **Server** |
| Java | **Java 21** |

Unter **Related Projects** drei Einträge hinzufügen. Dafür jeweils nach dem Namen suchen:

| Projekt | Art |
|---|---|
| **GeckoLib** | **Required Dependency** |
| **Just Enough Items (JEI)** | **Optional Dependency** |
| **ProjectE** | **Optional Dependency** |

Wichtig: Wähle bei GeckoLib das richtige Projekt. Es ist das von *Gecko*, mit Dateien für 1.21.1 und NeoForge. Der CurseForge-Launcher installiert es dann automatisch mit.

Danach auf **Submit** bzw. **Upload** klicken.

## 6. Prüfung durch CurseForge

- Neue Projekte und Dateien werden von CurseForge-Moderatoren geprüft. Das dauert meist einige Stunden bis wenige Tage. Bis dahin steht das Projekt auf *Under Review*.
- Wird etwas abgelehnt, schreibt CurseForge den Grund dazu. Typisch sind eine fehlende englische Beschreibung oder eine falsche Kategorie. Beides ist hier schon vorbereitet.
- Nach der Freigabe ist die Mod öffentlich und im CurseForge-Launcher zu finden.

## 7. Spätere Updates

1. In `gradle.properties` die Version erhöhen (zum Beispiel `mod_version=1.0.1`).
2. Mit `./gradlew build` bauen. Die neue Jar liegt dann in `build/libs/`.
3. In CurseForge unter **Files → Upload File** die neue Jar hochladen, mit einem kurzen Changelog und den gleichen Einstellungen wie in Schritt 5.

## Kurz-Check vor dem Absenden

- [ ] Projektname, Summary und Beschreibung sind auf Englisch
- [ ] Logo hochgeladen
- [ ] Banner-Link in der Beschreibung ersetzt (kein `BANNER_IMAGE_URL` mehr sichtbar)
- [ ] Hauptkategorie und 4 Zusatzkategorien gewählt, Lizenz *All Rights Reserved*
- [ ] Datei: Release, 1.21.1, NeoForge, Client + Server
- [ ] GeckoLib als *Required*, JEI und ProjectE als *Optional* verknüpft
