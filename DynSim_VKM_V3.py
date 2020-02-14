########################################################################################################
# Imports
########################################################################################################
import logging
from time import time
import powerfactory as pf
import math
import json
import sys

# Importiere aus Projektpackages
from main.faults import Faults, Faults_values
from main.utils_db import (read_project_attributes_from_moebase,
                                  convert_df_to_dict,
                                  read_project_attributes_from_excel)
from main.utils_sqlite3 import get_db, get_faults_by_test
from main.pf_functions import (set_grid, del_faults, del_scenarios, create_faults_scenarios,
                               del_res_vars, clear_vis, set_res_vars, create_load_flow_controller,
                               set_load_flow_controller, execute_simulation, execute_export)


########################################################################################################
# START
########################################################################################################
  
# Setup Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(r'C:\Ausgabe_Skript\Log_DynSim.log', mode = "w")
formatter = logging.Formatter(fmt='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.addHandler(file_handler)

# Defniere shortnames, die aus der MOEbase abgerufen werden sollen.
shortnames = ['zYkGradNB',  # Netzimpedanzwinkel am NAP Yk [°]
              'zSkkVAnb',  #  Netzkurzschlussleistung am NAP Sk [kVA]
              'zUnkVnb',  # Nominale Betriebsspannung Un [kV]
              'zUckVnb',  # Vereinbarte Versorgungsspannung Uc [kV]
              'sSPEnapNB',  # Sternpunktbehandlung im gleichen Netz
              'sArtVNetzNB', # Art Vorgelagertes Netz: Freileitungsnetz; Kabelnetz; gemischt; unbekannt
              'zRnetzOhmNB',  # Vorgelagerter Netztransformator: Rnetz [Ohm]
              'zSnetzkVAnb',  #Vorgelagerter Netztransformator: Scheinleistung Snetz [kVA]
              'zXnetzOhmNB',  # Vorgelagerter Netztransformator: Xnetz [Ohm]
              'sAnschlussartEZEnb',  # Anschlussart der EZE (MS-Netz, HS-Netz, UW-Direktanschluss)
              'zImpSPEnb', # Impedanz der SPE [Ohm]
              'zUsollkVnb', # Reglersollspannung Usoll [kV]
              'sAnschlussSonstNAPnb'] # Sonstiges

app = pf.GetApplication() # Greife auf PowerFactory zu
app.EchoOff() # Deaktiviert das User Interface von PowerFactory
app.ClearOutputWindow() # Ausgabefenster leeren
# Eingabeparameter einlesen
script = app.GetCurrentScript()
projektnummer = script.projektnummer
vde = script.vde
type = script.type
t_nachfehler = script.t_nachfehler
flag_load_flow_unsym = script.lfd_unsym
t_sim = script.t_sim

logger.info("----------------------------------------")
logger.info("Aufruf DynSim_VKM")
logger.info("Projektnummer: {}".format(projektnummer))
logger.info("----------------------------------------")

# Funktionsaufruf: read_project_attributes_from_moebase
# Liest die angegeben oder alle Attribute des gewählten Projekts aus der MOEbase/moeProduction-Datenbank.
# Die Attribute werden als Pandas DataFrame zurückgegeben und als Excel-Datei gespeichert. 
# df = read_project_attributes_from_moebase(projektnummer=projektnummer, shortnames=shortnames)
df = read_project_attributes_from_excel()


# Kontrolle des Rückgabewertes
if isinstance(df, str):
    app.PrintError(df)
    logger.error("read_project_attributes_from_moebase: {}".format(df))
    sys.exit()

# Funktionsaufruf: convert_df_to_dict
# Konvertiert eine Pandas DataFrame zu einer Dictionary. 
# Speichert den Wert jeweiligen Wert, der dem shortname zugeordnet ist. 
dict_grid_att = convert_df_to_dict(df)
# Kontrolle des Rückgabewertes
if isinstance(dict_grid_att, str):
    app.PrintError(dict_grid_att)
    logger.error("convert_df_to_dict: {}".format(dict_grid_att))
    sys.exit()

# Ausgabe der abgefragten Attribute
logger.debug("Abgefragte Attribute:")
for key in dict_grid_att.keys():
    logger.debug("{}: {}".format(key, dict_grid_att[key]))

# Funktionsaufruf: calc_grid_data: classmethod von Faults_values
# Berechnet die Netzdaten für das Ersatzschaltbild (ElmVac/ElmSind) in PowerFactory.
# Ergebnisse werden als Class Variables gespeichert.
Faults_values.calc_grid_data(dict_grid_data=dict_grid_att, flag_debug=True)


# Funktionsaufruf: get_db(db_name="DB_Faults.db")
# Connects to sqlite3-database ('db_name') and return Connection and cursor object.
# Connection has to be closed manually with conn.close().
conn, c = get_db(db_name="./data/DB_Faults.db")

# Lade die Fehlerereignisse aus der Tabelle tablenames der sqlite3-Datenbank db_name.
# Mögliche Tabellen:
# FAULTS_4110_TYP1 - Versuchsdefinitionen VDE AR-N 4110/FGW TR8 Rev9 Typ1
# FAULTS_4110_TYP2 - Versuchsdefinitionen VDE AR-N 4110/FGW TR8 Rev9 Typ2
# FAULTS_4120_TYP1 - Versuchsdefinitionen VDE AR-N 4120/FGW TR8 Rev9 Typ1
# FAULTS_4120_TYP2 - Versuchsdefinitionen VDE AR-N 4120/FGW TR8 Rev9 Typ2
tablename = "FAULTS_{}_TYP{}".format(vde, type)
logger.info("Versuche gemäß {} gewählt.".format(tablename))

# Funktionsaufruf: get_faults_by_test(conn, c, tablename, test=None)
# Selects a row or all rows (test=None) of the database table "tablename",
# to which the connection (conn) and the cursor (c) are pointing.
faults_param = get_faults_by_test(conn, c, tablename)
# Kontrolle des Rückgabewertes
if isinstance(faults_param, str):
    app.PrintError(faults_param)
    logger.error("get_faults_by_test: {}".format(faults_param))
    sys.exit()

# Erstelle für jedes Fehlerereignis eine Instanz der Klasse Faults_values
Faults.list_of_faults = []
for fault_param in faults_param:
    # Fault_values: class
    # Eine Klasse, die die alle Fehlerereignisse in PowerFactory gemäß VDE-AR-N 4110/4120 berechnen kann.
    # Berechnet die Netzdaten gemäß FGW TR8 Rev.9 basierend auf den Daten des Anhangs VDE-AR-N 4110/4120 E9.
    Faults_values(fault_param, dict_grid_att)
# Faults.type = type
# Faults.vde = vde
logger.debug("Liste der Fehlerfälle:")
for fault in Faults.list_of_faults:
   logger.debug("{}".format(fault)) 
conn.close()

# Funktionsaufruf: set_grid(app, Faults_values, logger)
# Die Function "set_grid" stellt die durch die Klasse "Fault_values"
# berechneten Netzdaten in das Ersatzschaltbild des Netzes gemäß FGW TR8 ein.
set_grid(app, Faults_values, logger)

# Funktionsaufruf: create_load_flow_controller(app, logger)
# Die Function "create_load_flow_controller" erstellt einen Anlagenregler und nimmt die Voreinstellungen vor
create_load_flow_controller(app, logger)

# Funktionsaufruf: del_faults(app, logger)
# Die Function "del_faults" greift auf den Ordner Fehlerfälle zu und löscht
# alle vorhandenen Fehlerfälle, wenn der String "Versuch_" im Namen enthalten ist.
del_faults(app, logger)

# Funktionsaufruf: del_scenarios(app, logger)
# Die Function "del_scenarios" greift auf den Ordner "Betriebsfälle" zu und löscht
# alle vorhandenen Betriebsfälle, wenn der String "Versuch_" im Namen enthalten ist.
del_scenarios(app, logger)

# Funktionsaufruf: create_faults_scenarios(app, logger, Faults)
# Die Funktion "create_faults_scenarios" looped über die Liste der ausgewählten Fehlerfälle
# und erstellt Betriebs- und Fehlerfälle.
create_faults_scenarios(app, logger, Faults)

# Variablen für verschiedene Messstellen aus json laden
with open("./data/json_res_vars.txt", "r") as f:
    res_vars = json.load(f)
print(res_vars)

# Funktionsaufruf: clear_vis(app, logger, flag_clear=True)
# Die Function "clear_vis" greift auf die VIpages zu und entfernt alle Kurven aus dem Plot,
# wenn "Trafo bus" oder "Line bus" im Namen enthalten ist.
# flag_clear: Wenn flag aktiv, werden alle Kurven aus den Plots entfernt.
clear_vis(app, logger, flag_clear=True)

# Funktionsaufruf: del_res_vars(app, logger, flag_del=True):
# Die Function "del_res_vars" greift auf die Variablenauswahl zu und löscht
# alle vorhandenen Variablenauswahlen, wenn der Name NAP, EZE, MS, NS enthält.
# flag_del: Wenn flag aktiv, werden alle Variablen mit NAP, EZE, MS oder NS im Namen gelöscht
del_res_vars(app, logger, flag_del=True)

# Funktionsaufruf: set_res_vars(app, logger, res_vars, flag_vis=False)
# Die Function "set_res_vars" greift auf die Variablenauswahl zu und löscht
# alle vorhandenen Variablenauswahlen, wenn der der Name NAP, EZE, MS, NS enthält.
# flag_vis: wenn flag aktiv, werden VIPages und VIPlots erstellt. 
set_res_vars(app, logger, res_vars, flag_vis=True)

# Funktionsaufruf: execute_simulation(app, logger, Faults, flag_load_flow_unsym, res_vars):
# Die Function "execute_simulation" führt einen Lastfluss und Berechnung der Anfangsbedingungen durch.
# Die Simulation wird durchgeführt und die Exportfunktion aufgerufen.
# flag_load_flow_unsym: True: Alle Lastflüsse und Berechnung der Anfangsbedingungen werden unsymmetrisch ausgeführt
execute_simulation(app, logger, Faults, flag_load_flow_unsym=flag_load_flow_unsym, res_vars=res_vars, t_sim=t_sim)

app.EchoOn() # Aktiviert das User Interface von PowerFactory

# Zeitauswertung
tend = time()
t = tend-tstart
app.PrintPlain("Zeit: {} s".format(round(t,2)))