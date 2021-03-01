import pandas as pd
import argparse

parser = argparse.ArgumentParser()

# Definition der Commandozeilenoptionen und Parameter + Hilfe
parser.add_argument("-c", "--choice", dest="choice", default="none",
                    choices=["distance", "delay", "both"],
                    help=">distance<: Berechnung der Gesamtflugstrecke einer Fluggesellschaft >delay<: Berechnung der "
                         "durchschnittlichen Verspätung einer FLuggesellschaft an einem Tag >both<: beides")
parser.add_argument("carrier", type=str, help="Zweistelliger Code der Fluggesellschaft")
parser.add_argument("date", type=str, default="00.00.00", help="Datum in der Form TT.MM.JJJJ", const=1, nargs='?')
parser.add_argument("-s", "--save", action="store_true", help="Ergebnisse werden in Textdatei geschrieben")
args = parser.parse_args()

# Check, ob der angegebene Fluggesellschaftscode zweistellig ist
if len(args.carrier) != 2:
    print("\nERROR. Bitte einen gültigen zweistelligen IATA-Airline-Code angeben."
          "\n**** Programm wird beendet. **** \n")
    quit()

# Check, ob ein Datum angegeben wurde und ob es überhaupt gebraucht wird
if args.date == "00.00.00" and (args.choice == "delay" or args.choice == "both"):
    print("\nERROR: Kein Datum angegeben. Für diese Auswahl wird eine Datumsangabe benötigt."
          "\n**** Programm wird beendet. ****\n")
    quit()

# Datum zerlegen und Nullen entfernen
try:
    day, month, year = args.date.split(".")
    day = day.lstrip('0')  # nur voranstehende Nullen werden entfernt
    month = month.lstrip('0')
except ValueError:
    print("\nERROR. Datum konnte nicht erkannt werden. Bitte im Format TT.MM.JJJJ angeben."
          "\n**** Programm wird beendet ****\n")
    quit()

# Angegebenes Datum innerhalb des Zeitfensters (wenn benötig)?
if args.choice != "distance" and (int(year) != 2019 or int(month) != 1 or int(day) < 1 or int(day) > 15):
    print("\nERROR: Der angegebene Tag befindet sich außerhalb des Beobachtungszeitraums oder wurde falsch geschrieben."
          "\nBitte ein Datum im Zeitraum 1.1.2019 - 15.1.2019 angeben.\nProgramm wird beendet.\n")
    quit()

# Einlesen der Daten
data = pd.read_csv("fluege_2019-01-01_2019-01-15.tsv", sep="\t")

# Abfrage, ob Airline in Daten enthalten
if args.carrier not in list(data["OP_UNIQUE_CARRIER"]):
    print("\nERROR. Angegebener IATA-Airline-Code nicht im Datensatz vorhanden."
          "\n**** Programm wird beendet. ****\n")
    quit()

# hier wird versucht, eine Datei mit den Klarnamen der Fluggesellschaften einzulesen, um diese am Schluss anzuzeigen
try:
    airlines = pd.read_csv("airlines.csv")
    carrier_name = airlines.loc[airlines["Code"] == args.carrier, "Description"].to_string(index=False)
except FileNotFoundError:
    print("\nDatei 'airlines.csv' nicht gefunden - Klarnamen der Fluggesellschaften können nicht angegeben werden.")
    carrier_name = args.carrier

# Abfrage für den Dateinamen der Exportdatei
if args.save:
    filename = open(input("\nBitte Dateinamen angeben:\n")+".txt", "w")
    filename.write("Fluggesellschaft:\t\t {carrier}\n".format(carrier=carrier_name))

# Berechnung der Gesamtflugstrecke einer Gesellschaft, wenn ausgewählt
if args.choice == "distance" or args.choice == "both":
    dist_sum = sum(data.loc[data["OP_UNIQUE_CARRIER"] == args.carrier, "DISTANCE"])
    print("\nDie von der Fluggesellschaft {carrier} insgesamt geflogene Strecke beträgt {miles} Meilen - "
          "das entspricht {km} Kilometern.".format(carrier=carrier_name, miles=dist_sum, km=round(dist_sum/1.609, 1)))
    if args.save:
        filename.write("Insgesamt geflogen:\t\t {miles} Meilen (ca. {km} km)\n".
                       format(miles=dist_sum, km=round(dist_sum / 1.609, 1)))

# Berechnung der Verspätung
if args.choice == "both" or args.choice == "delay":

    data_delay_sub = data.query("YEAR=={}".format(year)). \
        query("MONTH=={}".format(month)). \
        query("DAY_OF_MONTH=={}".format(day)). \
        query("OP_UNIQUE_CARRIER=='{}'".format(args.carrier))

    data["DELAY_CALC"] = data_delay_sub["ARR_TIME"] - data_delay_sub["CRS_ARR_TIME"]
    data["DELAY_CALC"] = data.loc[data["DELAY_CALC"] > 0, "DELAY_CALC"]
    delay = data["DELAY_CALC"].mean()

    if delay > 0:
        print("\nDie Fluggesellschaft {carrier} hatte am {date} eine durchschnittliche Verspätung von {delay_min} Minuten, "
              "also etwa {delay_hr} Stunden!\n".format(carrier=carrier_name, date=args.date, delay_min=round(delay, 1),
                                                       delay_hr=round(delay/60, 1)))
    else:
        print("\nDie Fluggesellschaft {carrier} hatte am {date} keinerlei Verspätungen. Alles lief glatt.\n".
              format(carrier=carrier_name, date=args.date, delay_min=round(delay, 1), delay_hr=round(delay / 60, 1)))
    if args.save:
        filename.write("Mittlere Verspätung am {date}:\t {delay_min} Min. (ca. {delay_hr} Std.)".
                       format(date=args.date, delay_min=round(delay, 1), delay_hr=round(delay / 60, 1)))
if args.save:
    filename.close()
    print("Die Ergebnisse wurden in die Datei {} geschrieben.\n".format(filename.name))
