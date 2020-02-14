class Faults:
    """
    A class used to represent an Fault event in PowerFactory

    Attributes:
    ----------
    test : str
        number of the fault according to VDE-AR-N 4110/4120
    duration : double
        the duration of the fault event in seconds
    fault_type: int
        the type of the fault event. 
        0 - 3 phase symmetrical fault
        1 - either 2 phase fault or switch event if uf > 1
        2 - 1 phase to earth fault 
    uf : double
        remaining voltage during the fault in p.u. 
    grid: str
        Fault location
        'g' - gleiches Netz
        'v' - vorgelagertes Netz
    qset: str
        reactive power at the Connection Point (NAP)
        '0' - reactive power = 0 kvar 
        'untererregt' -  maximal underexcited reactive power
        'uebererregt'- maximal oeverexcited reactive power
    
    Class Variables
    -------
    num_of_faults: int
        number of class instances (total number of faults)
    list_of_faults
        list of class instances. The list includes all defined faults.
    """
    
    num_of_faults = 0
    list_of_faults = []
    
    def __init__(self, test, duration, fault_type, uf, grid, qset, phases, uv):
        """
        Parameters 
        ----------
        test : str
            number of the fault according to VDE-AR-N 4110/4120
        duration : double
            the duration of the fault event in seconds
        fault_type: int
            the type of the fault event. 
        uf : double
            remaining voltage during the fault in p.u. 
        grid: str
            Fault location
        qset: str
            reactive power at the Connection Point (NAP)
        phases: int
            phases of short circuit (3 - 3 phase symmetric, 2 - 2ph without earth, 1 - 1ph with earth)
        uv: 
            prefault voltage in p.u (Uc)
    """ 
        self.test = test
        self.duration = duration
        self.fault_type = fault_type
        self.uf = uf
        self.grid = grid
        self.qset = qset
        self.phases = phases
        self.uv = uv
        Faults.num_of_faults += 1
        Faults.list_of_faults.append(self)
        
    def __repr__(self):
        """__repr__:
        Formats how a the instance of the class is displayed
        for debugging purposes, when repr oder __repr__ is called.
        e.g. print(repr(fault_01)) -> Faults(1, 0.150, 0, 0.025, 'g', '0')
        """
        return "Faults('{}',{},{}, {}, '{}', '{}', '{}', '{}')".format(self.test, self.duration, self.fault_type, self.uf, self.grid, self.qset, self.phases, self.uv)
        
    def __str__(self):
        """__str__:
        Formats how a the instance of the class is displayed,
        when print() oder str()/__str__ is called.
        e.g. print(fault_01) -> Faultevent Faults(1, 0.150, 0, 0.025, 'g', '0')
        """
        return "Test {} Fault event: duration: {} s, fault_type: {}, uf: {} p.u., grid: {},qset: {}, phases: {}, uv: {})".format(self.test, self.duration, self.fault_type, self.uf, self.grid, self.qset, self.phases, self.uv)  

class Faults_values(Faults):
    """ Fault_values: class
        
    Eine Klasse, die die alle Fehlerereignisse in PowerFactory gemäß VDE-AR-N 4110/4120 berechnen kann.
    Berechnet die Netzdaten gemäß FGW TR8 Rev.9 basierend auf den Daten des Anhangs VDE-AR-N 4110/4120 E9.

    Attributes:
    ----------
    params : tuple
        tuple mit Definition der Fehlerereignisse gemäß VDE-AR-N 4110/4120
        (test, duration, fault_type, uf, grid, qset)

    Class Variables:
    -------
    grid_Ra_gleich: float
        R [Ohm] der Wechselspannungsquelle 1 bei PF (gleiches Netz)
    grid_Xa_gleich: float
        X [Ohm] der Wechselspannungsquelle 1 bei PF (gleiches Netz)
    grid_Rb_gleich: float
        R [Ohm] der Serieninduktivität 1 bei PF (gleiches Netz)		
    grid_Xb_gleich: float
        X [Ohm] der Serieninduktivität 1 bei PF (gleiches Netz)
    grid_Ra_vorg: float
        R [Ohm] der Wechselspannungsquelle 2 bei PF (vorgelagertes Netz)
    grid_Xa_vorg: float
        X [Ohm] der Wechselspannungsquelle 2 bei PF (vorgelagertes Netz)
    grid_Rb_vorg: float
        R [Ohm] der Serieninduktivität 2 bei PF (vorgelagertes Netz)
    grid_Xb_vorg: float
        X [Ohm] der Serieninduktivität 2 bei PF (vorgelagertes Netz)
    flag_UW: boolean 
        UW-Direktanschluss (True) oder kein UW-Direktanschluss (False)
    flag_MS: boolean
        Anschluss der EZA im MS-Netz (True), sonst (False)
    flag_HS: boolean
        Anschluss der EZA im HS-Netz (True), sonst (False)
    grid_Usoll: float
        Reglersollspannung Usoll in kV
    grid_Uc: float
        vereinbarte Versorgungsspannung Uc in kV
    grid_Un: float
        nominale Betriebsspannung Un in kV
    
    Methods:
    -------
    calc_grid_data: @classmethod 
        Berechnet die Netzdaten für das Ersatzschaltbild (ElmVac/ElmSind) in PowerFactory.
    calc_fault_values: 
        Berechnet den Fehlerwiderstand und Fehlerreaktanz in Abhängigkeit der Netzdaten.
    """
    flag_UW = None
    flag_MS = None
    flag_HS = None
    grid_Usoll = None
    grid_Uc = None
    grid_Un = None    
    grid_Ra_gleich = None
    grid_Xa_gleich = None
    grid_Rb_gleich = None
    grid_Xb_gleich = None
    grid_Ra_vorg = None
    grid_Xa_vorg = None
    grid_Rb_vorg = None
    grid_Xb_vorg = None
    grid_R0 = None
    grid_X0 = None

    @classmethod
    def calc_grid_data(cls, dict_grid_data, flag_debug=False):
        """ calc_grid_data: classmethod
            Calculates the grid data for the equivalent circuit (ElmVac/ElmSind) in PowerFactory.
            Results are saved as class variables.
        
        Parameters:
        -----------
        dict_grid_data: dictionary
            Dictionary, welche die Netzdaten gemäß Anhang E9 der VDE-AR-N enthält.
            
            Folgende Keys sind erforderlich: 
                'zUckVnb':  Vereinbarte Versorgungsspannung Uc [kV]
                'zUnkVnb': Nominale Betriebsspannung Un [kV]
                'zSkkVAnb': Netzkurzschlussleistung am NAP Skv [kVA]
                'zYkGradNB': Netzimpedanzwinkel am NAP Yk [°]
                'zUsollkVnb': Reglersollspannung Usoll [kV] bei HS-Parks
            optionale Keys:     
                'sAnschlussartEZEnb': Anschlussart der EZE (MS-Netz, HS-Netz, UW-Direktanschluss)
                    Default: MS-Netz
                'zRnetzOhmNB': Vorgelagerter Netztransformator: Rnetz [Ohm]
                    Wenn nicht vorhanden: Flag_UW: True
                'zXnetzOhmNB': Vorgelagerter Netztransformator: Xnetz [Ohm]
                    Wenn nicht vorhanden: Flag_UW: True
                "sSPEnapNB": Sternpunktbehandlung im gleichen Netz
                    Default: RSPE (R=20 Ohm, X=15000 Ohm)
                "zImpSPEnb": Impedanz der SPE [Ohm]
                    Nur relvant, wenn Sternpunktbehandlung gleich NOSPE/KNOSPE ist.
                    Default: Zm = 30 Ohm
                    
        flag_debug: boolean
            Aktiviert (True) oder deaktiviert (False) die Ausgabe zum Debuggen
        
        Updated Class Variables:
        -----------
        flag_UW: boolean 
            UW-Direktanschluss (True) oder kein UW-Direktanschluss (False)
        flag_MS: boolean
            Anschluss der EZA im MS-Netz (True), sonst (False)
        flag_HS: boolean
            Anschluss der EZA im HS-Netz (True), sonst (False)
        grid_Usoll: float
            Reglersollspannung Usoll in kV
        grid_Uc: float
            vereinbarte Versorgungsspannung Uc in kV
        grid_Un: float
            nominale Betriebsspannung Un in kV
        cls.grid_Ra_gleich: float
            R [Ohm] der Wechselspannungsquelle 1 bei PF (gleiches Netz)
        cls.grid_Xa_gleich: float
            X [Ohm] der Wechselspannungsquelle 1 bei PF (gleiches Netz)
        cls.grid_Rb_gleich: float
            R [Ohm] der Serieninduktivität 1 bei PF (gleiches Netz)		
        cls.grid_Xb_gleich: float
            X [Ohm] der Serieninduktivität 1 bei PF (gleiches Netz)
        cls.grid_Ra_vorg: float
            R [Ohm] der Wechselspannungsquelle 2 bei PF (vorgelagertes Netz)
        cls.grid_Xa_vorg: float
            X [Ohm] der Wechselspannungsquelle 2 bei PF (vorgelagertes Netz)
        cls.grid_Rb_vorg: float
            R [Ohm] der Serieninduktivität 2 bei PF (vorgelagertes Netz)
        cls.grid_Xb_vorg: float
            X [Ohm] der Serieninduktivität 2 bei PF (vorgelagertes Netz)
        cls.grid_R0: float
            Nullsystemwiderstand R0 [Ohm] der Wechselspannungsquellen in PowerFactory
        cls.grid_X0
            Nullsystemreaktanz X0 [Ohm] der Wechselspannungsquellen in PowerFactory
        
        ToDo:
        -----------
        - Flag debug durch logger ersetzen

        """
        import math
        import sys
        
        # Attribute aus der Moebase auf Eintragung und Wert überprüfen:
        # 'zUnkVnb' - Nominale Betriebsspannung Un [kV]
        # 'zUckVnb' - Vereinbarte Versorgungsspannung Uc [kV]
        # 'zSkkVAnb' - Netzkurzschlussleistung am NAP Sk [kVA]
        # 'zYkGradNB' - Netzimpedanzwinkel am NAP Yk [°]
        for key in ['zUnkVnb', 'zUckVnb', 'zSkkVAnb', 'zYkGradNB']:
            try:
                value = float(dict_grid_data[key].replace(",", "."))
            except KeyError as e: 
                print("Key not in dict_grad_data: {}".format(e))
                print("Bitte Angabe des Attribut in der Moebase prüfen!")
                sys.exit()
            except ValueError as e: 
                print("Kein gültiger Wert für: {}".format(e))
                print("Bitte Angabe des Attribut in der Moebase prüfen!")
                sys.exit()
            else:
                if key == 'zUnkVnb':
                    # Nominale Betriebsspannung Un [kV]
                    Un = value
                elif key == 'zUckVnb':
                    # Vereinbarte Versorgungsspannung Uc [kV]
                    Uc = value
                elif key == 'zSkkVAnb':
                    # Netzkurzschlussleistung am NAP Sk [kVA]
                    Skvmin = value
                elif key == 'zYkGradNB':
                    # Netzimpedanzwinkel am NAP Yk [°]
                    Ykv = value
        
        # Prüfe die Anschlussart der EZE
        # Gültige Werte: MS-Netz; MS-Netz (reine Einspeiseleitung); HS-Netz oder UW-Direktanschluss ist
        # Default: MS-Netz
        try:
            Anschlussart = dict_grid_data['sAnschlussartEZEnb']
            print('Anschlussart: {}'.format(Anschlussart))
        except KeyError as e:
            print("Key not in dict_grad_data: {}".format(e))
            print("MS-Netz angenommen!")
            Anschlussart = "MS-Netz"
            
        if not Anschlussart == None:
            if Anschlussart.strip() in ["MS-Netz", "MS-Netz (reine Einspeiseleistung)"]:
                flag_MS = True
                flag_HS = False
                flag_UW = False
            elif Anschlussart.strip() == "UW-Direktanschluss":
                flag_MS = True
                flag_HS = False
                flag_UW = True
            elif Anschlussart.strip() == "HS-Netz":
                flag_HS = True
                flag_MS = False
                flag_UW = False
            else:
                print("Keine gültiger Wert in der Moebase für das Attribut: Anschlussart der EZE")
                print("gültige Werte: MS-Netz; MS-Netz (reine Einspeiseleitung); HS-Netz; UW-Direktanschluss")
                print("MS-Netz angenommen!")                
                flag_MS = True
                flag_HS = False
                flag_UW = False
        
        # Wenn Anschluss im MS-Netz und kein UW-Direktanschluss, prüfe ob Daten für den vorgelagerten Netztrafo vorhanden sind.
        if flag_MS and not flag_UW:
            try: 
                RT = dict_grid_data['zRnetzOhmNB']
                XT = dict_grid_data['zXnetzOhmNB']
            except KeyError as e:
                print("Key not in dict_grad_data: {}".format(e))
                print("Annahme: Keine Trafodaten vorhanden!")
                flag_UW = True
            else:
                try:
                    # Konvertiere RT und XT von String zu float 
                    # Ersetze Komma durch Punkt
                    RT = float(RT.replace(",", "."))
                    XT = float(XT.replace(",", "."))
                except ValueError as e:
                    print("Kein gültiger Wert für Vorgelagerter Netztransformator: Rnetz oder Xnetz")
                    print("Trafodaten werden vernachlässigt!")
                    flag_UW = True
                    
        # Wenn Anschluss im HS-Netz oder UW-Direktanschluss, hole zusätzlich das Attribut Reglersollspannung
        if flag_HS or flag_UW:
            try: 
                Usoll = float(dict_grid_data['zUsollkVnb'].replace(",", "."))
            except KeyError as e: 
                print("Key not in dict_grad_data: {}".format(e))
                print("Bitte Angabe des Attributs in der Moebase prüfen!")
                sys.exit()
            except ValueError as e: 
                print("Kein gültiger Wert für: {}".format(e))
                print("Bitte Angabe des Attributs in der Moebase prüfen!")
                sys.exit()
            else: 
                cls.grid_Usoll = Usoll  
        
        # Speichere Flags in cls
        cls.flag_UW = flag_UW
        cls.flag_MS = flag_MS
        cls.flag_HS = flag_HS
        cls.grid_Uc = Uc
        cls.grid_Un = Un

        # Berechne Netzimpedanz ZN, Netzwiederstand RN und Netzreaktanz XN
        ZN = round(Un*Un*1000/(Skvmin), 7)  # Ohm
        RN = round(ZN*math.cos(math.radians(Ykv)), 7)  # Ohm
        XN = round(ZN*math.sin(math.radians(Ykv)), 7)  # Ohm
        
        # Berechne Za und Zb für Ersatzschaltbild
        cls.grid_Ra_vorg = round(0.1*RN, 5)
        cls.grid_Xa_vorg = round(0.1*XN, 5)
        cls.grid_Rb_vorg = round(0.9*RN, 5)
        cls.grid_Xb_vorg = round(0.9*XN, 5)
        if flag_MS and not flag_UW:
            cls.grid_Ra_gleich = RT
            cls.grid_Xa_gleich = XT
            cls.grid_Rb_gleich = round(RN - RT, 5)
            cls.grid_Xb_gleich = round(XN - XT, 5)
        elif flag_HS or flag_UW:
            cls.grid_Ra_gleich = RN
            cls.grid_Xa_gleich = XN
            cls.grid_Rb_gleich = 0
            cls.grid_Xb_gleich = 0
            
        # Berechne die Nullsystemimpedanz Z0 bzw. R0/X0
        # Sternpunkterdung (SPE)
        # gültige Werte:  
        # Starre Sternpunkterdung (SSPE)
        # Resonanzsternpunkterdung (RSPE)
        # Isoliert (OSPE)
        # Nierderohmige Sternpunkterdung (NOSPE)
        # kurzzeitig niederohmige Sternpunkterdnung (KNOSPE)
        SPE_values = ["Starre Sternpunkterdung (SSPE)",
                      "Resonanzsternpunkterdung (RSPE)",
                      "Isoliert (OSPE)",
                      "Niederohmige Sternpunkterdung (NOSPE)",
                      "kurzzeitig niederohmige Sternpunkterdnung (KNOSPE)"]               
        try:
            SPE = dict_grid_data["sSPEnapNB"]
        except KeyError as e:
            # Keine Angabe in der Moebase
            print("Key not in dict_grad_data: {}".format(e))
            print("Resonanzsternpunkterdung angenommen!")
            cls.grid_R0 = 20
            cls.grid_X0 = 15000
        else:
            # Prüfe ob ein gültiger Wert gewählt wurde. Wenn nicht, wird RSPE angenommen.
            if SPE in SPE_values:
                # SSPE
                if SPE == "Starre Sternpunkterdung (SSPE)":
                    cls.grid_R0 = cls.grid_Ra_gleich
                    cls.grid_X0 = cls.grid_Xa_gleich
                # OSPE / RSPE)
                elif SPE == "Isoliert (OSPE)" or SPE == "Resonanzsternpunkterdung (RSPE)":
                    cls.grid_R0 = 20
                    cls.grid_X0 = 15000
                # NOSPE / KNOSPE
                elif SPE == "kurzzeitig niederohmige Sternpunkterdnung (KNOSPE)" or SPE == "Niederohmige Sternpunkterdung (NOSPE)":
                    # Bei NOSPE oder Knospe wird geprüft, ob ein Wert für die Impedanz
                    # der Sternpunkterdnung Zspe in der MOEbase angegeben wurde.
                    # Wenn ja: R0 = 3*Zspe + Ra, X0 = 0
                    # Wenn nein oder ungültiger Wert R0 = 30 Ohm + Ra, X0 = 0
                    try: 
                        Zspe = float(dict_grid_data["zImpSPEnb"].replace(",","."))
                    except KeyError as e:
                        # R0 = 30 Ohm + Ra, X0 = 0
                        print("Key not in dict_grad_data: {}".format(e))
                        print("Annahme: R0= 30 Ohm + Ra, X0 = 0")
                        cls.grid_R0 = 30 + cls.grid_Ra_gleich
                        cls.grid_X0 = 0
                    except ValueError as e:
                        # R0 = 30 Ohm + Ra, X0 = 0
                        print("Kein gültiger Wert für: {}".format(e))
                        print("Annahme: R0= 30 Ohm + Ra, X0 = 0")    
                        cls.grid_R0 = round(30 + cls.grid_Ra_gleich,4)
                        cls.grid_X0 = 0
                    else:
                        # R0 = 3*Zspe + Ra
                        cls.grid_R0 = round(3*Zspe + cls.grid_Ra_gleich, 4)
                        cls.grid_X0 = 0
            else:
                print("Kein gültiger Wert für die Sternpunkterdung")
                print("Resonanzsternpunkterdung angenommen!")       
                cls.grid_R0 = 20
                cls.grid_X0 = 15000  

        # Kontrollausgabe Netzparameter
        if flag_debug:
            print("flag_MS: {}".format(flag_MS))
            print("flag_HS: {}".format(flag_HS))
            print("flag_UW: {}".format(flag_UW))
            if flag_UW:
                print("Usoll = {} kV".format(Usoll))
            print("Uc = {} kV".format(Uc))
            print("Un = {} kV".format(Un))
            print('Skvmin = {} kVA'.format(Skvmin))
            print('Ykv = {} Grad'.format(Ykv))
            if flag_MS and not flag_UW:
                print('RT = {} Ohm'.format(RT))
                print('XT = {} Ohm'.format(XT))
            print('ZN = {} Ohm'.format(ZN))
            print('RN = {} Ohm'.format(RN))
            print('XN = {} Ohm'.format(XN))
            print('Ra_gleich = {} Ohm'.format(cls.grid_Ra_gleich))
            print('Xa_gleich = {} Ohm'.format(cls.grid_Xa_gleich))
            print('Rb_gleich = {} Ohm'.format(cls.grid_Rb_gleich))
            print('Xb_gleich = {} Ohm'.format(cls.grid_Xb_gleich))
            print('Ra_vorg = {} Ohm'.format(cls.grid_Ra_vorg))
            print('Xa_vorg = {} Ohm'.format(cls.grid_Xa_vorg))
            print('Rb_vorg = {} Ohm'.format(cls.grid_Rb_vorg))
            print('Xb_vorg  = {} Ohm'.format(cls.grid_Xb_vorg))
            print("R0 = {} Ohm".format(cls.grid_R0))
            print("X0 = {} Ohm".format(cls.grid_X0))

    def calc_fault_values(self, dict_grid_data):
        """ calc_fault_values: method
            Calculates the fault resistance and fault reactance depending on the grid data        
        
        Parameters:
        -----------
        dict_grid_data: dictionary
            Dictionary, welche die Netzdaten gemäß Anhang E9 der VDE-AR-N enthält.
            
            Folgende Keys sind erforderlich: 
            "sArtVNetzNB": string
                Art des vorgelagerten Netzes 
                Optionen: unbekannt, gemischt, Freileitungsnetz, Kabelnetz
        
        Updated Instance Variables: 
        ---------------------------
        self.Rf: float
            Fehlerwiderstand Rf in Ohm für die aktuelle Instanz
        self.Xf: float
            Fehlerreaktanz Xf in Ohm für die aktuelle Instanz
        """
        from math import radians, tan, sqrt
        
        flag_MS = self.flag_MS
        flag_HS = self.flag_HS
        uf = self.uf/self.uv
        
        # Unterscheidung gleiches/vorgelagertes Netz
        if self.grid == "g":
            Ra = self.grid_Ra_gleich
            Xa = self.grid_Xa_gleich
        else: 
            Ra = self.grid_Ra_vorg
            Xa = self.grid_Xa_vorg
        
        # Frage die Art des vorgelagerten Netzes ab.
        # Optionen: unbekannt, gemischt, Freileitungsnetz, Kabelnetz
        # Default: unbekannt
        try: 
            grid_type = dict_grid_data["sArtVNetzNB"]
        except KeyError as e:
            print("Key not in dict_grad_data: {}".format(e))
            print("Annahme: Art des vorgl. Netzes: unbekannt")
            grid_type = "unbekannt"
        else:   
            if not grid_type in ["unbekannt", "gemischt","Freileitungsnetz", "Kabelnetz"]:
                print("Kein gültiger Wert für die Art des vorgelagerten Netzes")
                print("Annahme: Art des vorgl. Netzes: unbekannt")
                grid_type = "unbekannt"
        
        #Bestimmung des Fehlerimpedanzwinkels Psif
        if self.flag_HS: 
            if grid_type == "Freileitungsnetz":
                Psif = 75
            else: # unbekannt, gemischt, Kabelnetz
                Psif = 70
        elif self.flag_MS:
            if grid_type == "Freileitungsnetz":
                Psif = 50
            else: # unbekannt, gemischt, Kabelnetz
                Psif = 30
        else: 
            Psif = 30 
        
        print("Test No.: {}".format(self.test))    
        print("Psif: {} Grad".format(Psif))
        print("uf: {} p.u.".format(uf))
        
        # Berechne Rf und Xf für Versuche mit Fehlerspannung <= 1 p.u.
        if self.uf <= 1:
            # Formeln gemäß FGW TR8 Rev 9
            A = tan(radians(Psif))
            B = ((uf**2)-1)*(1+(A**2))
            p = (2*(uf**2)*(Ra+A*Xa))/B
            q = ((uf**2)*((Ra**2)+(Xa**2)))/B
            self.Rf = -p/2 + sqrt((p**2)/4 - q)
            # Fehlerwiderstand wird bei unsymmetrischen Fehlern verdoppelt
            if not self.fault_type==0 and not self.fault_type==2 : 
                self.Rf *= 2
                print("unsymmetrischer Fehler => Rf*2")
            self.Xf = self.Rf*A
            # Debuggingausgabe
            print("A = {}".format(A))
            print("B = {}".format(B))
            print("p = {}".format(p))
            print("q = {}".format(q))
        else: 
            # Wenn Fehlerspannung > 1, werden keine Werte für Rf und Xf berechnet
            self.Rf = None
            self.Xf = None
            
        # Debuggingausgabe
        print("Rf [Ohm] = {} ".format(self.Rf))
        print("Xf [Ohm] = {}\n\n".format(self.Xf))
            
    def __init__(self, params, dict_grid_data):
        test, duration, fault_type, uf, grid, qset, phases, uv = params
        super().__init__(test, duration, fault_type, uf, grid, qset, phases, uv)
        self.calc_fault_values(dict_grid_data)