# Tool für die automatisierte Segmentierung von Werbeanzeigen in historischen Zeitschriften

Dieses Repository enthält sowohl Routinen zur Vor- und Nachbereitung der Anzeigenseiten, als auch ein Programm zur automatischen Segmentierung und manuellen Nachkorrektur.

## Das Segmentierungstool benutzen 

### Voraussetzungen

Python 3.8 und folgende zusätzliche Bibliotheken:
- tkinter
- matplotlib
- numpy
- scikit-image
- Pillow

### Beispieldaten

Wenn das Repository geklont, oder heruntergeladen wird, liegen im Ordner `/input/prep/bin/` 5 Beispielseiten aus der Zeitschrift "Der Sturm" zum Testen der Anwendung vor. Diese stammen aus dem Digitalisat der Uni Heidelberg (https://doi.org/10.11588/diglit.31770). Die Seiten wurden als Vorbereitung für die Verarbeitung in das .png Format überführt und binarisiert.

### Das Tool starten

Um das Tool zu starten folgende Schritte ausführen:
1. Eine Konsole öffnen
2. In den Ordner /KonsumEdio/python navigieren
3. Die Python-Datei "konsumedio.py" ausführen, z.B. mit dem Befehl: `python3 konsumedio.py`

### Standard input und output anpassen

Beim Öffnen des Tools wird das erste Bild aus dem Standard-Input-Ordner angezeigt und die segmentierten Bilder werden in den Standard-Output-Ordner abgelegt.
Diese Ordner können in der Datei object_app.py in Zeile 381 und 396 ("/output_int/" ersetzen) angepasst werden.
Die Ordner können für jede Session auch über das Interface geändert werden.

Alternativ können eigene Bilder in den Ordner `/input/prep/bin/` gelegt werden.

### Anleitung zur Oberfläche

Nach dem Start wird das erste Bild des Standard-Input-Ordners angezeigt und eine Segmentierung vorgeschlagen.

+ und - : Erhöhen die Iterationstiefe. Mehr oder weniger Schnitte werden gesetzt. Achtung! Durch das Klicken werden manuell hinzugefügte Schnitte überschrieben.

Radio Buttons: Je nachdem, welcher Button ausgewählt ist, passieren bei einem Klick auf das Bild verschiedene Dinge:
- "v": ein vertikaler Schnitt wird an der Mausposition gesetzt (Tastatur: v)
- "h": ein horizontaler Schnitt wird an der Mausposition gesetzt (Tastatur: h)
- "m": zwei Boxen werden miteinander vereint. Dafür erst Box 1 und dann Box 2 anklicken. (Tastatur: m)
- "i": bei einem Klick in eine Box wird diese schwarz eingefärbt und für die Speicherung der Anzeigen ignoriert. Achtung! Lässt sich aktuell nicht rückgängig machen, außer durch einen Klick auf + oder - (Tastatur: i)

Weitere Optionen:
- Define Metadata: Öffnet ein Fenster, in das sich Metadaten für die Seite eingeben lassen. Die Metadaten werden dann für alle weiteren Seiten übernommen. Achtung! Überprüfen, ob das erwünscht ist. Sinnvoll z.B. für Jahrgang und Zeitschrift, für Seite ist eine eigene csv-Datei in der Regel schneller
- Define Paths: Öffnet ein Fenster, in dem sich Input- und Output-Pfad für die aktuelle Session festlegen lassen. 
- Weiter: Wechsle zur nächsten Anzeige (Tastatur: Pfeil nach rechts)
- Speichern: Speichert die segmentierten Anzeigen dieser Bilder

### Workflow

1. Bilder vorbereiten und in den Input-Ordner legen. Die Bilder müssen binär sein und im .png-Format vorliegen.
2. Das Tool öffnen
3. Für jede Anzeige:
  1. Vorgeschlagene Segmentierung begutachten, ggf. Iterationstiefe erhöhen oder senken
  2. Schnitte hinzufügen oder entfernen
  3. Ggf. Metadaten anpassen
  4. Ggf. Boxen schwärzen
  5. Auf Speichern klicken
  6. Zur nächsten Anzeige
4. Die fertigen Anzeigen liegen standardmäßig im Ordner "output_int". Metadaten werden jeweils in den Dateien "page_meta.json" gespeichert.

## Weitere Hilfs-Routinen (Noch nicht gut aufbereitet, Nutzung auf eigene Gefahr!)

**pdf_to_png.py**

*Benötigt Bibliothek pdf2image*

Konvertiert PDF-Dateien in einzelne Bilddateien. Pfade: Zeile 5 & 6, Dateityp: Zeile 18

**move_to_folder.py** 

*Benötigt Bibliothek tqdm*

Verschiebt Bilddateien aus einem Ordner mit Unterordnern (z.B. Jahrgängen) in einem gemeinsamen Ordner. Die Pfade können in Zeile 5 & 6 angepasst werden, der Dateityp in Zeile 13.

**move_corpus.ipynb**

Verschiebt Bilder aus einem Ordner mit unterordnern in einen anderen und benennt diese um (aufsteigende Nummerierung). Ein Mapping zwischen dem Originalnamen und dem neuen Namen wird in einer .json-Datei gespeichert. Diese Methode sollte ausgeführt werden, wenn die Bilder in OCR4All importiert werden, da die Informationen aus den Dateinamen sonst verloren gehen. 

**prep_images.ipynb**

Konvertiert Bilder in grayscale und binäre Bilder und speichert diese in den Ordnern "input/prep/gray" und "input/prep/bin" Pfade: Zelle 2

**create_yearly_csv**

*Benötigt Bibliothek pandas*

Erschafft eine csv-Datei mit einer Liste aller Anzeigen und den zugehörigen Metadaten im in Zelle 4 angegebenen Ordner.


### AutorInnen

Johanna Sophia Danielzik 
im Rahmen einer Projektarbeit am Institut für Digital Humanities Göttingen


