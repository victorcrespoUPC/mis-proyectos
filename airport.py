#In this file called "airport" we will define the functions and classes that will be used during this phase.
#Firstly, we define the class Airport with the required characteristics:
import os
class airport:
    def __init__(self,code,latitude,longitude):
        self.code=code
        self.latitude=latitude
        self.longitude=longitude
        self.Schengen=False #The characteristic of an Airport to belong to Schengen zone is set to false by default, the airport will be recognised as Schengen if the function SetSchengen is used.

SchengenPrefixes = [
    'LO', #Austria
    'EB', #Belgium
    'LK', #Czech Republic
    'LC', #Cyprus
    'EK', #Denmark
    'EE', #Estonia
    'EF', #Finland
    'LF', #France
    'ED', #Germany
    'LG', #Greece
    'EH', #Netherlands
    'LH', #Hungary
    'BI', #Iceland
    'LI', #Italy
    'EV', #Latvia
    'EY', #Lithuania
    'EL', #Luxembourg
    'LM', #Malta
    'EN', #Norway
    'EP', #Poland
    'LP', #Portugal
    'LZ', #Slovakia
    'LJ', #Slovenia
    'LE', #Spain
    'ES', #Sweeden
    'LS'  #Switzerland
]

def FindAirport(airports, code): #Receives a list of airports and an ICAO code.
    for ap in airports:
        if ap.code == code.upper():
            return ap
    return None

def IsSchengenairport(code):
    if not code:
        return False

    prefix = code[:2].upper()

# We use a while to iterate through the list of prefixes
    i = 0
    found = False
    while i < len(SchengenPrefixes):
        if SchengenPrefixes[i] == prefix:
            found = True
        i = i + 1  # Let's move on to the next item.

    return found

def SetSchengen(airport):
    # This is a direct assignment, no loop needed,
    # but the previous function call already uses the "while"
    airport.Schengen = IsSchengenairport(airport.code)

def Printairport(airport):
    # We simply print the object data
    print(
        f"Code: {airport.code} | Latitude: {airport.latitude} | Longitude: {airport.longitude} | Schengen: {airport.Schengen}")

def _parse_coordinate(coord_str):
    # Let's take the letter (N, S, E, W)
    direction = coord_str[0]

    # To extract the numbers (deg, min, sec) without using complex cuts,
    # we can use a while to store characters:

    # 1. We take the degrees (from character 1 until before the last 4)
    deg_str = ""
    i = 1
    limit_deg = len(coord_str) - 4
    while i < limit_deg:
        deg_str = deg_str + coord_str[i]
        i = i + 1
    deg = float(deg_str)

    # 2. Let's take the minutes (the next two)
    min_str = ""
    limit_min = len(coord_str) - 2
    while i < limit_min:
        min_str = min_str + coord_str[i]
        i = i + 1
    min = float(min_str)

    # 3. Let's take the seconds (the last two)
    sec_str = ""
    while i < len(coord_str):
        sec_str = sec_str + coord_str[i]
        i = i + 1
    sec = float(sec_str)

    # Note: The formula to return the final value would be missing here,
    # but we put the "while" to separate the numbers from the text.

    decimal = deg + (min/60) + (sec/3600)

    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


def _to_dms_string(decimal, is_lat): #This function is needed in order to keep SavaSchengenAirports working as stablished before.
    if is_lat:
        dir_char = 'N' if decimal >= 0 else 'S'
    else:
        dir_char = 'E' if decimal >= 0 else 'W'

    abs_val = abs(decimal)
    deg = int(abs_val)
    m = int((abs_val - deg) * 60)
    s = int(round((abs_val - deg - m / 60) * 3600))

    deg_str = f"{deg:02d}" if is_lat else f"{deg:03d}"
    return f"{dir_char}{deg_str}{m:02d}{s:02d}"

def LoadAirports(filename):
    if not os.path.exists(filename):
        return []

    airports_list = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        if not lines:
            return []

        for line in lines[1:]:
            parts = line.split()
            if len(parts) == 3:
                code = parts[0]
                latitude = _parse_coordinate(parts[1])
                longitude = _parse_coordinate(parts[2])

                new_airport = airport(code, latitude, longitude)
                airports_list.append(new_airport)
    return airports_list


def SaveSchengenAirports(airports, filename):
    schengen_list = [a for a in airports if a.Schengen]

    if not schengen_list:
        return -1

    with open(filename, 'w') as f:
        f.write("CODE LAT LON\n")
        for a in schengen_list:

            latitude_str = _to_dms_string(a.latitude, is_latitude=True)
            longitude_str = _to_dms_string(a.longitude, is_latitude=False) #EHHHHHH
            f.write(f"{a.code} {latitude_str} {longitude_str}\n")
    return 0


def AddAirport(airports, new_airport):
    for a in airports:
        if a.code == new_airport.code:
            print(f"Error: The airport {new_airport.code} already exists.")
            return
    airports.append(new_airport)


def RemoveAirport(airports, code):
    for i, a in enumerate(airports):
        if a.code == code:
            airports.pop(i)
            return 0
    return -1


import matplotlib.pyplot as plt


def PlotAirports(airports): #This will show a plot wich fratures Schengen and non Schengen airports.

    if len(airports) == 0:
        print("Error: no airports were loaded.")
        return

    schengen = 0
    no_schengen = 0

    for ap in airports:
        if ap.Schengen:
            schengen += 1
        else:
            no_schengen += 1

    plt.bar(["Airports"], [schengen], label="Schengen", color="blue") #We will be using blue for Schengen airports and red with non Schengen airports.
    plt.bar(["Airports"], [no_schengen], bottom=[schengen], label="No Schengen", color="red", alpha=0.7)

    plt.title("Schengen airports")
    plt.ylabel("Count")
    plt.legend()
    plt.show()


def MapAirports(airports): #Here we create the kml files that will show the airports in Google Earth.


    if len(airports) == 0:
        print("Error: no airports were loaded.")
        return

    kml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml_content += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml_content += '<Document>\n'

    #Schengen Airports will be represented as green.
    kml_content += '''<Style id="schengen">
        <IconStyle>
            <color>ff00ff00</color>
        </IconStyle>
    </Style>\n'''

    #NONSchengen Airports will be represented as red.
    kml_content += '''<Style id="noschengen">
        <IconStyle>
            <color>ff0000ff</color>
        </IconStyle>
    </Style>\n'''

    for ap in airports:
        style = "schengen" if ap.Schengen else "noschengen"
        kml_content += f'<Placemark>\n'
        kml_content += f'  <name>{ap.code}</name>\n'
        kml_content += f'  <styleUrl>#{style}</styleUrl>\n'
        kml_content += f'  <Point>\n'
        kml_content += f'    <coordinates>{ap.longitude},{ap.latitude},0</coordinates>\n'
        kml_content += f'  </Point>\n'
        kml_content += f'</Placemark>\n'


    kml_content += '</Document>\n'
    kml_content += '</kml>\n'

    with open("airports.kml", "w") as f:
        f.write(kml_content)

    print("You can see the airport by clicking in the generated kml file.")
