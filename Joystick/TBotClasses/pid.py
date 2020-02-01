#!/usr/bin/python
import time

class pid(object):
    def __init__(self,kp,ki,kd,int_limits,output_limits,dt):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.p_term = 0
        self.i_term = 0
        self.d_term = 0
        self.int_llimit, self.int_ulimit = int_limits[0], int_limits[1]
        self.output_llimit, self.output_ulimit  = output_limits[0],output_limits[1] 
        self.last_error = 0.0

    def set_PID(self,kp,ki,kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def set_dt(self,kp,ki,kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def set_int_limit(self,limits):
        self.int_limits(limits)

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

        if self.i_term > self.int_ulimit:
           self.i_term = self.int_ulimit
        elif self.i_term < self.int_llimit:
           self.i_term = self.int_llimit
            
        self.d_term = delta_error / self.dt
        self.last_error = error
        self.u = (self.kp*error)+(self.ki * self.i_term)+(self.kd * self.d_term)

        if self.u > self.output_ulimit:
           self.u = self.output_ulimit
        elif self.u < self.output_llimit:
           self.u = self.output_llimit
        return self.u
        
