import time
from mega_job import interface_run_one_job_cycle

##*** note:  Prob don't need the .sh but just in case consider it

cycle_time=60
c=0
while True:
    c+=1
    print ("[mega_job] cycle #"+str(c))
    try:
        interface_run_one_job_cycle()
    except Exception as e:
        print ("[mega_job] error: "+str(e))

#    print ("DEBUG BREAK AT 1")
#    break
    time.sleep(cycle_time)
    
