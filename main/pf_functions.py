
def set_grid(app, Faults_values, logger):
    """ Die Function "set_grid" stellt die durch die Klasse "Fault_values"
        berechneten Netzdaten in das Ersatzschaltbild des Netzes gemäß FGW TR8 ein. 
    
        Parametrierte Objekt: 
        - Spannungsquelle gleiches Netz
        - Spannungsquelle vorgelagertes Netz
        - Serieninduktivität gleiches Netz
        - Serieninduktivität vorgelagertes Netz
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    Faults_values: Class
        Eine Klasse, die die Netzdaten gemäß VDE-AR-N 4110/4120 berechnet. 
        Netzdaten sind als Klassenvariablen gespeichert.
    logger: 
        logging.logger object
    """
    # GetCalcRelevantObjects aus Parkaufbau
    term = app.GetCalcRelevantObjects('ideales Netz.ElmTerm')[0]
    vac_gleich = app.GetCalcRelevantObjects('*gleich*.ElmVac')[0]
    vac_vorg = app.GetCalcRelevantObjects('*vorg*.ElmVac')[0]
    sind_gleich = app.GetCalcRelevantObjects('*gleich*.ElmSind')[0]
    sind_vorg = app.GetCalcRelevantObjects('*vorg*.ElmSind')[0]
    
    # TODO: Check if all Elements are found
    
    # Spannungsquelle gleiches Netz:
    vac_gleich.Unom = Faults_values.grid_Un
    vac_gleich.usetp = round(Faults_values.grid_Uc/Faults_values.grid_Un, 3)
    vac_gleich.R1 = Faults_values.grid_Ra_gleich
    vac_gleich.X1 = Faults_values.grid_Xa_gleich
    vac_gleich.R0 = Faults_values.grid_R0
    vac_gleich.X0 = Faults_values.grid_X0
    vac_gleich.R2 = Faults_values.grid_Ra_gleich
    vac_gleich.X2 = Faults_values.grid_Xa_gleich
    logger.info("set_grid: Uc: {} kV; Un: {} kV; usetp: {} p.u.".format(Faults_values.grid_Uc, Faults_values.grid_Un, round(Faults_values.grid_Uc/Faults_values.grid_Un, 3)))
    logger.info("set_grid: Spannungsquelle gleiches Netz parametriert")
    
    # Serieninduktivität gleiches Netz:
    sind_gleich.ucn = Faults_values.grid_Un
    sind_gleich.rrea = Faults_values.grid_Rb_gleich
    sind_gleich.xrea = Faults_values.grid_Xb_gleich
    logger.info("set_grid: Serieninduktivität gleiches Netz parametriert")
    
    # Spannungsquelle vorgelagertes Netz:
    vac_vorg.Unom = Faults_values.grid_Un
    vac_vorg.usetp = round(Faults_values.grid_Uc/Faults_values.grid_Un, 3)
    vac_vorg.R1 = Faults_values.grid_Ra_vorg
    vac_vorg.X1 = Faults_values.grid_Xa_vorg
    vac_vorg.R0 = Faults_values.grid_R0
    vac_vorg.X0 = Faults_values.grid_X0
    vac_vorg.R2 = Faults_values.grid_Ra_vorg
    vac_vorg.X2 = Faults_values.grid_Xa_vorg
    logger.info("set_grid: Spannungsquelle vorgelagertes Netz parametriert")
    
    # Serieninduktivität vorgelagertes Netz:
    sind_vorg.ucn = Faults_values.grid_Un
    sind_vorg.rrea = Faults_values.grid_Rb_vorg
    sind_vorg.xrea = Faults_values.grid_Xb_vorg
    logger.info("set_grid: Serieninduktivität vorgelagertes Netz parametriert")

def del_faults(app, logger):
    """ Die Function "del_faults" greift auf den Ordner Fehlerfälle zu und löscht
        alle vorhandenen Fehlerfälle, wenn der String "Versuch_" im Namen enthalten ist.  
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object
    """
    # Auf Ordner "Fehlerfälle" zugreifen und vorhandene Fehlerfaelle entfernen:
    folder_events = app.GetFromStudyCase('IntEvt')
    shc_events = folder_events.GetContents('Versuch_*.*')
    # app.PrintPlain("SHC_Events vorher: {}".format(shc_events))
    if shc_events[0]==[]:
        logger.info("del_faults: Keine löschbaren SHC_Events gefunden.")
        return 
    for del_event in shc_events[0]:
        del_event.Delete()	
    shc_events = folder_events.GetContents()        
    # app.PrintPlain("SHC_Events nacher: {}".format(shc_events))
    logger.info("del_faults: Vorhandene SHC_Events gelöscht.")

def del_scenarios(app, logger):
    """ Die Function "del_scenarios" greift auf den Ordner "Betriebsfälle" zu und löscht
        alle vorhandenen Betriebsfälle, wenn der String "Versuch_" im Namen enthalten ist.  
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object
    """
    # Auf Ordner "Betriebsfälle" zugreifen 
    folder_scenario = app.GetProjectFolder('scen')
    # Auf vorhandene Betriebsfälle zugreifen
    scenarios = folder_scenario.GetContents("Versuch_*.IntScenario")[0]
    # Wenn Betriebsfälle mit "Versuch_*.IntScenario" vorhanden sind, werden diese gelöscht
    app.PrintPlain(scenarios)
    if not scenarios==[]:
        for del_scen in scenarios:
            del_scen.Delete()
    scenarios = folder_scenario.GetContents()
    logger.info("del_scenarios: Vorhandene Betriebsfälle gelöscht!")

def create_faults_scenarios(app, logger, Faults):
    """ 
    Die Funktion "create_faults_scenarios" geht die List der ausgewählten Fehlerfälle durch
    und erstellt Betriebs- und Fehlerfälle.
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object
    Faults: Class
        Eine Instanz enthält alle Parameter für ein Kurzschlussereignis in PowerFactory enthält.
    """
    # Auf Projekt zugreifen
    # Klemmleiste ideales Netz
    term = app.GetCalcRelevantObjects('ideales Netz.ElmTerm')[0]
    # Klemmleiste NVP
    term_nvp = app.GetCalcRelevantObjects('NVP.ElmTerm')[0]
    # Spannungsquelle gleiches Netz
    vac_gleich = app.GetCalcRelevantObjects('*gleich*.ElmVac')[0]
    # Spannungsquelle vorgelagertes Netz
    vac_vorg = app.GetCalcRelevantObjects('*vorg*.ElmVac')[0]
    # Serieninduktivität gleiches Netz
    sind_gleich = app.GetCalcRelevantObjects('*gleich*.ElmSind')[0]
    # Serieninduktivität vorgelagertes Netz
    sind_vorg = app.GetCalcRelevantObjects('*vorg*.ElmSind')[0]
    # Ordner Betriebsfälle
    folder_scenario = app.GetProjectFolder('scen')
    # Ordner Simulationsereignisse
    folder_events = app.GetFromStudyCase('IntEvt')
    # Spannungsquelle U_Sprung 
    vac_sprung = app.GetCalcRelevantObjects('*sprung*.Elmvac')[0]
    # Leistungsschalter ls_sprung_sym 
    ls_sprung_sym = app.GetCalcRelevantObjects('*ls_sprung_sym*.ElmCoup')[0]
    ls_sprung_sym.on_off = 0 # Offen
    ls_sprung_sym.nphase = 3 # Anzahl Phasen: 3
    # Leistungsschalter ls_sprung_unsym
    ls_sprung_unsym = app.GetCalcRelevantObjects('*ls_sprung_unsym*.ElmCoup')[0]
    ls_sprung_unsym.on_off = 0 # Offen
    ls_sprung_unsym.nphase = 2 # Anzahl Phasen: 3
    
    # Schleife über alle gewählten Versuche nach 4110 oder 4120
    for fault in Faults.list_of_faults: 
        # Betriebsfall anlegen und aktivieren
        scenario = folder_scenario.CreateObject('IntScenario', 'Versuch_',fault.test.zfill(2))[0]
        logger.info("create_faults_scenarios: {}, Betriebsfall erstellt:".format(scenario.loc_name))
        scenario.Activate()
        # Kurzschlussereignis oder Schalterereignis erstellen:
        # Wenn Rf=None -> OVRT-Versuch -> Schalterereignis
        # Wenn Rf!=None -> LVRT-Versuch -> Kurzschlussereignis
        if not fault.Rf == None: 
            # Kurzschlussereignisobjekt erstellen: Versuch_XX_on
            shc_event_on = folder_events.CreateObject('EvtShc', 'shc_event')[0]
            # KS-Ereignis: Name
            shc_event_on.loc_name = "Versuch_{}_on".format(fault.test.zfill(2))
            # KS-Ereignis: Absolut s
            shc_event_on.time = 1
            # KS-Ereignis: Fehlertyp         
            shc_event_on.i_shc = fault.fault_type
            # KS-Ereignis: Fehlerwiderstand Ohm
            shc_event_on.R_f = fault.Rf  
            # KS-Ereignis: Fehlerreaktanz Ohm            
            shc_event_on.X_f = fault.Xf
            # KS-Ereignis: Objekt    
            shc_event_on.p_target = term	
            # KS-Ereignis: außer Betrieb setzen
            shc_event_on.outserv = 1
            logger.info("create_faults_scenarios: Kurzschlussereignis erstellt: {}".format(shc_event_on.loc_name))
            
            # Kurzschlussereignisobjekt erstellen: Versuch_XX_off
            shc_event_off = folder_events.CreateObject('EvtShc', 'shc_event')[0]
            # KS-Ereignis: Name
            shc_event_off.loc_name = "Versuch_{}_off".format(fault.test.zfill(2))
            # KS-Ereignis: Absolut s            
            shc_event_off.time = 1 + fault.duration
            # KS-Ereignis: Fehlertyp 
            shc_event_off.i_shc = 4
            # KS-Ereignis: Objekt  
            shc_event_off.p_target = term
            # KS-Ereignis: außer Betrieb setzen
            shc_event_off.outserv = 1
            logger.info("create_faults_scenarios: Kurzschlussereignis erstellt: {}".format(shc_event_off.loc_name))
        else: #  Schalterereignis (Switchevent)
            # Switch-Event erstellen: Versuch_XX_on
            switch_event_on = folder_events.CreateObject('EvtSwitch', 'switch_event')[0]
            # Switch_Event: Name
            switch_event_on.loc_name = "Versuch_{}_on".format(fault.test.zfill(2))
            # Switch_Event: Aktion Schließen (1)
            switch_event_on.i_switch = 1
            # Switch_Event: LS-Schalter/Netzelement
            # Wenn unsymmetrisch, Schalterobjekt ls_sprung_unsym setzen
            if not fault.phases==3:
                switch_event_on.p_target = ls_sprung_unsym
            else: 
                switch_event_on.p_target = ls_sprung_sym
            # Switch_Event: Absolut h
            switch_event_on.hrtime = 0
            # Switch_Event: Absolut min
            switch_event_on.mtime = 0
            # Switch_Event: Absolut s
            switch_event_on.time = 1
            # Switch_Event: außer Betrieb setzen
            switch_event_on.outserv = 1
            logger.info("create_faults_scenarios: Schaltersereignis erstellt: {}".format(switch_event_on.loc_name))
            # Spannungsquelle U_Sprung: Nennspannung Leiter-Leiter /kV
            vac_sprung.Unom = fault.grid_Un
            # Spannungsquelle U_Sprung: Mitsystem Spannung, Betrag /p.u.
            vac_sprung.usetp = round(fault.uf*(fault.grid_Uc/fault.grid_Un), 4)
            logger.info("create_faults_scenarios: Spannungsquelle Sprung eingestellt: Un={} kV, usetp={} p.u.".format(vac_sprung.Unom, round(vac_sprung.usetp, 4)))
            
            # Switch-Event erstellen: Versuch_XX_off
            switch_event_off = folder_events.CreateObject('EvtSwitch', 'switch_event')[0]
            # Switch_Event: Name
            switch_event_off.loc_name = "Versuch_{}_off".format(fault.test.zfill(2))
            # Switch_Event: Aktion öffnen (0)
            switch_event_off.i_switch = 0            
            # Switch_Event: LS-Schalter/Netzelement
            # Wenn unsymmetrisch, Schalterobjekt ls_sprung_unsym setzen
            if fault.phases==2:
                switch_event_off.p_target = ls_sprung_unsym
            else: 
                switch_event_off.p_target = ls_sprung_sym
            # Switch_Event: Absolut h    
            switch_event_off.hrtime = 0
            # Switch_Event: Absolut min
            switch_event_off.mtime = 0
            # Switch_Event: Absolut s
            switch_event_off.time = 1 + fault.duration
            # Switch_Event: außer Betrieb setzen
            switch_event_off.outserv = 1
            
        # Spannungsquelle und Serieninduktivität auswählen:
        if fault.grid == "g":
            # Gleiches Netz wählen
            vac_gleich.outserv = 0
            vac_vorg.outserv = 1 
            sind_gleich.outserv = 0
            sind_vorg.outserv = 1
            vac_on = vac_gleich
            logger.info("create_faults_scenarios: Vorgelagerten Netzes deaktiviert, gleiches Netz aktiviert")
        else:
            # Vorgelagertes Netz wählen
            vac_gleich.outserv = 1
            vac_vorg.outserv = 0 
            sind_gleich.outserv = 1
            sind_vorg.outserv = 0
            vac_on = vac_vorg
            logger.info("create_faults_scenarios: Gleiches Netzes deaktiviert, vorgelagertes Netzes aktiviert")
        
        
        # Vorfehlerspannung für bestimmte Versuche erhöht.
        vac_on.contbar = term_nvp # geregelter Knoten NVP
        vac_on.usetp = vac_on.usetp*fault.uv
        logger.info("create_faults_scenarios: Test {}: Vorfehlerspannung auf {} p.u. gesetzt. Eingestellter Wert für usetp: {} p.u.".format(fault.test,fault.uv, round(vac_on.usetp,3)))
        
        # Anlagenregler einstellen
        # Funktionsaufruf: set_load_flow_controller(app, logger, fault, flag_debug=False)
        # Berechnet die Sollblindleistung für den Anlagenregler für den aktuellen Versuch
        # anhand der Einstellung der EZE im Reiter Lastfluss für Wirkleistung und Blindleistung.  
        set_load_flow_controller(app, logger, fault, flag_debug=False)
        
        # Scenario speichern und deaktivieren
        scenario.Save()
        scenario.Deactivate()  
        logger.info("create_faults_scenarios: Betriebsfall gespeichert und deaktiviert: {}".format(scenario.loc_name))

def del_res_vars(app, logger, flag_del=True):
    """ Die Function "del_res_vars" greift auf die Variablenauswahl zu und löscht
        alle vorhandenen Variablenauswahlen, wenn der der Name NAP, EZE, MS, NS enthält.  
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object
    flag_del: Bool
        wenn flag aktiv, werden alle Variablen mit NAP, EZE, MS oder NS im Namen gelöscht. 
    """
    if flag_del:
        allcalcs = app.GetFromStudyCase('*.ElmRes') #greife auf alle Berechnungsarten zu 
        int_mon = allcalcs.GetContents()
        for del_int_mon in int_mon: 
            if "NAP" or "EZE" or "MS" or "NS" in del_int_mon.loc_name:
                del_int_mon.Delete()
                logger.debug("del_res_vars: Variablenauswahl gelöscht: {}".format(del_int_mon.loc_name))
        logger.info("del_res_vars: Vorhandene Ergebnisvariablen gelöscht.")

def clear_vis(app, logger, flag_clear=True):
    """ Die Function "clear_vis" greift auf die VIpages zu und entfernt alle Kurven aus dem Plot,
        wenn "Trafo bus" oder "Line bus" im Namen enthalten ist. 
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object
    flag_clear: Bool
        wenn flag aktiv, werden alle Kurven aus den Plots entfernt. 
    """
    if flag_clear:
        graphics_board = app.GetGraphicsBoard()
        Pages = graphics_board.GetContents()
        for entry in Pages: 
            if "Line bus" or "Trafo bus" in entry.loc_name: 
                for object in entry.GetContents():
                    object.Clear()
                    logger.debug("clear_vis: VIplot geleert: Page: {}, Plot: {}".format(entry.loc_name, object.loc_name))
        logger.info("clear_vis: VIplots geleert!")
        

def set_res_vars(app, logger, res_vars, flag_vis = False):
    """ Die Function "set_res_vars" greift auf die Variablenauswahl zu und löscht
        alle vorhandenen Variablenauswahlen, wenn der der Name NAP, EZE, MS, NS enthält. 
    
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object
    res_vars: dict
        Nested Dictionary mit Variablenauswahl für verschiedene Elemente
        keys:
            Stufe 1 - EZE, NS, MS, NAP
            Stufe 2 - line, trafo
            Stufe 3 - bus1, bus2, buslv, bushv 
            Stufe 4 - Sym, Unsym, ULE
        Beispiel: 
            Eingabe: res_vars["NAP"]["line"]["bus1"]["Sym"] 
            Ausgabe: ['m:u1:bus1', 'm:I1:bus1', 'm:I1P:bus1', 'm:I1Q:bus1']
    flag_vis: Bool
        wenn flag aktiv, werden VIPages und VIPlots erstellt. 
    """
    allcalcs = app.GetFromStudyCase('*.ElmRes')
    graphics_board = app.GetGraphicsBoard()
    # Auswahlmöglichkeiten: NAP, MS, NS, EZE
    for key in res_vars.keys():
        # Durchsuche Parkaufbau nach Bezeichnung xNAP, xEZE, xNS, xMS
        search_str = "x"+key 
        objects = app.GetCalcRelevantObjects("*{}*.*".format(search_str))
        for counter, object in enumerate(objects):
            app.PrintPlain(object)
            # Variablenauswahl an der Leitung
            if object.GetClassName() == "ElmLne":
                # Auswahl bus1 oder bus2
                if "bus2" in object.loc_name and "bus2" in res_vars[key]["line"]:
                    vars = res_vars[key]["line"]["bus2"]
                    name = "{}{} Line bus2".format(key, counter)
                    # logger.debug("Variablenauswahl für {} (Line bus2): {}".format(object.loc_name, vars))                
                elif "bus1" in res_vars[key]["line"]: # Default für xNAP
                    vars = res_vars[key]["line"]["bus1"]
                    name = "{}{} Line bus1".format(key, counter)
                    # logger.debug("Variablenauswahl für {} (Line bus1): {}".format(object.loc_name, vars))
                else: # Default für xEZE
                    vars = res_vars[key]["line"]["bus2"]
                    name = "{}{} Line bus2".format(key, counter)
                    # logger.debug("Variablenauswahl für {} (Line bus2): {}".format(object.loc_name, vars))
            # Variablenauswahl am Trafo       
            elif object.GetClassName() == "ElmTr2":
                if key == "NS": #  Niederspannungsseitig
                    vars = res_vars[key]["trafo"]["buslv"]
                    name = "{}{} Trafo buslv".format(key, counter)
                    # logger.debug("Variablenauswahl für {} (Trafo buslv): {}".format(object.loc_name, vars))
                elif key == "MS": #  Mittelspannungsseitig
                    vars = res_vars[key]["trafo"]["bushv"]
                    name = "{}{} Trafo bushv".format(key, counter)
                    # logger.debug("Variablenauswahl für {} (Trafo bushv): {}".format(object.loc_name, vars))
            # Variablenauswahl am Synchrongenerator
            elif object.GetClassName() == "ElmSym":
                app.PrintPlain("ElmSym")
                vars = res_vars[key]["ElmSym"]
                app.PrintPlain(vars)
                name = "{}{}".format(key, counter)
                app.PrintPlain(name)
                
            # Erstelle ein Set aus einzigartigen Variablen für jeden Messpunkt
            set_vars = set()
            for i in vars.keys():
                set_add = set(vars[i])
                set_vars.update(set_add)     
            logger.debug("set_res_vars: Variablenauswahl für {} ({}, {}): {}".format(object.loc_name, object.GetClassName(), key, vars))
            
            # Definiere Ergebnissvariablen
            new_IntMon = allcalcs.CreateObject('IntMon', name)[0]
            new_IntMon.loc_name = name
            new_IntMon.obj_id = object
            # Jede Variable des Sets zur Auswahl hinzufügen
            for var in set_vars:
                new_IntMon.AddVar(var)
            logger.info("set_res_vars: Simulationsergebnisse festgelegt: {} ({}, {})".format(object.loc_name, object.GetClassName(), key))  
            
            # Erzeuge VIs, wenn flag_vis gesetzt
            if flag_vis: 
                vi_page = graphics_board.GetPage(name, 1)[0]
                for vi_name in vars.keys():
                    plot = vi_page.GetVI(vi_name, 'VisPlot', 1)[0]
                    # Variablen hinzufügen
                    for var in vars[vi_name]:
                        plot.AddResVars(allcalcs, object, var)            
                    logger.debug("set_res_vars: Plot {} auf Seite {} erstellt und Variablen hinzugefügt.".format(plot.loc_name, vi_page.loc_name))
                logger.info("set_res_vars: VIpage {} angelegt!".format(vi_page.loc_name))

def create_load_flow_controller(app, logger):
    """ 
    Die Function "create_load_flow_controller" erstellt einen Anlagenregler und nimmt die Voreinstellungen vor:
        - Geregelt an Feld zwischen Leitung NAP und Klemmleiste NVP
        - Regelmodus: Blindleistungsregelung
        - Regler außer Betrieb setzen
        - Q=0 kvar voreinstellen
        - EZEs (statischer Generator, Synchrongenerator) mit BDEW und Neu im Namen hinzufügen 
        
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object 
    """    
    # Klemmleiste NVP und dessen Anbindungen auswählen
    term_nvp = app.GetCalcRelevantObjects('NVP.ElmTerm')[0]
    cubs_nvp = term_nvp.GetConnectedCubicles()
    # Synchrongeneratoren/statische Generatoren
    eze_synchron = app.GetCalcRelevantObjects('*.ElmSym')
    eze_stat = app.GetCalcRelevantObjects('*.ElmGenstat')
    # Übernehme bestehende Anlagenregler
    ldf_controller = app.GetCalcRelevantObjects('*.ElmStactrl')
    # Bestehende Anlagenregler werden ersetzt
    for controller in ldf_controller:
        controller.Delete()
        logger.info('create_load_flow_controller: Anlagenregler: Bestehender Anlagenregeler gelöscht')
    # Suche Feld zwischen Klemmleiste NVP und Leitung xNAP
    for cub in cubs_nvp:
        branch = cub.GetBranch()  # übergebe Verbindungszweig an Variable 'Leitung'
        if 'xNAP' in branch.loc_name:  # filtere Verbindungszweige nach Leitung NAP
            cub_nvp = cub  # übergebe Verbindung Klemmleiste NVP - Leitung NAP an Var 'Cub_NVP'
            logger.info('create_load_flow_controller: Anlagenregler: Verbindungsfeld = {}'.format(cub.loc_name))  
    # Übernehme Ordner 'Netzdaten' und dessen Inhalte
    netdat = app.GetProjectFolder('netdat')
    netdat_contents = netdat.GetContents('*.ElmNet')[0][0]
    # Erstelle neuen Anlagenregler
    ldf_controller = netdat_contents.CreateObject('ElmStactrl', 'Anlagenregelung')[0]
    ldf_controller.outserv = 1  # Regler außer Betrieb setzen
    ldf_controller.i_ctrl = 1  # Regelmodus: Blindleistungsregelung
    ldf_controller.p_cub = cub_nvp #Q geregelt am Feld zwischen Klemmleiste NVP und Leitung xNAP
    ldf_controller.qsetp = 0 # Q=0 kvar
    
    for eze in eze_synchron:
        if any(x in eze.loc_name.lower() for x in ["bdew","neu"]):
            eze.c_pstac = ldf_controller
            logger.debug("create_load_flow_controller: EZE '{}' zu Anlagenregler hinzugefügt!".format(eze.loc_name))

    for eze in eze_stat:
        if any(x in eze.loc_name.lower() for x in ["bdew","neu"]):
            eze.c_pstac = ldf_controller
            logger.debug("create_load_flow_controller: EZE '{}' zu Anlagenregler hinzugefügt!".format(eze.loc_name))


def set_load_flow_controller(app, logger, fault, flag_debug=False):
    """ 
    Die Function "set_load_flow_controller" berechnet die Sollblindleistung für den Anlagenregler 
    für den aktuellen Versuch anhand der Einstellung der EZE im Reiter Lastfluss für Wirkleistung
    und Blindleistung. 
    
    Wenn die EZE "BDEW" oder "Neu" im Namen hat, wird die EZE in die Anlagenregelung aufgenommen,
    ansonsten wird die eingetragen Blindleistungseinstellung verwendet.
        
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object 
    fault: Instance of Class
        Enthält die Fehlerdefinition für einen HVRT/LVRT-Versuch
    flag_debug: bool
        True: Aktiviert die Debuggingausgabe in PowerFactory
        Default: False
    """    
    # Anlagenregler
    ldf_controller = app.GetCalcRelevantObjects('*.ElmStactrl')[0]
    ldf_controller.outserv = 0
    # Synchrongeneratoren/statische Generatoren
    eze_synchron = app.GetCalcRelevantObjects('*.ElmSym')
    eze_stat = app.GetCalcRelevantObjects('*.ElmGenstat')
    
    if flag_debug:
        app.PrintPlain(ldf_controller.loc_name)
        app.PrintPlain("fault: {}, qset: {}".format(fault.test, fault.qset))
    
    # Vorzeichen der Blindleistung für über- und untererregten Betrieb anpassen
    if fault.qset == "untererregt":
        vorzeichen = 1
    elif fault.qset == "uebererregt":
        vorzeichen = -1
    else:
        ldf_controller.qsetp = 0
        logger.info("Anlagenregler: 0 Mvar")
        return
    
    # Initialisierungen
    P_A = 0 # Anlagenwirkleistung
    Q_A = 0 # Anlagenblindleistung
    
    # Schleife über alle Synchrongeneratoren
    for eze in eze_synchron:
        # Kommuliere die Anlagenwirkleistung
        P_A += eze.pgini*eze.ngnum
        # Wenn der Name BDEW oder Neu enthält, wird Q_soll = 0.33*P_EZE angenommen.
        if any(x in eze.loc_name.lower() for x in ["bdew","neu"]):
            # Blindleistung = Wirkleistung der EZE * Anzahl der EZE* 0.33 Q/P * 1 (untererregt) oder -1 (übererregt)
            Q = eze.pgini*eze.ngnum*0.33*vorzeichen
            # EZE zum Anlagenregler hinzufügen
            eze.c_pstac = ldf_controller 
        else: 
            # Bei Altanlagen wird aktuelle Blindleistungseinstellung verwendet
            Q = eze.qgini*eze.ngnum
        # Kommuliere die Anlagenblindleistung
        Q_A += Q
        if flag_debug:
            app.PrintPlain("eze: {}, P: {}, Q: {}".format(eze, round(eze.pgini*eze.ngnum,5), round(Q,5)))    
            app.PrintPlain("Gesamt: P_A: {}, Q_A: {}".format(round(P_A,5), round(Q_A,5)))
    
    # Schleife über alle statischen Generatoren
    for eze in eze_stat:
        # Kommuliere die Anlagenwirkleistung
        P_A += eze.pgini*eze.ngnum
        # Wenn der Name BDEW oder Neu enthält, wird Q_soll = 0.33*P_EZE angenommen.
        if any(x in eze.loc_name.lower() for x in ["bdew","neu"]):
            # Blindleistung = Wirkleistung der EZE * Anzahl der EZE* 0.33 Q/P * 1 (untererregt) oder -1 (übererregt)
            Q = eze.pgini*eze.ngnum*0.33*vorzeichen
            # EZE zum Anlagenregler hinzufügen
            eze.c_pstac = ldf_controller 
        else: 
            # Bei Altanlagen wird aktuelle Blindleistungseinstellung verwendet
            Q = eze.qgini*eze.ngnum
            if flag_debug:
                app.PrintPlain("Verwende eingetragenes Vermögen")
        # Kommuliere die Anlagenblindleistung
        Q_A += Q
        if flag_debug:
            app.PrintPlain("eze: {}, P: {}, Q: {}".format(eze, round(eze.pgini*eze.ngnum,5), round(Q,5)))
            app.PrintPlain("Gesamt: P_A: {}, Q_A: {}".format(round(P_A,5), round(Q_A,5)))
    logger.info("Anlagenregler: {} Mvar {}".format(round(Q_A,5), fault.qset))
    # Q-Sollwert des Anlagenreglers gleich berechneter Anlagenblindleistung setzen
    ldf_controller.qsetp = Q_A    

def execute_simulation(app, logger, Faults, flag_load_flow_unsym, res_vars, t_sim):
    """ 
    Die Function "execute_simulation" führt einen Lastfluss und Berechnung der Anfangsbedingungen durch.
    Die Simulation wird durchgeführt und die Exportfunktion aufgerufen. 
        
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object 
    flag_load_flow_unsym: bool
        True: Alle Lastflüsse und Berechnung der Anfangsbedingungen werden unsymmetrisch ausgeführt.
        Default: False
    res_vars: dict
        Nested Dictionary mit Variablenauswahl für verschiedene Elemente
        keys:
            Stufe 1 - EZE, NS, MS, NAP
            Stufe 2 - line, trafo
            Stufe 3 - bus1, bus2, buslv, bushv 
            Stufe 4 - Sym, Unsym, ULE
        Beispiel: 
            Eingabe: res_vars["NAP"]["line"]["bus1"]["Sym"] 
            Ausgabe: ['m:u1:bus1', 'm:I1:bus1', 'm:I1P:bus1', 'm:I1Q:bus1']
    """    
    
    #Initialisierungen-------------------------------------------------------
    folder_scenario = app.GetProjectFolder('scen')
    scenario = folder_scenario.GetContents()
    #Resultfiles und Eventfiles auslesen
    folder_events = app.GetFromStudyCase('IntEvt')
    #Lastfluss
    load_flow = app.GetFromStudyCase('ComLdf')
    #Anfangsbedingungen
    initial_conditions = app.GetFromStudyCase('ComInc')
    #Simulationsstart
    start_simulation = app.GetFromStudyCase('ComSim')
    
    #Simulationseinstellungen des Nutzers einlesen (RMS/EMT), sowie Schrittweite
    if initial_conditions.iopt_sim == 'rms':
        logger.info("execute_simulation: RMS-Simulation, Schrittweite_EMT: {} s, maximale Schrittweite: {} s".format(initial_conditions.dtgrd, initial_conditions.dtgrd_max))
    elif initial_conditions.iopt_sim == 'ins':
        logger.info("execute_simulation: EMT-Simulation, Schrittweite_EMT: {} s, maximale Schrittweite: {} s".format(initial_conditions.dtemt, initial_conditions.dtemt_max))
    logger.info("execute_simulation: Einstellung der Anfangsbedingungen aus PowerFactory-Dialog übernommen")
    
    #Schleife: Simulation der Versuche gemäß gewählter Richtlinie und Typ ausführen.
    for fault in Faults.list_of_faults:
        # Betriebsfall aktivieren
        scenario = folder_scenario.GetContents('Versuch_{}.IntScenario'.format(fault.test.zfill(2)))[0][0]
        scenario.Activate()
        logger.info("execute_simulation: {} aktiviert".format(scenario.loc_name))
        
        # Fehlerereignisse aktivieren
        events = folder_events.GetContents('Versuch_{}_o*.*'.format(fault.test.zfill(2)))[0]
        for event in events:
            app.PrintPlain(event)
            event.outserv = 0
            logger.info("execute_simulation: Fehlerfall {} aktiviert".format(event.loc_name))
        
        # Lastfluss durchführen 
        # load_flow.iopt_sim=0 - symmetrisch
        # load_flow.iopt_sim=1 - unsymmetrisch
        # Flag: Alle Versuche unsymmetrisch berechnen
        if flag_load_flow_unsym:
            load_flow.iopt_sim = 1
            logger.info("execute_simulation: unsymmetrischer Lastfluss gewählt.")
        # Wenn Fehlertyp ungleich 0, unsymmetrisch:    
        elif not fault.phases == 3:
            load_flow.iopt_sim = 1
            logger.info("execute_simulation: unsymmetrischer Lastfluss gewählt.")
        else: 
            load_flow.iopt_sim = 0
            logger.info("execute_simulation: symmetrischer Lastfluss gewählt.")
        err = load_flow.Execute()
        if err == 1:
            logger.error("execute_simulation: Fehler bei der Lastflussberechnung!")
        else:
            logger.info("execute_simulation: Lastflussberechnung erfolgreich durchgeführt.")
            
        # Anfangsbedingungen berechnen
        # iopt_sim="rms" - Effektivwerte
        # iopt_sim="ins" - Momentanwerte
        # iopt_net="sym" - symmetrisch 
        # iopt_net="rst" - unsymmetrisch
        # RMS-Simulation
        if initial_conditions.iopt_sim=="rms": 
            # Flag: Alle Versuche unsymmetrisch berechnen
            if flag_load_flow_unsym:
                initial_conditions.iopt_net = "rst"
            # Wenn Fehlertyp ungleich 0, unsymmetrisch:
            elif not fault.phases == 3:
                initial_conditions.iopt_net = "rst"
            else: 
                initial_conditions.iopt_net = "sym"
        # EMT-Simulation        
        elif initial_conditions.iopt_sim=="ins":
            # initial_conditions.iopt_net = "rst" # immer unsymmetrisch
            logger.debug("execute_simulation: EMT-Simulation bei der Berechnung der Anfangsbedingungen gewählt!")
        err = initial_conditions.Execute()        
        if err == 1:
            logger.error("execute_simulation: Fehler bei der Berechnung der Anfangsbedingungen!")
        else:
            logger.info("execute_simulation: Anfangsbedingungenerfolgreich berechnet.")
        
        start_simulation.tstop = t_sim
        tmin = 1 + fault.duration + 5
        # Simulation starten 
        if start_simulation.tstop < tmin: 
            start_simulation.tstop = tmin
            # "tstop" - Stopp-Zeitpunkt absolut
            logger.info("execute_simulation: minimale Simulationsdauer von {} s gewählt".format(tmin))
        else:
            logger.info("execute_simulation: Simulationsdauer gemäß Einstellung im ComSim-Dialog auf {} s gesetzt".format(start_simulation.tstop))
        start_simulation.Execute()
        
        # Funktionsaufruf: execute_export(app, logger, res_vars, fault) 
        # Die Function "execute_export" exportiert die Simulationsergebnisse 
        logger.info("execute_simulation: Aufruf function execute_export")
        execute_export(app, logger, res_vars, fault)
        
        # Fehlerereignisse aktivieren
        for event in events: 
            event.outserv = 1
            logger.info("execute_simulation: Fehlerfall {} deaktiviert".format(event.loc_name))
        
        #Betriebsfälle speichern und deaktivieren
        scenario.Save()
        scenario.Deactivate()
        logger.info("execute_simulation: Betriebsfall {} gespeichert und deaktiviert".format(scenario.loc_name))

def execute_export(app, logger, res_vars, fault):
    """ 
    Die Function "execute_export" exportiert die Simulationsergebnisse 
        
    Parameters
    ----------
    app: 
        PowerFactory Application Object
    logger: 
        logging.logger object 
    res_vars: dict
        Nested Dictionary mit Variablenauswahl für verschiedene Elemente
        keys:
            Stufe 1 - EZE, NS, MS, NAP
            Stufe 2 - line, trafo
            Stufe 3 - bus1, bus2, buslv, bushv 
            Stufe 4 - Sym, Unsym, ULE
        Beispiel: 
            Eingabe: res_vars["NAP"]["line"]["bus1"]["Sym"] 
            Ausgabe: ['m:u1:bus1', 'm:I1:bus1', 'm:I1P:bus1', 'm:I1Q:bus1']
    fault: Instance of Class
        Enthält die Fehlerdefinition für einen HVRT/LVRT-Versuch
    """       
    
    #Anfangsbedingungen auslesen für Exportunterscheidung    
    initial_conditions = app.GetFromStudyCase('ComInc')
    #greife auf alle Berechnungsarten zu
    allcalcs = app.GetFromStudyCase('*.ElmRes')
    resultobjects = allcalcs.GetContents("*.IntMon")
    #Exportdialog übernehmen
    export = app.GetFromStudyCase('ComRes')
    
    for resultobject in resultobjects[0]:
        # String Formatting
        # loc_name des resultobject bei leerzeichnen in Liste teilen
        name_split = resultobject.loc_name.split()
        # Nummern entfernen
        name_strip = [x.strip("0123456789") for x in name_split]
        key = name_strip[0]
        # Nur Nummer behalten
        number_strip = [int(x) for x in name_split[0] if x.isdigit()]
        logger.debug("execute_export: Ergebnisobjekt: {}, Variablen_Soll: {}".format(resultobject.loc_name, resultobject.vars))
        
        # Variablenauswahl: Leitung 
        if resultobject.obj_id.GetClassName() == "ElmLne":
            # Variablenauswahl: bus1 oder bus2
            if "bus2" in resultobject.loc_name.lower() and "bus2" in res_vars[key]["line"]:
                vars = res_vars[key]["line"]["bus2"]
                logger.debug("execute_export: Messstelle  {},{},{}".format(key, "Leitung", "bus2"))
            elif "bus1" in res_vars[key]["line"]:
                vars = res_vars[key]["line"]["bus1"]
                logger.debug("execute_export: Messstelle  {},{},{}".format(key, "Leitung", "bus1"))
            else: 
                vars = res_vars[key]["line"]["bus2"]
                logger.debug("execute_export: Messstelle  {},{},{}".format(key, "Leitung", "bus1"))
        # Variablenauswahl: Trafo     
        elif resultobject.obj_id.GetClassName() == "ElmTr2":
            # Variablenauswahl: buslv oder bushv
            if key == "NS": #  Niederspannungsseitig
                vars = res_vars[key]["trafo"]["buslv"]
                logger.debug("execute_export: Messstelle  {},{},{}".format(key, "Trafo", "buslv"))
            elif key == "MS": #  Mittelspannungsseitig
                vars = res_vars[key]["trafo"]["bushv"]
                logger.debug("execute_export: Messstelle  {},{},{}".format(key, "Trafo", "bushv"))
                
        # Variablenauswahl: Synchrongenerator 
        elif resultobject.obj_id.GetClassName() == "ElmSym":
            vars = res_vars[key]["ElmSym"]
            logger.debug("execute_export: Messstelle  {},{}".format(key, "ElmSym"))
                
        # var_type: "Sym", "Unsym", "ULE"
        for var_type in vars.keys():
            logger.info("execute_export: var_type: {}, fault_type: {}".format(var_type, fault.fault_type))
            # Überspringe die Ausgabe der symmetrischen Ergebnisse bei unsymmetrischen Versuchen
            if var_type == "Sym" and not fault.phases==3:
                logger.debug("execute_export: var_type=Sym, fault_type!=0, Export überspringen")
                continue
            # Überspringe die Ausgabe der unsymmetrischen Ergebnisse bei symmetrischen Versuchen    
            elif var_type == "Unsym" and fault.phases==3:
                logger.debug("execute_export: var_type=Unsym, fault_type=0, Export überspringen")
                continue
            # Überspringe die Ausgabe der ULE-Ergebnisse bei symmetrischen Versuchen     
            elif var_type == "ULE" and fault.phases==3:
                logger.debug("execute_export: var_type=ULE, fault_type=0, Export überspringen")
                continue
            
            # Ausgabevariablen zur Zeit (b:tnow) hinzufügen
            cvariable = ["b:tnow"]
            objs, elements = [allcalcs], [allcalcs]
            for var in vars[var_type]:
                cvariable.append(var)
                elements.append(resultobject.obj_id)
                objs.append(allcalcs)
            logger.debug("execute_export: export.cvariable: {}".format(cvariable))
            logger.debug("execute_export: export.element: {}".format([x.loc_name for x in elements]))
            logger.debug("execute_export: export.resultobj: {}".format([x.loc_name for x in objs]))
            # Exportieren von: Ergebnisobjekt
            export.pResult = allcalcs
            # Exportieren nach: Textdatei
            export.iopt_exp = 4
            
            # Dateinamen formatieren
            # Für erste Messstelle keine Zahl ausgeben: Versuch1_EZE.dat
            if number_strip[0]==0:
                fname = "Versuch{}_{}.dat".format(fault.test, name_strip[0])
            else:
                # Für erste Messstelle Zahl ausgeben: Versuch1_EZE1.dat
                fname = "Versuch{}_{}.dat".format(fault.test, name_split[0])
            # Für unsymmetrische EMT-Simulation
            if initial_conditions.iopt_sim=="ins" and not fault.phases==3:  # EMT
                fname_split = fname.split('_')
                fname = "{}_EMT_{}".format(fname_split[0], fname_split[1])
            # Für ULE-Ausgabe    
            if var_type == "ULE":
                fname_split = fname.split(".")
                fname = "{}_ULE.{}".format(fname_split[0], fname_split[1])
               
            export.f_name = "C:\\Ausgabe_Skript\\{}".format(fname) # Dateiname     
            export.iopt_csel = 1 # Nur ausgewählte Variablen exportieren
            export.resultobj = objs # Ergebnisobjekt
            export.element = elements # Element
            export.cvariable = cvariable # Variable
            export.iopt_tsel = 0 # Benutzerdefinitertes Intervall off
            export.Execute() # Export ausführen
            logger.debug("execute_export: Datei {} exportiert".format(fname))
            
