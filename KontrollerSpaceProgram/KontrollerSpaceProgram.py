import threading,krpc,math

targetAltitude=100000
preApoWait1=10
preApoWait2=30
class AutoStager(threading.Thread):
    def run(x):
        print "AutoStager ON"
        vessel=conn.space_center.active_vessel
        while True:
            res=vessel.resources_in_decouple_stage(vessel.control.current_stage,False)
            if (res.amount("LiquidFuel")==0) and vessel.control.current_stage > 0:
                vessel.control.activate_next_stage()

class AutoMANU(threading.Thread):
    def run(x):
        print "AutoMANU ON"
        vessel=conn.space_center.active_vessel
        flight=vessel.flight(vessel.orbital_reference_frame)
        while True:
            ms=flight.mach*flight.speed_of_sound
            pitch,roll,heading=90,0,90
            if ms<1800 and flight.speed_of_sound>0:
                pitch=90*math.cos(3*ms/1800)
            else:
                pitch=0
            if pitch < 0:
                pitch = 0
            vessel.auto_pilot.set_rotation(pitch,heading,roll)
class AutoMANO(threading.Thread):
    def run(x):
        print "AutoMANO ON"
        vessel=conn.space_center.active_vessel
        flight=vessel.flight(vessel.orbital_reference_frame)
        while True:
            ms=flight.mach*flight.speed_of_sound
            maxThrottle=1
            if flight.terminal_velocity < ms:
                maxThrottle=flight.terminal_velocity/ms
            if maxThrottle<0:
                maxThrottle=0
            if maxThrottle>1:
                maxThrottle=1
            if vessel.orbit.apoapsis_altitude<targetAltitude:
                vessel.control.throttle=maxThrottle
            elif vessel.orbit.periapsis_altitude < targetAltitude and vessel.orbit.time_to_apoapsis > preApoWait1 and vessel.orbit.time_to_periapsis > vessel.orbit.time_to_apoapsis:
                vessel.control.throttle=0
            elif vessel.orbit.periapsis_altitude < targetAltitude and vessel.orbit.time_to_apoapsis < preApoWait2 or vessel.orbit.time_to_periapsis < vessel.orbit.time_to_apoapsis:
                vessel.control.throttle=maxThrottle
            else:
                vessel.control.throttle=0
            pass

print "Awaiting connection"
conn = krpc.connect(name='Kontroller')

mano=AutoMANO()
print "Starting mano",
mano.start()
while not mano.isAlive():
    print ".",
print "OK"

manu=AutoMANU()
print "Starting manu",
manu.start()
while not manu.isAlive():
    print ".",
print "OK"

stager=AutoStager()
print "Starting stager",
stager.start()
while not stager.isAlive():
    print ".",
print "OK"

print "All managers started"

while True:
    pass

