import pandas as pd
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--choice", dest="choice", default="none",
                    choices=["distance", "delay", "both"],
                    help=">distance<: Berechnung der Gesamtflugstrecke einer Fluggesellschaft >delay<: Berechnung der "
                         "durchschnittlichen Verspätung einer FLuggesellschaft an einem Tag\n")
parser.add_argument("carrier", type=str, help="Name der Fluggesellschaft")
parser.add_argument("date", type=str, default="00.00.00", help="Datum in der Form TT.MM.JJJ", const=1, nargs='?')
args = parser.parse_args()

# TODO: date-format-check

# Check, ob ein Datum angegeben wurde und ob es überhaupt gebraucht wird
if args.date == "00.00.00" and (args.choice == "delay" or args.choice == "both"):
    print("Kein Datum angegeben. Für diese Auswahl wird eine Datumsangabe Benötigt.\nProgramm wird beendet.")
    quit()
day, month, year = args.date.split(".")

# Einlesen der Dateien
data = pd.read_csv("fluege_2019-01-01_2019-01-15.tsv", sep="\t")

# hier wird versucht, eine Datei mit den Klarnamen der Fluggesellschaften einzulesen, um diese am Schluss anzuzeigen
try:
    airlines = pd.read_csv("airlines.csv")
    carrier_name = airlines.loc[airlines["Code"] == args.carrier, "Description"].to_string(index=False)
except FileNotFoundError:
    print("\nDatei 'airlines.csv' nicht gefunden - Klarnamen der Fluggesellschaften können nicht angegeben werden.")
    carrier_name = args.carrier

# Berechnung der Gesamtflugstrecke einer Gesellschaft, wenn ausgewählt
if args.choice == "distance" or args.choice == "both":
    dist_sum = sum(data.loc[data["OP_UNIQUE_CARRIER"] == args.carrier, "DISTANCE"])
    print("\nDie von der Fluggesellschaft {carrier} insgesamt geflogene Strecke beträgt {miles} Meilen - "
          "das entspricht {km} Kilometern.".format(carrier=carrier_name, miles=dist_sum, km=round(dist_sum/1.609, 1)))

# Berechnung der Verspätung
if args.choice == "both" or args.choice == "delay":

# Durchschn. Verspätung an einem best. Tag
# Hier durch die angegebenen Versöätungsgründe berechnet
# data["ALL_DELAYS"] = data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "CARRIER_DELAY"] + \
#                      data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "WEATHER_DELAY"] + \
#                      data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "NAS_DELAY"] + \
#                      data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "SECURITY_DELAY"] + \
#                      data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "LATE_AIRCRAFT_DELAY"]
#
# # hier nach der Differenz aus Vorgegebner und tatsächlicher Ankunftszeit
# data["NEW_DELAYS"] = data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "ARR_TIME"] - \
#                      data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "CRS_ARR_TIME"]
# data["DELAYS!"] = data.loc[data["NEW_DELAYS"] > 0, "NEW_DELAYS"]
# Funfact: Die Mittelwerte sind unterschiedlich --> die "_DELAY"-Angaben sind also unvollständig
# delay_mean = data["DELAYS!"].mean()

    data_delay_sub = data.query("YEAR=={}".format(year)). \
        query("MONTH=={}".format(month)). \
        query("DAY_OF_MONTH=={}".format(day)). \
        query("OP_UNIQUE_CARRIER=='{}'".format(args.carrier))

    data["DELAY_CALC"] = data_delay_sub["ARR_TIME"] - data_delay_sub["CRS_ARR_TIME"]
    data["DELAY_CALC"] = data.loc[data["DELAY_CALC"] > 0, "DELAY_CALC"]
    delay = data["DELAY_CALC"].mean()

# TODO: Abspeichern in Textdatei: Name wäählbar.
    print("\nDie Fluggesellschaft {carrier} hatte am {date} eine akkumulierte Verspätung von {delay_min} Minuten, "
          "also etwa {delay_hr} Stunden!\n".format(carrier=carrier_name, date=args.date, delay_min=round(delay, 1),
                                                   delay_hr=round(delay/60, 1)))
