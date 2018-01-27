import numpy as np

def spiralCoilDimensionCalc(N,length,width,spacing,thickness,angle):

    z_thick=thickness # %pcb board thickness

    theta_rot=angle # %default value is pi/2
    # define dimensions
    l = length   # define side length of outer square
    w = width    # define width of each track
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

    line_segs = np.zeros(4*N)
    line_segs[0:3] = l


    i = 1
    # increment the decrease in length

    for seg_move in range(3,2*N,2):
        line_segs[seg_move:(seg_move+2)] = (l-i*ll_s)
        i = i+1
        
    i_smaller = i-1

    for seg_move in range(2*N-1,(4*N)-1,2):
        line_segs[seg_move:(seg_move+2)] = (l-i_smaller*ll_s)
        i = 1+i
        i_smaller = i_smaller-1

    line_segs[(4*N-3):(4*N-1)] = l
    line_segs[4*N-1] = l-ll_s


    x_traj = np.cos([theta_rot, theta_rot+.5*np.pi, theta_rot+np.pi, theta_rot+1.5*np.pi])
    y_traj = np.sin([theta_rot, theta_rot+.5*np.pi, theta_rot+np.pi, theta_rot+1.5*np.pi])

    q = 0

    for p in range(1,Points_total):
        x_points[p] = x_traj[q]*line_segs[p-1]+x_points[p-1]
        y_points[p] = y_traj[q]*line_segs[p-1]+y_points[p-1]
        q = q + 1
        if q == 4:
            q = 0


    x_points_new[0:2* N +1] = x_points[0:2*N +1]
    x_points_new[2*N +1] = x_points[2*N]
    x_points_new[2*N+2:Points_total+1] = x_points[2*N +1:Points_total]

    y_points_new[0:2* N +1] = y_points[0:2*N +1]
    y_points_new[2*N +1] = y_points[2*N]
    y_points_new[2*N +2:Points_total+1] = y_points[2*N +1:Points_total]

    z_points_new[0:2* N +2] = z_points[0:2* N +2]
    z_points_new[2*N +2] = z_points[2*N+1]
    z_points_new[2*N +3:Points_total+1] = z_points[2*N +2:Points_total]

    x_points_out = x_points_new
    y_points_out = y_points_new
    z_points_out = z_points_new

    if angle == np.pi/2:
        x_points_out = x_points_out+length/2
        y_points_out = y_points_out-length/2 
    else:
    
        y_points_out = y_points_out-length/(np.sqrt(2))

    return x_points_out, y_points_out, z_points_out

# Test
if __name__ == '__main__':
    l=70e-3 
    w=0.5e-3 
    s=0.25e-3 
    thickness=1.6e-3 
    Nturns=25

    [x,y,z] = spiralCoilDimensionCalc(Nturns, l, w, s, thickness, np.pi/4)
    print('Square coil test\nN = 25\n\n')
    print('x = ')

    print(x)

    print('\n\ny = ')
    print(y)

    print('\n\nz = ')
    print(z)