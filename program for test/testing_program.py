import pyvisa
import time
import csv
import datetime
import statistics
import signal  
import sys     
import os      

rm = pyvisa.ResourceManager()

from insts import instruments  # globals for VISA resource strings
from insts import mp710259
from insts import hmc8043

in_measures = hmc8043.get_meas(ps)
out_measures = mp710259.get_meas(load)

# Test parameters from the test
rails = {
    "3V6": {"voltage":3.6, "max_current":2.5},
    "1V8": {"voltage":1.8, "max_current":3},
    "3V3": {"voltage":3.3, "max_current":3},
    "2V5": {"voltage":2.5, "max_current":1.5}
}

# Open CSV file
csv_file = open("test_results.csv","w",newline="")
writer = csv.writer(csv_file)

writer.writerow([
"Time",
"Rail",
"Measured Voltage",
"Min Limit",
"Max Limit",
"Result"
])

print("Starting Load Transient Test")

results = []

for rail in rails:

    voltage = rails[rail]["voltage"]
    max_current = rails[rail]["max_current"]

    print("Testing rail:", rail)

    # Set power supply voltage
    power_supply.write("VOLT " + str(voltage))
    power_supply.write("OUTP ON")

    # Low load
    electronic_load.write("CURR 0.1")
    time.sleep(1)

    # High load
    electronic_load.write("CURR " + str(max_current))
    time.sleep(0.2)

    # low load
    electronic_load.write("CURR 0.1")
    time.sleep(1)

    # Measure voltage using multimeter
    measured_voltage = float(multimeter.query("MEAS:VOLT?"))

    # Calculate limits (±5%)
    tolerance = voltage * 0.05
    min_limit = voltage - tolerance
    max_limit = voltage + tolerance

    # Pass or Fail check
    if measured_voltage >= min_limit and measured_voltage <= max_limit:
        result = "PASS"
    else:
        result = "FAIL"

    timestamp = datetime.datetime.now()

    # Save the waveform
    waveform = oscilloscope.query(":WAV:DATA?")
    file_name = "waveform_" + rail + "_" + str(int(time.time())) + ".txt"

    f = open(file_name,"w")
    f.write(waveform)
    f.close()

    # Write to CSV
    writer.writerow([
        timestamp,
        rail,
        measured_voltage,
        min_limit,
        max_limit,
        result
    ])

    results.append(measured_voltage)

    print("Voltage:", measured_voltage, "Result:", result)

# Stats
mean_voltage = statistics.mean(results)
max_voltage = max(results)
min_voltage = min(results)

print("\nTest Statistics")
print("Mean Voltage:", mean_voltage)
print("Max Voltage:", max_voltage)
print("Min Voltage:", min_voltage)

# Save the report
report = open("test_report.txt","w")

report.write("Load Transient Test Report\n")
report.write("--------------------------\n")
report.write("Mean Voltage: " + str(mean_voltage) + "\n")
report.write("Max Voltage: " + str(max_voltage) + "\n")
report.write("Min Voltage: " + str(min_voltage) + "\n")

report.close()

csv_file.close()

print("Test Finished")