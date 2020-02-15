import pandas as pd
import sqlalchemy as db
import math
from os.path import exists

def read_project_attributes_from_moebase(projektnummer=None, shortnames=None):
    """ read_project_attributes_from_moebase: function
    
    Liest die angegeben oder alle Attribute des gewählten Projekts aus der MOEbase/moeProduction-Datenbank.
    Die Attribute werden als Pandas DataFrame zurückgegeben und als Excel-Datei gespeichert. 
    
    Parameters:
    ----------
    projektnummer: stringvalue
        MOE interne eindeutige Projektnummer im Format XX-EZA-XXXX (z.B. 19-EZA-0326)
    shortnames: list (optional)
        Liste mit shortnames der Attribute, die aus der Datenbank MOEbase/moeProduction/additionalattribute gelesen werden sollen.
        Für eine Übersicht der verfügbaren shortnames siehe Reiter Projektdaten im Gesamtkalkulationstool.
        Wenn keine Liste übergeben wird, werden alle Attribute abgefragt.
    
    Returns:
    --------
    None:
        Wenn keine Projektnummer übergeben wird, kann keine Abfrage der Datenbank erfolgen und es wird None zurückgegeben.
    df: pandas dataframe
        Tabelle, die für jedes abgefragtes Attribute die Spalten shortname, type, stringvalue, datevalue, integervalue und booleanvalue hat. 
    """
    
    if projektnummer is None:
        return "Keine Projektnummer übergeben! Datenbankabfrage abgebrochen"
        
    if shortnames is None:
        flag_all = True
    else:
        flag_all = False
    
    projektnummer = " ".join([projektnummer, "AZ"])
    # Datenbankzugriff auf MOEbase/moeProduction
    engine = db.create_engine('postgresql://<INSERT_USER>:<INSERT_PASSWORD@<INSERT_IP>', echo=False)
    metadata = db.MetaData()
    ta_project = db.Table('project', metadata, autoload=True, autoload_with=engine)
    ta_add = db.Table('additionalattribute', metadata, autoload=True, autoload_with=engine)
    conn = engine.connect()

    #Mit der Projektnummer die Tabelle "project" der MOEbase abfragen und die id speichern
    query = db.select([ta_project]).where(ta_project.columns.number == projektnummer)
    ResultProxy = conn.execute(query)
    ResultSet = ResultProxy.first()
    if ResultSet==None:
        return "Die Datenbankabfrage für die Projektnummer {} ist fehlgeschlagen. Es wurde kein Projekt gefunden."
    pid = ResultSet.id
    # Tabelle "additionalattribute" der MOEbase nach der id durchsuchen und alle Treffer speichern
    query = db.select([ta_add]).where(ta_add.columns.projectid == pid)
    ResultProxy = conn.execute(query)
    ResultSet = ResultProxy.fetchall()
    conn.close()
    
    # Pandas DataFrame anlegen
    keys = ResultSet[0].keys()
    df = pd.DataFrame(ResultSet, columns=keys)
    # Lösche nicht benötigte Spalten
    drop_keys = ['position', 'standardattributeid', 'id', 'projectid',]
    for key in drop_keys:
        if key in keys:
            df = df.drop(key, axis = 1)
    # Lösche nicht in shortnames enthaltene Attribute        
    if not flag_all:    
        df = df[df['shortname'].isin(shortnames)]
    df = df.set_index("shortname")
    #Speichere Dataframe als xls
    try:
        df.to_excel('grid_data.xlsx', sheet_name='grid_data')    
    except:
        print("grid_data.xlsx konnte nicht erstellt werden." )
    return df

def read_project_attributes_from_excel(file=r"C:/Ausgabe_Skript/grid_data.xlsx", sheet="grid_data"):
    """ read_project_attributes_from_moebase: function
    
    Liest die angegeben oder alle Attribute des gewählten Projekts aus der MOEbase/moeProduction-Datenbank.
    Die Attribute werden als Pandas DataFrame zurückgegeben und als Excel-Datei gespeichert. 
    
    Parameters:
    ----------
    file: path to file
        Default: "C:/Ausgabe_Skript/grid_data.xlsx"
    sheet: Sheetname as string
        Default: "grid_data"
        
    Returns:
    --------
    None:
        Wenn keine Projektnummer übergeben wird, kann keine Abfrage der Datenbank erfolgen und es wird None zurückgegeben.
    df: pandas dataframe
        Tabelle, die für jedes abgefragtes Attribute die Spalten shortname, type, stringvalue, datevalue, integervalue und booleanvalue hat. 
    """    
    
    if not exists(file):
        return None
        
    with pd.ExcelFile(file) as  xls:
        df = pd.read_excel(xls, sheet, dtype={'stringvalue': str})
        
    if "shortname" in df.columns:
        df.set_index("shortname", inplace=True)
    else:
        return None
    
    df["stringvalue"].replace("nan", '', regex=True, inplace=True)
    print(df.head())
    return df
    
def convert_df_to_dict(df):
    """ convert_df_to_dict: function
    Konvertiert eine Pandas DataFrame zu einer Dictionary. 
    Speichert den Wert jeweiligen Wert, der dem shortname zugeordnet ist. 
    
    Parameters:
    ----------
    df: pandas dataframe
        Tabelle, die für jedes Attribute die Spalten shortname, type, stringvalue, datevalue, integervalue und booleanvalue hat. 
    
    Returns:
    --------
    dict_grid_att: dictionary
        Dictionary mit shortnames als key und dem type entsprechendem Wert als Value
    """
    
    if not isinstance(df, pd.DataFrame):
        return "Es wird ein pandas.DataFrame als Eingabewert erwartet"
    
    # konvertiere Pandas DataFrame zu dictionary
    dict_attributes = df.to_dict("dict")
    dict_grid_att = {}
    
    # Für jedes Attribute wird der entsprechende Wert zu dem shortname gespeichert.
    # type = 1: String
    # type = 2: Integer
    # type = 3: Date
    # type = 4: Boolean
    if not "type" in dict_attributes.keys():
        return "Spalte 'type' existiert nicht im DataFrame"
    else:
        for key in dict_attributes["type"].keys():
            if dict_attributes["type"][key] == 1:
                if not dict_attributes["stringvalue"][key] == "":
                    dict_grid_att[key] = dict_attributes["stringvalue"][key]
            elif dict_attributes["type"][key] == 2:
                if not math.isnan(dict_attributes["integervalue"][key]):
                    dict_grid_att[key] = dict_attributes["integervalue"][key]
            elif dict_attributes["type"][key] == 3:
                    dict_grid_att[key] = dict_attributes["datevalue"][key]
            elif dict_attributes["type"][key] == 4:
                    dict_grid_att[key] = dict_attributes["booleanvalue"][key]
            else:
                dict_grid_att[key] = None
    return dict_grid_att 