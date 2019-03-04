/* Copyright (C) 2018 Gareth Nisbet, KLiK Robotics. All rights reserved.

 This software may be distributed and modified under the terms of the GNU
 General Public License version 2 (GPL2) as published by the Free Software
 Foundation and appearing in the file GPL2.TXT included in the packaging of
 this file. Please note that GPL2 Section 2[b] requires that all works based
 on this software must also be made publicly available under the terms of
 the GPL2 ("Copyleft").

 Contact information
 -------------------

 Gareth Nisbet, KLiK Robotics
 Web      :  http://www.klikrobotics.com
 e-mail   :  gareth.nisbet@klikrobotics.com
 */

class CFilter {
public:
    CFilter() {
        /* If the combination_weighting is zero then filter output will be the equal to the 
           gyro angle (the integral of the gyrorate). If the combination_weighting is 1, the
           output will be equal to the accelerometer angle.*/

        combination_weighting = 0.03;
        angle = 0; // Reset the angle

    };
        /* The angle should be in degrees and the rate should be in degrees per second and dt      
           in should be in seconds.*/
     
        double getAngle(double pitch, double gyrorate, double dt) {  // check to prevent NaN
        if ((pitch == pitch) && (gyrorate == gyrorate) && (dt == dt)){
        angle += dt * gyrorate;
        angle += combination_weighting * (pitch - angle);
        }
        return angle;
    };
    void setWeighting(double new_combination_weighting) { combination_weighting = new_combination_weighting; };

private:
    /* Combination Filter Variables */
    double combination_weighting; // Sets the relative weighting of the accelerometer and gyroscope contribution
    double angle; // The angle calculated by the CFilter 

};


