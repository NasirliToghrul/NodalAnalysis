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


a=1
b=2
d=3
e=4
f=5
g=6

#Input: Values are the examples values, should be changed according to the requirements
measured_depth = 5000+(e+1)*20
sg_gas = 0.65+(g+1)/50
tubing_ID = 1.61
roughness = 0.00062
wellhead_pressure = 800+(e+1)*20
wellhead_temperature = 110
reservoir_pressure = 1952
reservoir_temeprature = 180
c = 0.01936
n = 0.8608
carbon_dioxide = (e+1)/100
nitrogen = (f+1)/100
hydrogen_sulfur = (d+1)/100
angle = 0

#Standing Correlation
Tpc = 168+325*sg_gas-12.5*(sg_gas**2)
Ppc = 677+15*0.647-37.5*(sg_gas**2)

flow_rate = []
method = "CarrKobayashi"
bottomhole_p = []
IPR = []
q = 0

for i in range(10000):

    flow_rate.append(q)
    average_pressure = (wellhead_pressure+reservoir_pressure)/2
    average_temperature = (wellhead_temperature+reservoir_temeprature)/2 +460

    #Redlich & Kwong EOS
    z_factor = pvt.redlich_kwong_eos(average_pressure,average_temperature,sg_gas,carbon_dioxide,hydrogen_sulfur,method, nitrogen)


    #Lee-Gonzales & Eakin
    u = pvt.lee_gonzales_eakin(average_pressure,average_temperature,sg_gas,carbon_dioxide,hydrogen_sulfur,method,nitrogen)

    s = 0.0375*sg_gas*measured_depth*np.cos(angle/57.3)/(z_factor*average_temperature)
    reynolds = 20.1*q*sg_gas/(tubing_ID*u)
    f = (1/(1.14-2*np.log10(roughness+21.25/reynolds**0.9)))**2
    bottomhole_pressure = np.sqrt((np.exp(s)*wellhead_pressure**2)+((25*sg_gas*z_factor*average_temperature*f*measured_depth*q**2*(np.exp(s)-1)))/(tubing_ID**5*s*10**6))
    bottomhole_p.append(bottomhole_pressure)
    ipr = np.sqrt(reservoir_pressure**2-(q/c)**(1/n))
    IPR.append(ipr)
    q = q+10

    if ipr>0:
        continue
    else:
        break


plt.plot(flow_rate, bottomhole_p, label = "IPR")
plt.plot(flow_rate[1:], IPR[1:], label = "TPR")
plt.xlabel("Flow Rate (Mscf/d)")
plt.ylabel("Bottomhole Pressure (psi)")
plt.title("IPR-TPR")

line_1 = LineString(np.column_stack((flow_rate,bottomhole_p)))
line_2 = LineString(np.column_stack((flow_rate, IPR)))
intersection = line_1.intersection(line_2)

plt.plot(*intersection.xy, "ro", label = "INTERSECTION")
plt.legend()
plt.show()

print(intersection)