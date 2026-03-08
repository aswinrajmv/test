#
#this program collects values from the instruments and creates a CSV file with Pass/Fail status, calculate statistics, and generates a test report
#

import pyvisa
import time
import csv
import datetime
import statistics

rm = pyvisa.ResourceManager()

from insts import instruments  # globals for VISA resource strings
from insts import mp710259
from insts import hmc8043

# Connect intruments
power_supply = rm.open_resource(instruments.ps_id) 
electronic_load = rm.open_resource(instruments.load_id)
multimeter = rm.open_resource(instruments.dmm_id)
oscilloscope = rm.open_resource(instruments.scope_id)

# Setup Instruments
hmc8043.setup(power_supply, 5.0, 2.0, True)
mp710259.setup(electronic_load, True)

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
    
    input_meas = hmc8043.get_meas(power_supply)
    output_meas = mp710259.get_meas(electronic_load)

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