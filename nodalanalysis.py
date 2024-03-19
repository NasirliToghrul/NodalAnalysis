#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 20:55:40 2022

@author: Toghrul Nasirli
"""

import numpy as np
import matplotlib.pyplot as plt
import pvtprops as pvt
from shapely.geometry import LineString

# Input Parameters: Modify these values as required
measured_depth = 5100  # Measured depth of the well (ft)
sg_gas = 0.79  # Specific gravity of gas
tubing_ID = 1.61  # Inner diameter of tubing (in)
roughness = 0.00062  # Tubing roughness (in)
wellhead_pressure = 900  # Wellhead pressure (psi)
wellhead_temperature = 110  # Wellhead temperature (°F)
reservoir_pressure = 1952  # Reservoir pressure (psi)
reservoir_temperature = 180  # Reservoir temperature (°F)
c = 0.01936  # Flow coefficient
n = 0.8608  # Flow exponent
carbon_dioxide = 0.05  # CO2 mole fraction
nitrogen = 0.06  # N2 mole fraction
hydrogen_sulfur = 0.04  # H2S mole fraction
angle = 0  # Angle of inclination of the well (degrees)

# Standing Correlation Parameters Calculation
Tpc = 168 + 325 * sg_gas - 12.5 * (sg_gas ** 2)  # Pseudocritical temperature (°R)
Ppc = 677 + 15 * 0.647 - 37.5 * (sg_gas ** 2)  # Pseudocritical pressure (psia)

flow_rate = []
method = "CarrKobayashi"  # Method for calculating z-factor and viscosity
bottomhole_p = []  # List to store bottomhole pressures
IPR = []  # List to store Inflow Performance Relationship values
q = 0  # Initial flow rate (Mscf/d)

# Iterating through flow rates
for i in range(10000):
    flow_rate.append(q)

    # Calculation of average pressure and temperature
    average_pressure = (wellhead_pressure + reservoir_pressure) / 2
    average_temperature = (wellhead_temperature + reservoir_temperature) / 2 + 460  # Converting to Rankine

    # Calculation of z-factor and viscosity
    z_factor = pvt.redlich_kwong_eos(average_pressure, average_temperature, sg_gas, carbon_dioxide, hydrogen_sulfur,
                                     method, nitrogen)
    u = pvt.lee_gonzales_eakin(average_pressure, average_temperature, sg_gas, carbon_dioxide, hydrogen_sulfur, method,
                               nitrogen)

    # Calculation of dimensionless length
    s = 0.0375 * sg_gas * measured_depth * np.cos(angle / 57.3) / (z_factor * average_temperature)
    reynolds = 20.1 * q * sg_gas / (tubing_ID * u)

    # Calculation of friction factor
    if reynolds == 0:
        f = 0  # Assigning a default value
    else:
        f = (1 / (1.14 - 2 * np.log10(roughness + 21.25 / reynolds ** 0.9))) ** 2

    # Calculation of bottomhole pressure
    bottomhole_pressure = np.sqrt((np.exp(s) * wellhead_pressure ** 2) + (
        (25 * sg_gas * z_factor * average_temperature * f * measured_depth * q ** 2 * (np.exp(s) - 1))) / (
                                          tubing_ID ** 5 * s * 10 ** 6))
    bottomhole_p.append(bottomhole_pressure)

    # Calculation of Inflow Performance Relationship (IPR)
    ipr = np.sqrt(reservoir_pressure ** 2 - (q / c) ** (1 / n))
    IPR.append(ipr)

    # Incrementing flow rate
    q = q + 10

    # Break condition when IPR becomes negative
    if ipr > 0:
        continue
    else:
        break

# Plotting IPR and TPR curves
plt.plot(flow_rate, bottomhole_p, label="IPR")
plt.plot(flow_rate[1:], IPR[1:], label="TPR")
plt.xlabel("Flow Rate (Mscf/d)")
plt.ylabel("Bottomhole Pressure (psi)")
plt.title("IPR-TPR")

# Finding intersection point
line_1 = LineString(np.column_stack((flow_rate, bottomhole_p)))
line_2 = LineString(np.column_stack((flow_rate, IPR)))
intersection = line_1.intersection(line_2)

# Plotting intersection point
plt.plot(*intersection.xy, "ro", label="INTERSECTION")
plt.legend()
plt.show()

# Displaying intersection coordinates
print(intersection)
