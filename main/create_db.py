""" create_db.py 

Erstellen einer Datenbank für Fehlereignisse
gemäß VDE-AR-4110 und 4120 (Typ1/2)

Jeder Durchlauf des Skriptes erstellt eine
Tabelle in der gewählten Datenbank. Die Datenbank
sollte vorher noch nicht existieren. 

"""
import sqlite3
from faults import Faults
from utils_sqlite3 import get_db, insert_fault, get_faults_by_test, update_fault, remove_fault

#####################################################################################
# Start 
#####################################################################################

# Eingabe des Datenbanknames
db_name = r"../data/DB_Faults.db"
# db_name = ":memory:"

#Öffnen der Datenbank
conn, c = get_db(db_name=db_name)

"""
Fehlereignisse für die Richtlinien VDE-AR-N-4110 
und VDE-AR-N-4120 (Typ1 und Typ2) anlegen

Auswahl durch ein-/auskommentieren
""" 

for i in range(4):
    Faults.num_of_faults = 0
    Faults.list_of_faults = []
    if i == 0:
        # VDE-AR-N-4110 Typ 1
        tablename = "FAULTS_4110_TYP1"
        fault_01 = Faults(1, 0.150, 0, 0.325, 'g', 'untererregt', 3, 0.95)
        fault_02 = Faults(2, 0.150, 0, 0.500, 'g', 'untererregt', 3, 0.95)
        fault_03 = Faults(3, 0.967, 0, 0.750, 'g', 'untererregt', 3, 0.95)
        fault_04 = Faults(4, 3.000, 0, 0.925, 'g', 'untererregt', 3, 1.00)
        fault_05 = Faults(5, 0.220, 1, 0.325, 'g', 'untererregt', 2, 0.95)
        fault_06 = Faults(6, 0.220, 1, 0.500, 'g', 'untererregt', 2, 0.95)
        fault_07 = Faults(7, 3.000, 1, 0.750, 'g', 'untererregt', 2, 0.95)
        fault_08 = Faults(8, 3.000, 1, 0.925, 'g', 'untererregt', 2, 1.00)
        fault_09 = Faults(9, 5.000, 1, 1.050, 'g', 'uebererregt', 3, 1.00)
        fault_10 = Faults(10, 5.000, 1, 1.200, 'g', 'uebererregt', 3, 1.05)
        fault_11 = Faults(11, 5.000, 1, 1.150, 'g', 'uebererregt', 2, 1.00)
        fault_12 = Faults(12, 0.967, 0, 0.750, 'v', 'untererregt', 3, 0.95)
        fault_13 = Faults(13, 0.220, 2, 0.325, 'g', 'untererregt', 1, 0.95)
        fault_14 = Faults(14, 60.000, 1, 1.150, 'g', '0', 3, 1.00)
        fault_15 = Faults(15, 60.000, 0, 0.850, 'g', '0', 3, 1.00)
    elif i == 1: 
        # VDE-AR-N-4110 Typ 2
        tablename = "FAULTS_4110_TYP2"
        fault_01 = Faults(1, 0.557, 0, 0.250, 'g', 'untererregt', 3, 1.00)
        fault_02 = Faults(2, 1.575, 0, 0.500, 'g', 'uebererregt', 3, 1.00)
        fault_03 = Faults(3, 2.593, 0, 0.750, 'g', 'untererregt', 3, 1.00)
        fault_04 = Faults(4, 3.000, 0, 0.925, 'g', '0', 3, 1.00)
        fault_05 = Faults(5, 0.683, 1, 0.250, 'g', 'untererregt', 2, 1.00)
        fault_06 = Faults(6, 1.842, 1, 0.500, 'g', 'untererregt', 2, 1.00)
        fault_07 = Faults(7, 3.000, 1, 0.750, 'g', 'uebererregt', 2, 1.00)
        fault_08 = Faults(8, 3.000, 1, 0.925, 'g', '0', 2, 1.00)
        fault_09 = Faults(9, 5.000, 1, 1.050, 'g', 'uebererregt', 3, 1.00)
        fault_10 = Faults(10, 5.000, 1, 1.200, 'g', 'uebererregt', 3, 1.05)
        fault_11 = Faults(11, 5.000, 1, 1.150, 'g', 'uebererregt', 2, 1.00)
        fault_12 = Faults(12, 2.593, 0, 0.750, 'v', 'untererregt', 3, 1.00)
        fault_13 = Faults(13, 0.683, 2, 0.250, 'g', '0', 1, 1.00)
        fault_14 = Faults(14, 60.000, 1, 1.150, 'g', '0', 3, 1.00)
        fault_15 = Faults(15, 60.000, 0, 0.850, 'g', '0', 3, 1.00)
    elif i == 2:
        # VDE-AR-N-4120 Typ 1 
        tablename = "FAULTS_4120_TYP1"
        fault_01 = Faults(1, 0.150, 0, 0.025, 'g', 'untererregt', 3, 0.95)
        fault_02 = Faults(2, 0.150, 0, 0.250, 'g', 'untererregt', 3, 0.95)
        fault_03 = Faults(3, 0.233, 0, 0.500, 'g', 'untererregt', 3, 0.95)
        fault_04 = Faults(4, 0.883, 0, 0.750, 'g', 'untererregt', 3, 0.95)
        fault_05 = Faults(5, 3.000, 1, 0.925, 'g', 'untererregt', 3, 1.00)
        fault_06 = Faults(6, 0.220, 1, 0.025, 'g', 'untererregt', 2, 0.95)
        fault_07 = Faults(7, 0.220, 1, 0.250, 'g', 'untererregt', 2, 0.95)
        fault_08 = Faults(8, 0.384, 1, 0.500, 'g', 'untererregt', 2, 0.95)
        fault_09 = Faults(9, 3.000, 1,  0.750, 'g', 'untererregt', 2, 0.95)
        fault_10 = Faults(10, 3.000, 1, 0.925, 'g', 'untererregt', 2, 1.00)
        fault_11 = Faults(11, 5.000, 1, 1.050, 'g', 'uebererregt', 3, 1.00)
        fault_12 = Faults(12, 5.000, 1, 1.200, 'g', 'uebererregt', 3, 1.10)
        fault_13 = Faults(13, 5.000, 1, 1.100, 'g', 'uebererregt', 2, 1.00)
        fault_14 = Faults(14, 0.833, 0, 0.750, 'v', 'untererregt', 3, 0.95)
        fault_15 = Faults(15, 0.220, 2, 0.025, 'g', 'untererreg', 1, 0.95)
        fault_16 = Faults(16, 60.000, 1, 1.150, 'g', '0', 3, 1.00)
        fault_17 = Faults(17, 60.000, 2, 0.850, 'g', '0', 3, 1.00)
    elif i == 3:
        # VDE-AR-N-4120 Typ 2 
        tablename = "FAULTS_4120_TYP2"
        fault_01 = Faults(1, 0.150, 0, 0.000, 'g', '0', 3, 1.00)
        fault_02 = Faults(2, 0.988, 0, 0.250, 'g', 'untererregt', 3, 1.00)
        fault_03 = Faults(3, 1.826, 0, 0.500, 'g', 'uebererregt', 3, 1.00)
        fault_04 = Faults(4, 2.664, 0, 0.750, 'g', 'untererregt', 3, 1.00)
        fault_05 = Faults(5, 3.000, 1, 0.925, 'g', '0', 3, 1.00)
        fault_06 = Faults(6, 0.220, 1, 0.000, 'g', '0', 2, 1.00)
        fault_07 = Faults(7, 1.147, 1, 0.250, 'g', 'untererregt', 2, 1.00)
        fault_08 = Faults(8, 2.073, 1, 0.500, 'g', 'untererregt', 2, 1.00)
        fault_09 = Faults(9, 3.000, 1,  0.750, 'g', 'uebererregt', 2, 1.00)
        fault_10 = Faults(10, 3.000, 1, 0.925, 'g', '0', 2, 1.00)
        fault_11 = Faults(11, 5.000, 1, 1.050, 'g', 'uebererregt', 3, 1.00)
        fault_12 = Faults(12, 5.000, 1, 1.200, 'g', 'uebererregt', 3, 1.00)
        fault_13 = Faults(13, 5.000, 1, 1.100, 'g', 'uebererregt', 2, 1.10)
        fault_14 = Faults(14, 2.664, 0, 0.750, 'v', 'untererregt', 3, 1.00)
        fault_15 = Faults(15, 0.220, 2, 0.000, 'g', '0', 1, 1.00)
        fault_16 = Faults(16, 60.000, 1, 1.150, 'g', '0', 3, 1.00)
        fault_17 = Faults(17, 60.000, 2, 0.850, 'g', '0', 3, 1.00)
    
    table = "CREATE TABLE {} (test text, duration real, fault_type int, uf real, grid text, qset text, phases int, uv real)".format(tablename)
    print("Tabelle {} erzeugt.".format(tablename))
    c.execute(table)	
    
    # Fehlereignisse in Datenbank schreiben 
    print("Anzahl Fehlereignisse: {}".format(Faults.num_of_faults))
    for fault in Faults.list_of_faults:
        # print(fault)
        insert_fault(conn, c, tablename, fault)
        print('Versuch{}: Fehlerereignis aufgenommen: {}'.format(fault.test, fault))
