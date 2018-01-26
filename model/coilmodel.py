import numpy as np


def spiralCoilFieldCalcMatrix(I, xPoints, yPoints, zPoints, Px, Py, Pz):


    numPoints = xPoints.shape[1]


    # matrix conversions

    xPoints = np.matrix(xPoints)
    yPoints = np.matrix(yPoints)
    zPoints = np.matrix(zPoints)

    ax = xPoints[:, 1:numPoints] - xPoints[:, 0:(numPoints-1)]
    ay = yPoints[:, 1:numPoints] - yPoints[:, 0:(numPoints-1)]
    az = zPoints[:, 1:numPoints] - zPoints[:, 0:(numPoints-1)]

    bx = xPoints[:, 1:numPoints] - Px
    by = yPoints[:, 1:numPoints] - Py
    bz = zPoints[:, 1:numPoints] - Pz

    cx = xPoints[:, 0:(numPoints-1)] - Px
    cy = yPoints[:, 0:(numPoints-1)] - Py
    cz = zPoints[:, 0:(numPoints-1)] - Pz

    cMag = np.sqrt(np.square(cx) + np.square(cy) + np.square(cz))
    bMag = np.sqrt(np.square(bx) + np.square(by) + np.square(bz))

    aDotb = np.multiply(ax, bx) + np.multiply(ay, by) + np.multiply(az, bz)
    aDotc = np.multiply(ax, cx) + np.multiply(ay, cy) + np.multiply(az, cz)

    cCrossa_x = np.multiply(az, cy) - np.multiply(ay, cz)
    cCrossa_y = np.multiply(ax, cz) - np.multiply(az, cx)
    cCrossa_z = np.multiply(ay, cx) - np.multiply(ax, cy)

    cCrossa_Mag_Squared =  np.square(cCrossa_x) + np.square(cCrossa_y) + np.square(cCrossa_z)

    scalar = np.divide((np.divide(aDotc, cMag) - np.divide(aDotb, bMag)), cCrossa_Mag_Squared)

    Hx_dum = (I/(4*np.pi))*np.multiply(cCrossa_x, scalar)
    Hy_dum = (I/(4*np.pi))*np.multiply(cCrossa_y, scalar)
    Hz_dum = (I/(4*np.pi))*np.multiply(cCrossa_z, scalar)

    Hx = np.sum(Hx_dum, axis=1)
    Hy = np.sum(Hy_dum, axis=1)
    Hz = np.sum(Hz_dum, axis=1)

    return Hx, Hy, Hz


if __name__ == '__main__':
    from coilpoints import spiralCoilDimensionCalc

    l = 70e-3
    w = 0.5e-3
    s = 0.25e-3
    thickness = 1.6e-3
    Nturns = 25

    [xPoints, yPoints, zPoints] = spiralCoilDimensionCalc(Nturns, l, w, s, thickness, np.pi/4)
    px = 0
    py = 0
    pz = 0.12
    [hx,hy,hz] = spiralCoilFieldCalcMatrix(1, xPoints, yPoints, zPoints, px, py, pz)

    p = 0;
