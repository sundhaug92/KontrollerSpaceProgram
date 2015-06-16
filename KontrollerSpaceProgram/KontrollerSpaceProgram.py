import threading,krpc,math

targetAltitude=100000
preApoWait1=5
preApoWait2=50
class AutoStager(threading.Thread):
    def run(x):
        print "AutoStager ON"
        vessel=conn.space_center.active_vessel
        while True:
            res=vessel.resources_in_decouple_stage(vessel.control.current_stage,False)
            if ((res.amount("LiquidFuel")==0 and res.has_resource("LiquidFuel")) or (res.amount("SolidFuel")==0 and res.has_resource("SolidFuel")) or (res.amount("XenonGas")==0 and res.has_resource("XenonGas")) or res.names==[]) and vessel.control.current_stage > 0:
                vessel.control.activate_next_stage()

class AutoMANU(threading.Thread):
    def run(x):
        print "AutoMANU ON"
        vessel=conn.space_center.active_vessel
        flight=vessel.flight(vessel.orbital_reference_frame)
        while True:
            ms=flight.mach*flight.speed_of_sound
            pitch,roll,heading=90,0,90
            if manu_mode==0:
                vessel.auto_pilot.sas=False
            if manu_mode==1:
                if ms<1800 and flight.speed_of_sound>0:
                    pitch=90*math.cos(3*ms/1800)
                else:
                    pitch=0
                if pitch < 0:
                    pitch = 0
                vessel.auto_pilot.set_rotation(pitch,heading,roll)
            if manu_mode==2:
                vessel.auto_pilot.sas_mode=conn.space_center.SASMode.prograde
class AutoMANO(threading.Thread):
    def run(x):
        print "AutoMANO ON"
        vessel=conn.space_center.active_vessel
        flight=vessel.flight(vessel.orbital_reference_frame)
        s,ps=-1,-1
        global manu_mode
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
                s=1
                manu_mode=1
                vessel.control.throttle=maxThrottle
            elif vessel.orbit.periapsis_altitude < targetAltitude and vessel.orbit.time_to_apoapsis > preApoWait2  and vessel.orbit.time_to_periapsis > vessel.orbit.time_to_apoapsis:
                s=2
                vessel.control.throttle=0
                manu_mode=2
            elif (vessel.orbit.periapsis_altitude < targetAltitude and vessel.orbit.time_to_apoapsis < preApoWait1) or vessel.orbit.time_to_periapsis < vessel.orbit.time_to_apoapsis:
                s=3
                vessel.control.throttle=maxThrottle
                manu_mode=2
            elif vessel.orbit.periapsis_altitude > targetAltitude:
                s=4
                vessel.control.throttle=0
                manu_mode=0
            if s<>ps:
                print "MANO FROM",ps,"TO",s
            ps=s

class SituAct(threading.Thread):
    def run(x):
        vessel=conn.space_center.active_vessel
        ps,s=0,0
        while True:
            s=vessel.situation
            if s<>ps:
                if action4situ.has_key(s) and action4situ[s]>-1:
                    vessel.control.toggle_action_group(action4situ[s])
print "Awaiting connection"
conn = krpc.connect(name='Kontroller')
action4situ={conn.space_center.VesselSituation.sub_orbital:1}

mano=AutoMANO()
print "Starting mano",
mano.start()
while not mano.isAlive():
    print ".",
print "OK"

manu_mode=1
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

situAct=SituAct()
print "Starting SituAct",
situAct.start()
while not situAct.isAlive():
    print ".",
print "OK"

print "All managers started"

while True:
    pass

