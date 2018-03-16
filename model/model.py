import numpy as np

class MagneticModel():


    def __init__(self, modelType='square', coilTurns=25, length=70e-3, width=0.5e-3, spacing=0.25e-3, thick=1.6e-3):



        if modelType.upper() == 'SQUARE':

            self.modelType = modelType
            self.coilTurns = coilTurns
            self.turnLength = length
            self.traceWidth = width
            self.traceSpacing = spacing
            self.traceThickness = thick

            self.xPointsTrans = np.array([])
            self.yPointsTrans = np.array([])
            self.zPointsTrans = np.array([])

            x_centres = np.array([-93.543, 0, 93.543, -68.55, 68.55, -93.543, 0, 93.543])
            x_centres = x_centres * 1.0e-3
            y_centres = np.array([93.543, 68.55, 93.543, 0, 0, -93.543, -68.55, -93.543])
            y_centres = y_centres * 1.0e-3

            self.numCoils = x_centres.shape[0]

            [xPointsA, yPointsA, zPointsA] = self._spiralCoilDimensionCalc(self.coilTurns,
                                                                                         self.turnLength,
                                                                                         self.traceWidth,
                                                                                         self.traceSpacing,
                                                                                         self.traceThickness, np.pi / 4)
            [xPointsV, yPointsV, zPointsV] = self._spiralCoilDimensionCalc(self.coilTurns,
                                                                                         self.turnLength,
                                                                                         self.traceWidth,
                                                                                         self.traceSpacing,
                                                                                         self.traceThickness, np.pi / 2)

            self.xPointsTrans = np.zeros([x_centres.shape[0], xPointsA.shape[0]])
            self.yPointsTrans = np.zeros([x_centres.shape[0], xPointsA.shape[0]])
            self.zPointsTrans = np.zeros([x_centres.shape[0], xPointsA.shape[0]])

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

            self.xPointsTrans = np.array(
                [xPoints1, xPoints2, xPoints3, xPoints4, xPoints5, xPoints6, xPoints7, xPoints8])
            self.yPointsTrans = np.array(
                [yPoints1, yPoints2, yPoints3, yPoints4, yPoints5, yPoints6, yPoints7, yPoints8])
            self.zPointsTrans = np.array(
                [zPoints1, zPoints2, zPoints3, zPoints4, zPoints5, zPoints6, zPoints7, zPoints8])


    def getField(self, p=np.array([0,0,0])):

        Hx, Hy, Hz = self._spiralCoilFieldCalcMatrix(
            1, self.xPointsTrans, self.yPointsTrans, self.zPointsTrans, p[0], p[1], p[2])

        return Hx, Hy, Hz


    def _spiralCoilFieldCalcMatrix(self, I, xPoints, yPoints, zPoints, Px, Py, Pz):
        numPoints = xPoints.shape[1]

        # matrix conversions

        xPoints = np.matrix(xPoints)
        yPoints = np.matrix(yPoints)
        zPoints = np.matrix(zPoints)

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

    def _spiralCoilDimensionCalc(self, N, length, width, spacing, thickness, angle):

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