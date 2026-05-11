import os

class Gate:
    "Represents an individual boarding gate"
    def __init__(self, name):
        self.name = name
        self.occupied = False      # Boolean: True if an aircraft is at the gate
        self.aircraft_id = None    # Stores the ID of the aircraft (e.g., 'DALEN')

class BoardingArea:
    "Represents a specific area containing a list of gates"
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type      # Schengen or non-Schengen
        self.gates = []            # List of Gate objects

class Terminal:
    "Represents an airport terminal (e.g., T1) with its areas and associated airlines"

    def __init__(self, name):
        self.name = name
        self.boarding_areas = []   # List of BoardingArea objects
        self.airlines = []         # List of airline ICAO codes

class BarcelonaAP:
    "Main class representing the Barcelona Airport (LEBL)"
    def __init__(self, code):
        self.code = code
        self.terminals = []        # List of Terminal objects


def SetGates(area, init_gate, end_gate, prefix):

    if end_gate <= init_gate:
        return -1

    # 2. Drop previous list of gates
    area.gates = []

    gate_num = init_gate
    while gate_num <= end_gate:
        gate_name = f"{prefix}{gate_num}"
        # We create the object Gate i we added to the area
        new_gate = Gate(gate_name)
        area.gates.append(new_gate)
        gate_num += 1

    return 0

def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"

    #We check if the file exists
    if not os.path.exists(filename):
        return -1 #File doesn't exist

    #If the file exists...
    terminal.airlines = []

    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line:
                parts = line.split('\t')
                icao_code = parts[-1] #The ICAO code is the las element of the line
                terminal.airlines.append(icao_code)
            i += 1
        return 0

    except Exception:
        return -1

def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        return None
    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        header = lines[0].split()
        icao_code = header[0]
        num_terminals = int(header[1])

        airport = BarcelonaAP(icao_code)

        current_line = 1
        t_count = 0

        while t_count < num_terminals:
            t_data = lines[current_line].split()
            t_name = t_data[1]
            num_areas = int(t_data[2])

            terminal_obj = Terminal(t_name)

            LoadAirlines(terminal_obj, t_name)

            current_line += 1
            a_count = 0

            while a_count < num_areas:
                a_data = lines[current_line].split()
                area_name = a_data[1]
                area_type = a_data[2]
                init_g = int(a_data[4])
                end_g = int(a_data[6])

                area_obj = BoardingArea(area_name, area_type)

                gate_prefix = f"{t_name}{area_name}G"
                SetGates(area_obj, init_g, end_g, gate_prefix)

                terminal_obj.boarding_areas.append(area_obj)

                current_line += 1
                a_count += 1

            airport.terminals.append(terminal_obj)
            t_count += 1

        return airport

    except Exception:
        return None
def GateOccupancy(bcn):
    result = []

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            g = 0
            while g < len(area.gates):
                gate = area.gates[g]
                result.append({
                    "gate_name": gate.name,
                    "status": "occupied" if gate.occupied else "free",
                    "aircraft_id": gate.aircraft_id
                })
                g += 1
            a += 1
        t += 1

    return result

def IsAirlineInTerminal(terminal,name):
    if name == '':
        return False
    if len (terminal.airline) ==0: #Empty list
        return False
    i=0
    while i< len(terminal.airline):
        if terminal.airline[i]==name:
            return True
    i+=1

def SearchTerminal(bcn,name):
    i=0
    while i<len(bcn.terminlals):
        if IsAirlineInTerminal(bcn.terminals[i],name):
            return bcn.terminals[i].name
        i+=1
    return ''
def AssignGate(bcn, aircraft):
    # 1. Buscar la terminal
    terminal_name = SearchTerminal(bcn, aircraft.airline)

    # 2. Si no se encuentra → error
    if terminal_name == "":
        return -1

    # 3. Encontrar el objeto Terminal
    terminal = None
    i = 0
    while i < len(bcn.terminals):
        if bcn.terminals[i].name == terminal_name:
            terminal = bcn.terminals[i]
        i += 1

    # 4. Recorrer áreas buscando tipo Schengen correcto
    a = 0
    while a < len(terminal.boarding_areas):
        area = terminal.boarding_areas[a]
        if area.type == aircraft.schengen:

            # 5. Buscar primera gate libre
            g = 0
            while g < len(area.gates):
                gate = area.gates[g]
                if not gate.occupied:

                    # 6. Asignar y retornar éxito
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id
                    return 0

                g += 1
        a += 1

    # Sin gates libres del tipo correcto
    return -1

def CountFreeGates(bcn): # extra addition
    result=[]
    t=0
    while t<len(bcn.terminals):
        terminal=bcn.terminals[t]
        free = 0
        b=0
        while b<len(terminal.boarding_areas):
            area =terminal.boarding_areas[b]
            g=0
            while g<len(area.gates):
                gate=area.gates[g]
                if not gate.occupied:
                    print(area.gates[g],"is not occupied")
                    free+=1
                g+=1
            b+=1
        t+=1
        result.append((terminal.name,free))
        return result

def FindAircraft(bcn,aircraft_id):
    t=0
    while t<len(bcn.terminals): #No [t]
        terminal = bcn.terminals[t]
        b=0
        while b<len(terminal.boarding_areas):
            area = terminal.boarding_areas[b]
            g=0
            while g<len(area.gates):
                gate=area.gates[g]
                if gate.aircraft_id == aircraft_id:
                   return(terminal.name,area.name,gate.name) #If found, does this
                g+=1
            b+=1
        t+=1
    return None #If didnt find anything

def GetTerminalFlights(bcn,terminal_name):
    result=[]
    t=0
    while t<len(bcn.terminals):
        if bcn.terminals[t].name==terminal_name:
            terminal=bcn.terminals[t]
            b = 0
            while b < len(terminal.boarding_areas):
                area = terminal.boarding_areas[b]
                g = 0
                while g < len(area.gates):
                    gate = area.gates[g]
                    if gate.occupied:
                        result.append((gate.name,gate.aircraft_id))
                    g+=1
                b+=1
            return result
        t+=1
    return None

