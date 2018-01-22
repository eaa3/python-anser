import numpy


def spiralCoilFieldCalcMatrix(I, xPoints, yPoints, zPoints, px, py, pz):
    

    numPoints = xPoints.length()

    ax = xPoints[:,1:numPoints-1] - xPoints[:,0:(numPoints-2)];
    ay = yPoints[:,1:numPoints-1] - yPoints[:,0:(numPoints-2)];
    az = zPoints[:,1:numPoints-1] - zPoints[:,0:(numPoints-2)];

    bx = xPoints[:,1:numPoints-1] - Px;
    by = yPoints[:,1:numPoints-1] - Py;
    bz = zPoints[:,1:numPoints-1] - Pz;

    cx=xPoints[:,0:(numPoints-2)] - Px;
    cy=yPoints[:,0:(numPoints-2)] - Py;
    cz=zPoints[:,0:(numPoints-2)] - Pz;

    cMag = np.sqrt(np.square(cx) + np.square(cy) + np.square(cz))
    bMag = np.sqrt(np.square(bx) + np.square(by) + np.square(bz))

    aDotb = np.multiply(ax,bx) + np.multiply(ay,by) + np.multiply(az,bz)
    aDotc = np.multiply(ax,cx) + np.multiply(ay,cy) + np.multiply(az,cz)

    cCrossa_x = np.multiply(az,cy) - np.multiply(ay,cz)
    cCrossa_y = np.multiply(ax,cz) - np.multiply(az,cx)
    cCrossa_z = np.multiply(ay,cx) - np.multiply(ax,cy)

    cCrossa_Mag_Squared =  np.square(cCrossa_x) + np.square(cCrossa_y) + np.square(cCrossa_z)

    scalar = np.divide((np.divide(aDotc,cMag) - np.divide(aDotb,bMag)),cCrossa_Mag_Squared)

    Hx_dum = (I/(4*pi))*np.multiply(cCrossa_x,scalar)
    Hy_dum = (I/(4*pi))*np.multiply(cCrossa_y,scalar)
    Hz_dum = (I/(4*pi))*np.multiply(cCrossa_z,scalar)

    Hx = np.sum(Hx_dum,0)
    Hy = np.sum(Hy_dum,0)
    Hz = np.sum(Hz_dum,0)

    return np.array([[Hx],[Hy],[Hz]])


    if __name__ == '__main__':
        spiralCoilFieldCalcMatrix(1,xPoints,yPoints,zPoints,px,py,pz)
        