import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from airport import *
from aircraft import *
from LEBL import *

# Load all airports from file (for searching coordinates)
all_airports = LoadAirports("Airports.txt")
i = 0
while i < len(all_airports):
    ap = all_airports[i]
    SetSchengen(ap)

    i = i + 1

# This is the list shown in the interface (starts empty)
airports = []


def load_airports():
    global airports
    filename = filedialog.askopenfilename(
        title="Select filed airports",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        airports = LoadAirports(filename)
        i = 0
        while i < len(airports):
            ap = airports[i]
            SetSchengen(ap)
            i = i + 1
        update_listbox()
        messagebox.showinfo("Correct", f"You loaded {len(airports)} airports.")

def add_airport():
    code = entry_code.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Introduce an ICAO code.")
        return

    # Search in the full database
    found = FindAirport(all_airports, code)
    if found is None:
        messagebox.showerror("Error", f"Airport {code} not found in database.")
        return

    # Add to the visible list
    SetSchengen(found)
    AddAirport(airports, found)
    update_listbox()
    entry_code.delete(0, tk.END)


def remove_airport():
    code = entry_code.get().strip().upper()
    if not code:
        messagebox.showerror("Error", "Enter the ICAO code of the airport you want to eliminate.")
        return
    result = RemoveAirport(airports, code)
    if result == -1: #Reason why we needed -1 in prior result!
        messagebox.showerror("Error", f"The airport {code} isn't registered.")
    else:
        messagebox.showinfo("Success", f"Airport {code} was eliminated.")
        update_listbox()
    entry_code.delete(0, tk.END)

def save_schengen():
    if not airports:
        messagebox.showerror("Error", "No airports were loaded.")
        return
    filename = filedialog.asksaveasfilename(
        title="Save Schengen airports",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        result = SaveSchengenAirports(airports, filename)
        if result == -1:
            messagebox.showerror("Error", "No Schengen airports found to save.")
        else:
            messagebox.showinfo("Success", "Schengen airports saved successfully.")

def show_plot():
    if not airports:
        messagebox.showerror("Error", "No airports were loaded!")
        return
    PlotAirports(airports)

def show_map():
    if not airports:
        messagebox.showerror("Error", "There are no loaded airports.")
        return
    MapAirports(airports)
    messagebox.showinfo("KML created", "File airports.kml was generated.\n Use Google Earth to open it.")

def update_listbox():
    listbox.delete(0, tk.END)
    i = 0
    while i < len(airports):
        ap = airports[i]

        if ap.Schengen == True:
            schengen_str = "✔ Schengen"
        else:
            schengen_str = "✘ Not a Schengen airport"

        #This will create the textline adding the necessary parts.
        #We will be aproximating the distance values to 4 decimals (by using round).
        linia = str(ap.code) + " | Latitude: " + str(round(ap.latitude, 4)) + \
                " | Longitude: " + str(round(ap.longitude, 4)) + " | " + schengen_str

        #And it is added to the listbox
        listbox.insert(tk.END, linia) #Tkinter special item

        i = i + 1

flights = [] #LISTA CON LOS ATRIBUTOS DE TIME y ID flight.time, flight.aircraft_id

def load_arrivals_ui():
    global flights
    filename = filedialog.askopenfilename(title="Select Arrivals file", filetypes=[("Text files", "*.txt")])
    if filename:
        flights = LoadArrivals(filename)
        messagebox.showinfo("Success", f"Loaded {len(flights)} flights.")

def save_flights_ui():
    filename = filedialog.asksaveasfilename(title="Save Flights", filetypes=[("Text files", "*.txt")])
    if filename:
        SaveFlights(flights, filename)

def map_flights_ui(long_only=False):
    MapFlights(flights, only_long=long_only)
    messagebox.showinfo("KML", "flights.kml generated!")

def clear_arrivals():  #We will use this to reload new flights, being able to eliminate the ones we don't want to study anymore
    global arrivals
    arrivals = []
    messagebox.showinfo("Success", "All arrivals cleared.")

def reload_arrivals_ui():
    global arrivals
    filename = filedialog.askopenfilename(
        title="Select New Arrivals File",
        filetypes=[("Text files", "*.txt")]
    )
    if filename:
        arrivals = LoadArrivals(filename)
        if len(arrivals) > 0:
            messagebox.showinfo("Success", f"Loaded {len(arrivals)} new flights.")
        else:
            messagebox.showerror("Error", "No valid flights found in file.")

bcn_airport = None
flights=[]

def load_lebl_structure():
    global bcn_airport
    filename = "Terminals.txt"
    bcn_airport = LoadAirportStructure(filename)
    if bcn_airport:
        messagebox.showinfo("LEBL", "LEBL airport structure loaded correctly.")
    else:
        messagebox.showerror("Error", "Could not find or load Terminals.txt.")


def assign_gates_to_flights():
    global bcn_airport
    if not bcn_airport:
        messagebox.showerror("Error", "First load the LEBL structure.")
        return
    if not flights:
        messagebox.showerror("Error", "No flights loaded.")
        return

    import datetime
    now = datetime.datetime.now()
    current_minutes = now.hour * 60 + now.minute

    # Reset all gates
    for terminal in bcn_airport.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupied = False
                gate.aircraft_id = None

    assigned_count = 0
    for flight in flights:
        try:
            h, m = flight.time.split(':')
            flight_minutes = int(h) * 60 + int(m)
        except:
            continue

        # Only flights that arrived in the last 90 minutes AND haven't left yet
        if current_minutes - 90 <= flight_minutes <= current_minutes:
            origin_ap = FindAirport(all_airports, flight.origin)
            is_schengen = origin_ap.Schengen if origin_ap else False
            if AssignGate(bcn_airport, flight, is_schengen) == 0:
                assigned_count += 1
    total_gates = 0
    free_gates = 0
    for terminal in bcn_airport.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                total_gates += 1
                if not gate.occupied:
                    free_gates += 1

    messagebox.showinfo("Assignment",
                        f"Active flights at {now.strftime('%H:%M')}: {assigned_count}\n"
                        f"Occupied gates: {total_gates - free_gates}\n"
                        f"Free gates: {free_gates}\n"
                        f"Total gates: {total_gates}")
    print(f"Flights: {len(flights)}, assigned: {assigned_count}")

def show_occupancy_ui():
    if not bcn_airport:
        return

    # Let's create a new window to show the status
    top = tk.Toplevel(root)
    top.title("Door Status - LEBL")
    txt = scrolledtext.ScrolledText(top, width=60, height=20)
    txt.pack()

    occupancy = GateOccupancy(bcn_airport)
    txt.insert(tk.END, f"{'DOOR':<15} | {'STATE':<10} | {'AIRCRAFT':<10}\n")
    txt.insert(tk.END, "-" * 40 + "\n")

    for entry in occupancy:
        gate = entry["gate_name"]
        status = entry["status"]
        ac_id = entry["aircraft_id"]
        line = f"{gate:<15} | {status:<10} | {str(ac_id):<10}\n"
        txt.insert(tk.END, line)

    PlotGateOccupancy(bcn_airport)

#def show_plot_occupancy_states_ui():
  #  if not bcn_airport:
     #   return
  #  top=tk.Toplevel(root)
  #  top.title("--Occupancy States--")
    #txt=scrolledtext.ScrolledText(top,width=60,height=20) #no lo necesita porque solo muestra plot, no textg
   # txt.pack()
    #occupstate=GetOccupancyStats(bcn_airport) #la variable se llama asi SE CAMBIA!!!!!!!!
#ES ASI:
def show_plot_occupancy_ui():
    if not bcn_airport:
        messagebox.showerror("ERROR","Load LEBL structure first!")
        return
    PlotOccupancyStats(bcn_airport)


def show_Get_Gates_By_Airline_ui():


    if not bcn_airport:
        messagebox.showerror("ERROR","Load LEBL structure first!")
        return
    airline=entry_airline.get().strip().upper()
    if not airline:
        messagebox.showerror("Error","Airline or callsign not found")
        return
    result = GetGatesbyAirline(bcn_airport,airline)
    if len(result)==0:
        messagebox.showerror("Sorry!","Did not find anything")
        return
    else:

        #airline,gate=result #HAY QUE DESEMPAQUETAR CON WHILE recibo tuplas en el orden del vector result: aerolinea terminal area gate
        i=0
        while i<len(result):
            terminal,area,gate_name,aircraft_id=result[i]
            txt.insert(tk.END,f"{gate_name} {aircraft_id}\n")
            i+=1

def show_plot_hours():
    if not bcn_airport:
        messagebox.showerror("Load it pal!")
        return
    PlotFlightsByHour(bcn_airport,flights)






#Main display:
root = tk.Tk()
root.title("Airport Management")
root.geometry("1000x800") #Interface modified to display al options

#Character customization:
tk.Label(root, text=" Airport Management", font=("Arial", 16, "bold")).pack(pady=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)
#Interface will display the following items:
tk.Button(frame_buttons, text="Load airports ✈️", width=20, command=load_airports).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_buttons, text="Save Schengen 🛂 ", width=20, command=save_schengen).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_buttons, text="See comparison graph 📊", width=20, command=show_plot).grid(row=0, column=2, padx=5, pady=5)
tk.Button(frame_buttons, text="View in Google Earth 🌍", width=20, command=show_map).grid(row=0, column=3, padx=5, pady=5)

#Interface customization code:
frame_add = tk.LabelFrame(root, text="Add / Eliminate airports", padx=10, pady=10)
frame_add.pack(pady=10, fill="x", padx=20)

tk.Label(frame_add, text="ICAO code:").grid(row=0, column=0, sticky="w")
entry_code = tk.Entry(frame_add, width=10)
entry_code.grid(row=0, column=1, padx=5)

#LINES WERE ELIMINATED

tk.Button(frame_add, text="Add", width=10, command=add_airport).grid(row=0, column=2, padx=5)
tk.Button(frame_add, text="Eliminate", width=10, command=remove_airport).grid(row=0, column=3, padx=5)

#Airport list:
tk.Label(root, text="Loaded Airports:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
listbox = tk.Listbox(root, width=100, height=5, font=("Courier", 9)) #Space of loaded airports MAXIMIZED FOR COMFORT
listbox.pack(padx=20, pady=5, fill="both", expand=True)

#We create the version 2 interface, which will be displayed under the old one:

#The new frame:
frame_v2 = tk.LabelFrame(root, text="VERSION 2: ARRIVALS ✈ ️", padx=10, pady=10)
frame_v2.pack(pady=10, fill="x", padx=20)

tk.Button(frame_v2, text="Load Arrivals", width=15, command=load_arrivals_ui).grid(row=0, column=0, padx=5)
tk.Button(frame_v2, text="Plot Hours", width=15, command=lambda: PlotArrivals(flights)).grid(row=0, column=1, padx=5)
tk.Button(frame_v2, text="Plot Airlines", width=15, command=lambda: PlotAirlines(flights)).grid(row=0, column=2, padx=5)
tk.Button(frame_v2, text="Plot Schengen", width=15, command=lambda: PlotFlightsType(flights)).grid(row=0, column=3, padx=5)

tk.Button(frame_v2, text="Save Flights", width=15, command=save_flights_ui).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_v2, text="Map All Flights", width=15, command=lambda: map_flights_ui(False)).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame_v2, text="Map Long Dist", width=15, command=lambda: map_flights_ui(True)).grid(row=1, column=2, padx=5, pady=5)

tk.Button(frame_v2, text="Clear All Arrivals", width=15, command=clear_arrivals,bg='red').grid(row=2, column=0, padx=5, pady=5)
tk.Button(frame_v2, text="Reload Arrivals", width=15, command=reload_arrivals_ui,bg='green').grid(row=2, column=1, padx=5, pady=5)

# We create the version 3 interface, which will be displayed under the old ones:

frame_v3 = tk.LabelFrame(root, text="VERSION 3: GATE MANAGEMENT 🏢", padx=10, pady=10, fg="black")
frame_v3.pack(pady=10, fill="x", padx=20)

tk.Button(frame_v3, text="Data structure LEBL", width=25,
          command=load_lebl_structure).grid(row=0, column=0, padx=5)

tk.Button(frame_v3, text="Assign gates", width=25,
          command=assign_gates_to_flights).grid(row=0, column=1, padx=5)

tk.Button(frame_v3, text="Show gate occupancy", width=25,
          command=show_occupancy_ui).grid(row=0, column=2, padx=5)
tk.Button(frame_v3, text ="show plot", width= 25,
          command= show_plot_occupancy_ui).grid(row=0,column=3,padx=5)

tk.Button(frame_v3, text="Gates occupied by airline").grid(row=0,column=7,sticky="w")
entry_airline=tk.Entry(frame_v3,width=15)
entry_airline.grid(row=1,column=0,padx=5)   #SEPARAMOS EN 2 PORQUE SI NO FALLA
tk.Button(frame_v3,text="Find the gates now",
          command=show_Get_Gates_By_Airline_ui).grid(row=0,column=6)

tk.Button(frame_v3,text="Show plotty", width=15,
          command=show_plot_hours).grid(row=2, column=0,padx=5)

root.mainloop()


