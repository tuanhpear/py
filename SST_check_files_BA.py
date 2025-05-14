# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime
import ConfigParser
import time

# Logging konfigurieren
def setup_logging(log_dir):
    """
    Konfiguriert das Logging: erstellt tägliche Logs im angegebenen Verzeichnis.
    Hängt bei erneutem Start am selben Tag an dieselbe Datei an.
    """
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Log-Dateiname nur mit Tagesdatum
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, 'file_check_{}.log'.format(date_str))
        
        # Logging konfigurieren mit Anfügemodus
        logging.basicConfig(
            filename=log_file,
            filemode='a',  # Anhängen statt überschreiben
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%d.%m.%Y %H:%M:%S',
            level=logging.INFO
        )
        logging.info("====== START des Skriptlaufs ======")
        logging.info("Log-Datei: '{}'".format(log_file))
    except Exception as e:
        print("Fehler beim Einrichten des Loggings: {}".format(e))

# Konfigurationsdatei lesen
def read_config(config_path):
    """
    Liest die Konfigurationsdatei und gibt ein ConfigParser-Objekt zurück.
    """
    try:
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        logging.info("Konfigurationsdatei gelesen: '{}'".format(config_path))
        return config
    except Exception as e:
        logging.error("Fehler beim Lesen der Konfigurationsdatei: {}".format(e))
        raise

# Dateien basierend auf dem Änderungsdatum prüfen
def check_files(section, config):
    logging.info("START - Überprüfung des Verzeichnisses '{}'".format(section))
    
    try:
        path = os.path.expandvars(config.get(section, 'path'))
        pattern = config.get(section, 'pattern')
        start_time = config.get(section, 'start_time')
        end_time = config.get(section, 'end_time')
        check_interval = int(config.get(section, 'check_interval'))
        max_checks = int(config.get(section, 'max_checks'))
    except Exception as e:
        logging.error("Fehler beim Lesen der Parameter aus der Konfigurationsdatei: {}".format(e))
        return

    current_date = datetime.now().strftime('%Y-%m-%d')
    start_dt = datetime.strptime("{} {}".format(current_date, start_time), '%Y-%m-%d %H:%M')
    end_dt = datetime.strptime("{} {}".format(current_date, end_time), '%Y-%m-%d %H:%M')
    now = datetime.now()

    if now < start_dt or now > end_dt:
        logging.info("Verzeichnis '{}' wird übersprungen, da die aktuelle Zeit außerhalb des Zeitintervalls liegt. Aktuelle Zeit: {}".format(section, now.strftime('%H:%M:%S')))
        return

    check_count = 0
    matching_files = []

    while datetime.now() <= end_dt and check_count < max_checks:
        logging.info("Überprüfung {} gestartet für Verzeichnis '{}'".format(check_count + 1, section))
        try:
            files_checked = 0
            for file_name in os.listdir(path):
                if pattern in file_name:
                    files_checked += 1
                    file_path = os.path.join(path, file_name)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if start_dt <= modified_time <= end_dt:
                        if file_name not in matching_files:
                            matching_files.append(file_name)
                            logging.info("Datei '{}' gefunden. Änderungszeit: {}".format(file_name, modified_time.strftime('%H:%M:%S')))

            if files_checked == 0:
                logging.info("Keine Dateien im Verzeichnis '{}' gefunden, die dem Muster '{}' entsprechen.".format(path, pattern))
        except Exception as e:
            logging.error("Fehler beim Verarbeiten der Dateien im Verzeichnis '{}': {}".format(path, e))

        check_count += 1
        if check_count < max_checks:
            time.sleep(check_interval)

    if matching_files:
        logging.info("RESULT - {} Dateien wurden verarbeitet: {}".format(len(matching_files), ", ".join(matching_files)))
    else:
        logging.info("RESULT - Keine passenden Dateien im Verzeichnis '{}' gefunden.".format(section))

    logging.info("END - Überprüfung des Verzeichnisses '{}' abgeschlossen.".format(section))

# Hauptprogramm
def main():
    config_path = '/home/s_tphd/TEMP_LH/Eingehende_Schnittstellen/SST_config.ini'
    log_dir = '/home/s_tphd/TEMP_LH/Eingehende_Schnittstellen/logs/'

    setup_logging(log_dir)

    try:
        config = read_config(config_path)
    except Exception:
        return

    for section in config.sections():
        check_files(section, config)

    logging.info("====== ENDE des Skriptlaufs ======")

if __name__ == '__main__':
    main()
