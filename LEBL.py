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
                parts = line.split()
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
    if len (terminal.airlines) ==0: #Empty list
        return False
    i=0
    while i< len(terminal.airlines):
        if terminal.airlines[i]==name:
            return True
        i+=1
    return False

def SearchTerminal(bcn,name):
    i=0
    while i<len(bcn.terminals):
        if IsAirlineInTerminal(bcn.terminals[i],name):
            return bcn.terminals[i].name
        i+=1
    return ''

def AssignGate(bcn, aircraft, is_schengen):
    terminal_name = SearchTerminal(bcn, aircraft.airline)
    if terminal_name == "":
        # Fallback: use first terminal
        terminal = bcn.terminals[0]
    else:
        terminal = None
        i = 0
        while i < len(bcn.terminals):
            if bcn.terminals[i].name == terminal_name:
                terminal = bcn.terminals[i]
            i += 1
    if terminal is None:
        return -1

    a = 0
    while a < len(terminal.boarding_areas):
        area = terminal.boarding_areas[a]
        if area.type.lower() == "schengen" and is_schengen:
            g = 0
            while g < len(area.gates):
                if not area.gates[g].occupied:
                    area.gates[g].occupied = True
                    area.gates[g].aircraft_id = aircraft.aircraft_id
                    return 0
                g += 1
        elif area.type.lower() != "schengen" and not is_schengen:
            g = 0
            while g < len(area.gates):
                if not area.gates[g].occupied:
                    area.gates[g].occupied = True
                    area.gates[g].aircraft_id = aircraft.aircraft_id
                    return 0
                g += 1
        a += 1

    # Fallback: any free gate
    a = 0
    while a < len(terminal.boarding_areas):
        g = 0
        while g < len(terminal.boarding_areas[a].gates):
            if not terminal.boarding_areas[a].gates[g].occupied:
                terminal.boarding_areas[a].gates[g].occupied = True
                terminal.boarding_areas[a].gates[g].aircraft_id = aircraft.aircraft_id
                return 0
            g += 1
        a += 1
    return -1

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def PlotGateOccupancy(bcn):
    if not bcn:
        return

    num_terminals = len(bcn.terminals)
    fig, axes = plt.subplots(1, num_terminals, figsize=(8 * num_terminals, 12))

    if num_terminals == 1:
        axes = [axes]

    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        ax = axes[t]
        ax.set_title(terminal.name, fontsize=13, fontweight='bold', pad=15)
        ax.axis('off')

        num_areas = len(terminal.boarding_areas)

        # Find max gates in any area to set y scale
        max_gates = 1
        a = 0
        while a < len(terminal.boarding_areas):
            if len(terminal.boarding_areas[a].gates) > max_gates:
                max_gates = len(terminal.boarding_areas[a].gates)
            a += 1

        total_height = max_gates * 1.2 + 3
        ax.set_xlim(0, num_areas * 6 + 2)
        ax.set_ylim(0, total_height)

        # Top horizontal terminal bar
        ax.plot([0.5, num_areas * 6 + 1.5], [total_height - 0.5, total_height - 0.5],
                color='steelblue', linewidth=10, solid_capstyle='butt')

        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            x_center = 1 + a * 6 + 2.5

            num_gates = len(area.gates)

            # Vertical spine
            ax.plot([x_center, x_center], [1.2, total_height - 0.5],
                    color='steelblue', linewidth=6, solid_capstyle='butt')

            # Area label at bottom
            ax.text(x_center, 0.4, area.name, ha='center', fontsize=9,
                    fontweight='bold', color='steelblue')

            if num_gates == 0:
                a += 1
                continue

            gate_spacing = (total_height - 2.5) / max_gates

            g = 0
            while g < num_gates:
                gate = area.gates[g]
                y = 1.5 + g * gate_spacing
                color = 'red' if gate.occupied else 'limegreen'

                rect_w = 2.2
                rect_h = min(gate_spacing * 0.55, 0.9)

                if g % 2 == 0:
                    x_rect = x_center - rect_w - 0.3
                    x_connector_end = x_rect + rect_w
                    x_label = x_rect - 0.1
                    ha = 'right'
                else:
                    x_rect = x_center + 0.3
                    x_connector_end = x_rect
                    x_label = x_rect + rect_w + 0.1
                    ha = 'left'

                rect = mpatches.FancyBboxPatch(
                    (x_rect, y - rect_h / 2), rect_w, rect_h,
                    boxstyle="round,pad=0.05",
                    color=color, zorder=3)
                ax.add_patch(rect)

                # Connector line
                ax.plot([x_center, x_connector_end], [y, y],
                        color='steelblue', linewidth=1.5, zorder=2)

                # Label
                font_size = max(4, min(7, gate_spacing * 3))
                if gate.occupied:
                    label = f"{gate.name}\n{gate.aircraft_id}"
                else:
                    label = gate.name
                ax.text(x_label, y, label, ha=ha, va='center',
                        fontsize=font_size, color='black')

                g += 1
            a += 1
        t += 1

    free_patch = mpatches.Patch(color='limegreen', label='Free')
    occupied_patch = mpatches.Patch(color='red', label='Occupied')
    fig.legend(handles=[free_patch, occupied_patch], loc='lower center',
               ncol=2, fontsize=10, bbox_to_anchor=(0.5, 0.01))

    plt.suptitle(f"Gate Occupancy - {bcn.code}", fontsize=15, fontweight='bold')
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    plt.show()



def GetOccupancyStats(bcn): #devuelve 3 listas, 1 nombres (t1,t2), 2 gates ocupadas en cada terminal, 3 gates libres por cada terminal.
    names =[]
    occupied=[]
    free=[]
    i=0
    while i<len(bcn.terminals):
        b=bcn.terminals[i]
        j=0
        names.append(b.name) #intuyo que se mete ahi el nombre
        occ=0
        fre=0
        while j<len(b.boarding_areas):
            a=b.boarding_areas[j]
            t=0
            while t<len(a.gates): #no se como llevar ahi el tema de las clases por eso pongo a.area.gates!
                gate=a.gates[t]
                if gate.occupied:
                    occ+=1
                else:
                    fre+=1
                t+=1
            j+=1
        occupied.append(occ)
        free.append(fre)
        i+=1
    return names,occupied,free

def PlotOccupancyStats(bcn): #hemos creado 2 plots por separado que iran uno encima del otro
    names, occupied, free = GetOccupancyStats(bcn) #ojo!! hay que desempaquetar esto de esta forma, sin crear objeto externo
    plt.bar(names,occupied,color="red",label="occupied")
    plt.bar(names,free,bottom=occupied,color="green",label="free")#ploteamos con names tambien!
    plt.title("Gate occupancy")
    plt.show()

def GetGatesbyAirline(bcn,airline):

    result=[]
    i=0

    while i<len(bcn.terminals):
        b=bcn.terminals[i]

        j=0
        while j<len(b.boarding_areas):
            a=b.boarding_areas[j]

            t=0                         #PONEMOS LOS APPEND UNICAMENTE SI ENCUENTRA
            while t<len(a.gates):
                gate=a.gates[t]
                print(f"{gate.name} occupied={gate.occupied} aircraft={gate.aircraft_id}")
                if gate.occupied and gate.aircraft_id[:3]==airline: #hacemos eso porqwue la aerolinea es los peimeros 3 digitos VLG

                    print(f"Ocupada: {gate.name} aircraft_id={gate.aircraft_id}")
                    result.append((b.name,a.name,gate.name,gate.aircraft_id)) #COMO ES TUPLA NECESITAMOS METER doble parentesis
                    #result.append(b.name)

                    #result.append(a.name) como lo que quiero es lista de tuplas lo que hagoes unappend #todo junto como arriba
                    #result.append(gate)

                t+=1
            j+=1
        i+=1
    return result

def GetFlightsByHourInGates(bcn,flights):
    IDBUSCADA=[]
    hours=range(24)
    counts=[0]*24
    i=0
    while i<len(bcn.terminals):
        b=bcn.terminals[i]
        j=0
        while j<len(b.boarding_areas):
            a=b.boarding_areas[j]
            t=0
            while t<len(a.gates):
                gate=a.gates[t]
                if gate.occupied:
                    IDBUSCADA.append(gate.aircraft_id)
                t+=1
            j+=1
        i+=1
    i=0
    while i<len(IDBUSCADA):
        j=0
        while j<len(flights):
            if flights[j].aircraft_id==IDBUSCADA[i]:
                hour =int(flights[j].time.split(":")[0])
                counts[hour]+=1
            j+=1
        i+=1
    return counts,hours

def PlotFlightsByHour(bcn,flights):
    count,hours=GetFlightsByHourInGates(bcn,flights)
    plt.bar(hours,count,color="b") #EN VEZ DE HOURS PODRIAS HACER RANGE 24 directamente pero da igual(porque ya lo devuelve la otraf cuncion)
    plt.title("paralo")
    plt.xlabel("Hours")
    plt.ylabel("Counts")
    plt.show()



if __name__ == "__main__":
    bcn = LoadAirportStructure("Terminals.txt")
    if bcn:
        print(f"Loaded: {bcn.code}")
        for t in bcn.terminals:
            print(f"  Terminal {t.name}, airlines: {t.airlines[:5]}")
            for a in t.boarding_areas:
                print(f"    Area {a.name} type={a.type} gates={len(a.gates)}")
    else:
        print("ERROR: Could not load Terminals.txt")

