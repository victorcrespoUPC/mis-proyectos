

from airport import *


airport = airport("LEBL",41.296445,2.08322941)
SetSchengen(airport)
Printairport(airport)

from airport import *

airport = airport("LELL",41.5209,2.10508)
SetSchengen(airport)
Printairport(airport)

from airport import *
airport = airport("LERS",41.1475, 1.1684)
SetSchengen(airport)
Printairport(airport)

from airport import *

airport = airport("OACL",33.9416, -118.4085)
SetSchengen(airport)
Printairport(airport)

#Now we will continue by testing step 3 functions:

from airport import *
airports=LoadAirports("Airports.txt") #Here we test the loaded airports by using the length of its vector (testing LoadAirports),
print(f"Airports loaded: {len(airports)}")

from airport import *
for ap in airports: #Here we test the SetSchengen function,
    SetSchengen(ap)

from airport import *
for ap in airports[:5]:
    Printairport(ap) #This will show the fist five airports.

from airport import * #Here we will test if new airports can be added.
newap = airport("LEBL", 41.297445, 2.0832941)
SetSchengen(newap)
AddAirport(airports, newap)
print(f"After adding LEBL: {len(airports)} airports in total")

from airport import *
AddAirport(airports, newap)
print(f"Duplicating LEBL:{len(airports)} airports remains equal") #If we try to add one that has already been added into the list, it cannot be duplicated adn therefore the number of airports added must remain equal.

from airport import *
RemoveAirport(airports,"LEBL")
print(f"After eliminating LEBL: {len(airports)} airports in total")

from airport import *
result = RemoveAirport(airports, "XXXX")
print(f"Eliminating a non exixtent airport: {result} ") #This must result in a ERROR message.

from airport import *
SaveSchengenAirports(airports, "Schengen_airports.txt")
print("File Schengen_airports.txt saved")

from airport import *
schengen = LoadAirports("Schengen_airports.txt") #Here we test if Schengen airports were saved correctly.
print(f"Schengen Airports saved: {len(schengen)}")


#Now we will test step 5:

PlotAirports(airports) #Here we test PlotAirports

MapAirports(airports) #Here we test MapAirports
                      #End result is correct for now, as we recieve that no airports were loaded, and also no errors occur!
