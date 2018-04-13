import numpy as np

class CoilModel():

    # The init function should initialise and prepare all data necessary for 'coil_field' to operate
    def __init__(self, module_config):
        self.xPoints, self.yPoints, self.zPoints = coil_definition(module_config)

    # MUST BE DEFINED. A User defined function which returns the magnetic field intensity H at a point in space P.
    # This function must be defined as accepting a cartesian coordinate (x,y,z),
    # and returning a three magnetic intensity values Hx, Hy and Hz
    def coil_field_total(self, Px, Py, Pz):
        I = 1
        numPoints = self.xPoints.shape[1]

        # matrix conversions

        xPoints = np.matrix(self.xPoints)
        yPoints = np.matrix(self.yPoints)
        zPoints = np.matrix(self.zPoints)

        ax = xPoints[:, 1:numPoints] - xPoints[:, 0:(numPoints - 1)]
        ay = yPoints[:, 1:numPoints] - yPoints[:, 0:(numPoints - 1)]
        az = zPoints[:, 1:numPoints] - zPoints[:, 0:(numPoints - 1)]

        bx = xPoints[:, 1:numPoints] - Px
        by = yPoints[:, 1:numPoints] - Py
        bz = zPoints[:, 1:numPoints] - Pz

        cx = xPoints[:, 0:(numPoints - 1)] - Px
        cy = yPoints[:, 0:(numPoints - 1)] - Py
        cz = zPoints[:, 0:(numPoints - 1)] - Pz

        cMag = np.sqrt(np.square(cx) + np.square(cy) + np.square(cz))
        bMag = np.sqrt(np.square(bx) + np.square(by) + np.square(bz))

        aDotb = np.multiply(ax, bx) + np.multiply(ay, by) + np.multiply(az, bz)
        aDotc = np.multiply(ax, cx) + np.multiply(ay, cy) + np.multiply(az, cz)

        cCrossa_x = np.multiply(az, cy) - np.multiply(ay, cz)
        cCrossa_y = np.multiply(ax, cz) - np.multiply(az, cx)
        cCrossa_z = np.multiply(ay, cx) - np.multiply(ax, cy)

        cCrossa_Mag_Squared = np.square(cCrossa_x) + np.square(cCrossa_y) + np.square(cCrossa_z)

        scalar = np.divide((np.divide(aDotc, cMag) - np.divide(aDotb, bMag)), cCrossa_Mag_Squared)

        Hx_dum = (I / (4 * np.pi)) * np.multiply(cCrossa_x, scalar)
        Hy_dum = (I / (4 * np.pi)) * np.multiply(cCrossa_y, scalar)
        Hz_dum = (I / (4 * np.pi)) * np.multiply(cCrossa_z, scalar)

        Hx = np.sum(Hx_dum, axis=1)
        Hy = np.sum(Hy_dum, axis=1)
        Hz = np.sum(Hz_dum, axis=1)

        return Hx, Hy, Hz

    def coil_field_single(self, Px, Py, Pz, coilindex=0):
        I = 1
        numPoints = self.xPoints.shape[1]

        # matrix conversions

        xPoints = np.matrix(self.xPoints[coilindex, :])
        yPoints = np.matrix(self.yPoints[coilindex, :])
        zPoints = np.matrix(self.zPoints[coilindex, :])

        ax = xPoints[:, 1:numPoints] - xPoints[:, 0:(numPoints - 1)]
        ay = yPoints[:, 1:numPoints] - yPoints[:, 0:(numPoints - 1)]
        az = zPoints[:, 1:numPoints] - zPoints[:, 0:(numPoints - 1)]

        bx = xPoints[:, 1:numPoints] - Px
        by = yPoints[:, 1:numPoints] - Py
        bz = zPoints[:, 1:numPoints] - Pz

        cx = xPoints[:, 0:(numPoints - 1)] - Px
        cy = yPoints[:, 0:(numPoints - 1)] - Py
        cz = zPoints[:, 0:(numPoints - 1)] - Pz

        cMag = np.sqrt(np.square(cx) + np.square(cy) + np.square(cz))
        bMag = np.sqrt(np.square(bx) + np.square(by) + np.square(bz))

        aDotb = np.multiply(ax, bx) + np.multiply(ay, by) + np.multiply(az, bz)
        aDotc = np.multiply(ax, cx) + np.multiply(ay, cy) + np.multiply(az, cz)

        cCrossa_x = np.multiply(az, cy) - np.multiply(ay, cz)
        cCrossa_y = np.multiply(ax, cz) - np.multiply(az, cx)
        cCrossa_z = np.multiply(ay, cx) - np.multiply(ax, cy)

        cCrossa_Mag_Squared = np.square(cCrossa_x) + np.square(cCrossa_y) + np.square(cCrossa_z)

        scalar = np.divide((np.divide(aDotc, cMag) - np.divide(aDotb, bMag)), cCrossa_Mag_Squared)

        Hx_dum = (I / (4 * np.pi)) * np.multiply(cCrossa_x, scalar)
        Hy_dum = (I / (4 * np.pi)) * np.multiply(cCrossa_y, scalar)
        Hz_dum = (I / (4 * np.pi)) * np.multiply(cCrossa_z, scalar)

        Hx = np.sum(Hx_dum, axis=1)
        Hy = np.sum(Hy_dum, axis=1)
        Hz = np.sum(Hz_dum, axis=1)

        return Hx, Hy, Hz


# Function used to define the dimensions of each coil in the square coil model
def coil_definition(model_config):
    if str(model_config['model_name']).upper() == 'SQUARE_MODEL':
        modelType = model_config['model_name']
        coilTurns = model_config['num_turns']
        turnLength = model_config['trace_length']
        traceWidth = model_config['trace_width']
        traceSpacing = model_config['trace_spacing']
        traceThickness = model_config['trace_thickness']

        xPointsTrans = np.array([])
        yPointsTrans = np.array([])
        zPointsTrans = np.array([])

        x_centres = np.array(model_config['centers_x'])
        x_centres = x_centres * 1.0e-3
        y_centres = np.array(model_config['centers_y'])
        y_centres = y_centres * 1.0e-3

        numCoils = x_centres.shape[0]

        [xPointsA, yPointsA, zPointsA] = _spiralCoilDimensionCalc(coilTurns,
                                                                       turnLength,
                                                                       traceWidth,
                                                                       traceSpacing,
                                                                       traceThickness, np.pi / 4)
        [xPointsV, yPointsV, zPointsV] = _spiralCoilDimensionCalc(coilTurns,
                                                                       turnLength,
                                                                       traceWidth,
                                                                       traceSpacing,
                                                                       traceThickness, np.pi / 2)

        xPointsTrans = np.zeros([x_centres.shape[0], xPointsA.shape[0]])
        yPointsTrans = np.zeros([x_centres.shape[0], xPointsA.shape[0]])
        zPointsTrans = np.zeros([x_centres.shape[0], xPointsA.shape[0]])

        xPoints1 = xPointsV + x_centres[0]
        xPoints2 = xPointsA + x_centres[1]
        xPoints3 = xPointsV + x_centres[2]
        xPoints4 = xPointsA + x_centres[3]
        xPoints5 = xPointsA + x_centres[4]
        xPoints6 = xPointsV + x_centres[5]
        xPoints7 = xPointsA + x_centres[6]
        xPoints8 = xPointsV + x_centres[7]

        yPoints1 = yPointsV + y_centres[0]
        yPoints2 = yPointsA + y_centres[1]
        yPoints3 = yPointsV + y_centres[2]
        yPoints4 = yPointsA + y_centres[3]
        yPoints5 = yPointsA + y_centres[4]
        yPoints6 = yPointsV + y_centres[5]
        yPoints7 = yPointsA + y_centres[6]
        yPoints8 = yPointsV + y_centres[7]

        zPoints1 = zPointsV
        zPoints2 = zPointsA
        zPoints3 = zPointsV
        zPoints4 = zPointsA
        zPoints5 = zPointsA
        zPoints6 = zPointsV
        zPoints7 = zPointsA
        zPoints8 = zPointsV

        xPoints = np.array(
            [xPoints1, xPoints2, xPoints3, xPoints4, xPoints5, xPoints6, xPoints7, xPoints8])
        yPoints = np.array(
            [yPoints1, yPoints2, yPoints3, yPoints4, yPoints5, yPoints6, yPoints7, yPoints8])
        zPoints = np.array(
            [zPoints1, zPoints2, zPoints3, zPoints4, zPoints5, zPoints6, zPoints7, zPoints8])

        return xPoints, yPoints, zPoints
    else:
        return 'Error calculating points'


# User defined function for generating coil filaments.
def _spiralCoilDimensionCalc(N, length, width, spacing, thickness, angle):

    z_thick = thickness  # %pcb board thickness

    theta_rot = angle  # %default value is pi/2
    # define dimensions
    l = length  # define side length of outer square
    w = width  # define width of each track
    s = spacing  # define spacing between tracks

    ll_s = w + s  # line to line spacing

    Points_total = (4 * N) + 1

    x_points = np.zeros(Points_total)
    y_points = np.zeros(Points_total)
    z_points = np.zeros(Points_total)

    z_points[(2 * N + 1):Points_total] = -z_thick

    x_points_new = np.zeros(Points_total + 1)
    y_points_new = np.zeros(Points_total + 1)
    z_points_new = np.zeros(Points_total + 1)

    x_points_out = np.zeros(Points_total + 1)
    y_points_out = np.zeros(Points_total + 1)
    z_points_out = np.zeros(Points_total + 1)

    line_segs = np.zeros(4 * N)
    line_segs[0:3] = l

    i = 1
    # increment the decrease in length

    for seg_move in range(3, 2 * N, 2):
        line_segs[seg_move:(seg_move + 2)] = (l - i * ll_s)
        i = i + 1

    i_smaller = i - 1

    for seg_move in range(2 * N - 1, (4 * N) - 1, 2):
        line_segs[seg_move:(seg_move + 2)] = (l - i_smaller * ll_s)
        i = 1 + i
        i_smaller = i_smaller - 1

    line_segs[(4 * N - 3):(4 * N - 1)] = l
    line_segs[4 * N - 1] = l - ll_s

    x_traj = np.cos([theta_rot, theta_rot + .5 * np.pi, theta_rot + np.pi, theta_rot + 1.5 * np.pi])
    y_traj = np.sin([theta_rot, theta_rot + .5 * np.pi, theta_rot + np.pi, theta_rot + 1.5 * np.pi])

    q = 0

    for p in range(1, Points_total):
        x_points[p] = x_traj[q] * line_segs[p - 1] + x_points[p - 1]
        y_points[p] = y_traj[q] * line_segs[p - 1] + y_points[p - 1]
        q = q + 1
        if q == 4:
            q = 0

    x_points_new[0:2 * N + 1] = x_points[0:2 * N + 1]
    x_points_new[2 * N + 1] = x_points[2 * N]
    x_points_new[2 * N + 2:Points_total + 1] = x_points[2 * N + 1:Points_total]

    y_points_new[0:2 * N + 1] = y_points[0:2 * N + 1]
    y_points_new[2 * N + 1] = y_points[2 * N]
    y_points_new[2 * N + 2:Points_total + 1] = y_points[2 * N + 1:Points_total]

    z_points_new[0:2 * N + 2] = z_points[0:2 * N + 2]
    z_points_new[2 * N + 2] = z_points[2 * N + 1]
    z_points_new[2 * N + 3:Points_total + 1] = z_points[2 * N + 2:Points_total]

    x_points_out = x_points_new
    y_points_out = y_points_new
    z_points_out = z_points_new

    if angle == np.pi / 2:
        x_points_out = x_points_out + length / 2
        y_points_out = y_points_out - length / 2
    else:

        y_points_out = y_points_out - length / (np.sqrt(2))

    return x_points_out, y_points_out, z_points_out