#!/usr/bin/python

class pid(object):
    def __init__(self,kp,ki,kd,input_limits,output_limits,dt):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.p_term = 0
        self.i_term = 0
        self.d_term = 0
        self.input_llimit, self.input_ulimit = input_limits[0], input_limits[1]
        self.output_llimit, self.output_ulimit  = output_limits[0],output_limits[1] 
        self.last_error = 0.0

    def set_PID(self,kp,ki,kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def set_dt(self,dt):
        self.dt = dt

    def set_input_limit(self,limits):
        self.input_limits(limits)

    def set_output_limits(self,limits):
        self.output_limits(limits)

    def get_PID(self):
        return self.kp, self.ki, self.kd

    def clear(self):
        self.p_term = 0
        self.i_term = 0
        self.d_term = 0
        self.u = 0

    def output(self,setpoint,currentvalue,dt_real=[]):
        if dt_real != []:
            self.dt = dt_real
        error = setpoint - currentvalue
        delta_error = error - self.last_error
        self.p_term = error
        self.i_term += error * self.dt

        if self.i_term > self.input_ulimit:
           self.i_term = self.input_ulimit
        elif self.i_term < self.input_llimit:
           self.i_term = self.input_llimit
            
        self.d_term = delta_error / self.dt
        self.last_error = error
        self.u = (self.kp*error)+(self.ki * self.i_term)+(self.kd * self.d_term)

        if self.u > self.output_ulimit:
           self.u = self.output_ulimit
        elif self.u < self.output_llimit:
           self.u = self.output_llimit
        return self.u
        

'''
This code serves as a guide to show how the filters work. 
A filter_weighting of 0 zero will be equivalent to using
the gyro only. A value of 1 will be equivalent to using the accelerometer  
only. You can use serial_GetData.py to collect the data from the T-BOT
to see how effective your filter is.

This is not an efficient way of writing this in Python but the 
structure is matched to the C code on the T-Bot for illustration.  
'''

angle = 0
filter_weighting = 0.06
'''
def getAngleCFilter(pitch, gyro_rate, dt):
    global angle
    angle += gyro_rate * dt
    angle += filter_weighting * (pitch - angle)
    return angle
'''


class cfilter(object):
    def __init__(self,theta, angle, alpha, filter_weighting, dt):
        self.theta = theta
        self.angle = angle
        self.alpha = alpha
        self.filter_weighting = filter_weighting
        self.dt = dt
        
    def setFilterWeighting(self,filter_weighting):
        self.filter_weighting = filter_weighting
        
    def getAngleCFilter(self, theta, gyro_rate, dt):

        self.angle += self.filter_weighting * (theta - (self.angle + gyro_rate * dt))
        return self.angle
        
