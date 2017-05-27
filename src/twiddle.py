import sys
import os
import time
from subprocess import Popen, PIPE

def run_pid(pid_path, p, i, d, max_run_time=60):
    # Runs pid with given coefficients as arguments. Monitors the CTE
    # to detect if the car has veered too much from the center of the lane
    # and estimates the distance the car has traveled by integrating the
    # speed. Returns the error for the run.
    distance = 0.0
    cte_squared = 0.0
    input('Reset the simulator and press a ENTER to start')
    start_time = None
    try:
        print('Running PID with P = %f I = %f D = %f' % (p, i, d))
        p = Popen([pid_path, str(p), str(i) , str(d)], stdout=PIPE, universal_newlines=True)
        cte = None
        while 1:
            line = p.stdout.readline().strip()
            if start_time and time.time() - start_time > max_run_time:
                print('Time out after %d seconds' % max_run_time)
                break
            if 'CTE:' in line:
                if start_time is None:
                    start_time = time.time()
                cte = float(line.split()[1])
                cte_squared += cte ** 2
                if abs(cte) > 4:
                    print('Cross-track error > 4')
                    break
            elif 'Speed: ' in line:
                speed = float(line.split()[1])
                distance += speed
            #print('Distance %f, total CTE %f' % (distance, total_cte))
    finally:
        print('Killing pid...')
        p.kill()
    
    #return cte_squared / distance
    return 1 / distance


pid_path = sys.argv[1]

if len(sys.argv) > 2:
    p = [float(arg) for arg in sys.argv[2:5]]
    dp = [float(arg) for arg in sys.argv[5:8]]
else:
    p = [1, 0, 5]
    dp = [1, 1, 1]
tolerance = 0.1
print('P = %f I = %f D = %f dP = %f dI = %f dD = %f' % tuple(p + dp))
best_error = run_pid(pid_path, *p)
print('Initial error:', best_error)
# Twiddle
while sum(dp) > tolerance:
    for i in range(len(p)):
        for change in [dp[i], -2 * dp[i]]:
            p[i] += change
            print('P = %f I = %f D = %f dP = %f dI = %f dD = %f' % tuple(p + dp))
            error = run_pid(pid_path, *p)
            print('Error:', error)
            if error < best_error:
                print('New best error!')
                best_error = error
                dp[i] *= 1.1
                break
        else:
            p[i] += dp[i]
            dp[i] *= 0.9
            


