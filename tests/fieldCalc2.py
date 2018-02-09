from coilmodel import  spiralCoilFieldCalcMatrix
from coilpoints import spiralCoilDimensionCalc
from objective import objectiveCoilSquareCalc3D_2
import time
from scipy.optimize import least_squares
import numpy as np
from constants import u0, pi


if __name__== '__main__':

    l = 70e-3
    w = 0.5e-3
    s = 0.25e-3
    thickness = 1.6e-3
    Nturns = 25

    [x_points_a, y_points_a, z_points_a] = spiralCoilDimensionCalc(Nturns, l, w, s, thickness, np.pi / 4, )
    [x_points_v, y_points_v, z_points_v] = spiralCoilDimensionCalc(Nturns, l, w, s, thickness, np.pi / 2, )

    x_centres = np.array([-93.543, 0, 93.543, -68.55, 68.55, -93.543, 0, 93.543])
    x_centres = x_centres * 1.0e-3
    y_centres = np.array([93.543, 68.55, 93.543, 0, 0, -93.543, -68.55, -93.543])
    y_centres = y_centres * 1.0e-3

    x_points1 = x_points_v + x_centres[0]
    x_points2 = x_points_a + x_centres[1]
    x_points3 = x_points_v + x_centres[2]
    x_points4 = x_points_a + x_centres[3]
    x_points5 = x_points_a + x_centres[4]
    x_points6 = x_points_v + x_centres[5]
    x_points7 = x_points_a + x_centres[6]
    x_points8 = x_points_v + x_centres[7]

    y_points1 = y_points_v + y_centres[0]
    y_points2 = y_points_a + y_centres[1]
    y_points3 = y_points_v + y_centres[2]
    y_points4 = y_points_a + y_centres[3]
    y_points5 = y_points_a + y_centres[4]
    y_points6 = y_points_v + y_centres[5]
    y_points7 = y_points_a + y_centres[6]
    y_points8 = y_points_v + y_centres[7]

    z_points1 = z_points_v
    z_points2 = z_points_a
    z_points3 = z_points_v
    z_points4 = z_points_a
    z_points5 = z_points_a
    z_points6 = z_points_v
    z_points7 = z_points_a
    z_points8 = z_points_v

    x_matrix = np.matrix(np.array([[x_points1], [x_points2], [x_points3], [x_points4], [x_points5], [x_points6], [x_points7], [x_points8]]))
    y_matrix = np.matrix(np.array([[y_points1], [y_points2], [y_points3], [y_points4], [y_points5], [y_points6], [y_points7], [y_points8]]))
    z_matrix = np.matrix(np.array([[z_points1], [z_points2], [z_points3], [z_points4], [z_points5], [z_points6], [z_points7], [z_points8]]))


    # Enter simulated sensor position and orientation here
    testPoint = np.array([0.05, 0.05, 0.14, 1.0, 0.0, 0.0, 1])
    # Calculate the flux density at the simulated sensor position
    [Hx, Hy, Hz] = spiralCoilFieldCalcMatrix(1, x_matrix, y_matrix, z_matrix, testPoint[0], testPoint[1], testPoint[2])

    Bx = Hx * u0
    By = Hy * u0
    Bz = Hz * u0

    # Determine the flux cutting the sensor at the simulated orientation.
    # Dot product of the B vector with the A vector (the sensor orientation)
    Bxsensor = Bx * testPoint[3]
    Bysensor = By * testPoint[4]
    Bzsensor = Bz * testPoint[5]

    Btest = Bxsensor + Bysensor + Bzsensor
    np.append(Btest,[[1]],axis=0)

    # Specify initial condition for the solver
    initialCond = np.array([0.0, 0.0, 0.3, 0, 0, 1, 1])

    # Specify the bounds for the trust region algorithm
    lowerbound = np.array([-0.5, -0.5, 0, -1,-1,-1, 0.99999999999])
    upperbound = np.array([0.5, 0.5, 0.5, 1, 1, 1, 1])

    times = np.zeros([100,])

    for i in range(100):
        tic = time.clock()
        res_1 = least_squares(objectiveCoilSquareCalc3D_2, initialCond, args=(x_matrix, y_matrix, z_matrix, Btest, np.ones([8,1])),  jac='2-point', bounds=(lowerbound, upperbound), method='trf', ftol=1e-16, xtol=1e-8, gtol=1e-12, verbose=1)
        toc = time.clock()
        times[i] = tic - toc

    print("Test x = ", '%f' % testPoint[0])
    print("Test y = ", '%f' % testPoint[1])
    print("Test z = ", '%f' % testPoint[2])
    print("Test a = ", '%f' % testPoint[3])
    print("Test b = ", '%f' % testPoint[4])
    print("Test c = ", '%f' % testPoint[5])

    print("Initial x ," '%f' % initialCond[0])
    print("Initial y ," '%f' % initialCond[1])
    print("Initial z ," '%f' % initialCond[2])
    print("Initial a ," '%f' % initialCond[3])
    print("Initial b ," '%f' % initialCond[4])
    print("Initial c ," '%f' % initialCond[5])

    print("x = ", '%f' % res_1.x[0])
    print("y = ", '%f' % res_1.x[1])
    print("z = ", '%f' % res_1.x[2])
    print("a = ", '%f' % res_1.x[3])
    print("b = ", '%f' % res_1.x[4])
    print("c = ", '%f' % res_1.x[5])
    # print(times)
    # print(1/times)
    dummy = 0

