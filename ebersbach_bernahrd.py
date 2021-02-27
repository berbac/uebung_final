import calendar
import pandas as pd
import numpy as np

# Dummy
carrier = "9E"
in_date = "13.1.2019"
day, month, year = in_date.split(".")
# Einlesen der Datei
data = pd.read_csv("fluege_2019-01-01_2019-01-15.tsv", sep="\t")

# Berechnung der Gesamtflugstrecke einer Gesellschaft
dist_sum = sum(data.loc[data["OP_UNIQUE_CARRIER"] == carrier, "DISTANCE"])

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
    query("OP_UNIQUE_CARRIER=='{}'".format(carrier))

data["DELAY_CALC"] = data_delay_sub["ARR_TIME"] - data_delay_sub["CRS_ARR_TIME"]
data["DELAY_CALC"] = data.loc[data["DELAY_CALC"] > 0, "DELAY_CALC"]
delay = data["DELAY_CALC"].mean()