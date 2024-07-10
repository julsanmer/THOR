import matplotlib.pyplot as plt
import numpy as np
import pickle as pck
import os
import matplotlib.gridspec as gridspec
from matplotlib import rc

from Basilisk import __path__
bsk_path = __path__[0] + '/supportData/LocalGravData/'

m2km = 1e-3
rad2deg = 180/np.pi

font = 20
font_legend = 15
font_map = 15
color_asteroid = [105/255, 105/255, 105/255]
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)


# This function plots orbits
def plot_orbits(orbits):
    # Get polyhedron
    shape = orbits.asteroid.shape
    xyz_vert = shape.xyz_vert
    order_face = shape.order_face

    # Create grid of plots
    gs = gridspec.GridSpec(2, 6)
    ax = []
    fig = plt.figure(figsize=(14, 8))
    ax.append(plt.subplot(gs[0, 0:2], projection='3d'))
    ax.append(plt.subplot(gs[0, 2:4], projection='3d'))
    ax.append(plt.subplot(gs[0, 4:6], projection='3d'))
    ax.append(plt.subplot(gs[1, 1:3], projection='3d'))
    ax.append(plt.subplot(gs[1, 3:5], projection='3d'))
    for i in range(len(ax)):
        inc0 = orbits.orbits[0][i].oe[2] * rad2deg
        lines = []

        # Plot asteroid
        ax[i].plot_trisurf(xyz_vert[:, 0] * m2km, xyz_vert[:, 1] * m2km, xyz_vert[:, 2] * m2km,
                           triangles=order_face - 1, color=color_asteroid, zorder=0)

        # Loop through orbits
        for j in range(len(orbits.orbits)):
            a0 = orbits.orbits[j][i].oe[0] * m2km
            ax[i].plot(orbits.orbits[j][i].data.pos_BP_P[0, 0] * m2km,
                       orbits.orbits[j][i].data.pos_BP_P[0, 1] * m2km,
                       orbits.orbits[j][i].data.pos_BP_P[0, 2] * m2km,
                       marker='.', color=colors[j])
            ax[i].plot(orbits.orbits[j][i].data.pos_BP_P[-1, 0] * m2km,
                       orbits.orbits[j][i].data.pos_BP_P[-1, 1] * m2km,
                       orbits.orbits[j][i].data.pos_BP_P[-1, 2] * m2km,
                       marker='s', markersize=4, color=colors[j])
            line, = ax[i].plot(orbits.orbits[j][i].data.pos_BP_P[:, 0] * m2km,
                               orbits.orbits[j][i].data.pos_BP_P[:, 1] * m2km,
                               orbits.orbits[j][i].data.pos_BP_P[:, 2] * m2km,
                               label='$a_0=' + str(int(a0)) + '$ km', color=colors[j])
            lines.append(line)

        # Labels
        ax[i].set_xlabel('$x$ [km]', fontsize=font-5, labelpad=2.5)
        ax[i].set_ylabel('$y$ [km]', fontsize=font-5, labelpad=2.5)
        ax[i].set_zlabel('$z$ [km]', fontsize=font-5, labelpad=2.5)
        ax[i].tick_params(axis='both', labelsize=font-5)
        ax[i].set_facecolor('white')
        ax[i].set_title('$i_0=' + str(int(inc0)) + '^{\circ}$', fontsize=font_map, pad=0)

        # Set limits
        ax[i].set_xlim(-50, 50)
        ax[i].set_ylim(-50, 50)
        ax[i].set_zlim(-50, 50)

    # Global
    fig.suptitle('Constant density polyhedron', fontsize=font-5)
    fig.legend(handles=lines, bbox_to_anchor=(0.97, 0.15),
               fontsize=font_legend)
    fig.tight_layout()
    plt.savefig('Plots/orbits_' + model + '.pdf',
                format='pdf', bbox_inches='tight')


# This function plots propagation errors
def plot_errors(orbits1, orbits2):
    # Root-mean square errors
    RMSE1_list = []
    RMSE2_list = []

    # Loop
    for i in range(len(orbits1)):
        # Number of semi-major axes and inclinations
        n_a, n_inc = orbits1[i].n_a, orbits1[i].n_inc
        inc0 = np.zeros(n_inc)
        a0 = np.zeros(n_a)

        # Prune if there is a collision
        for j in range(n_a):
            for k in range(n_inc):
                #
                pos = orbits_gt.orbits[j][k].data.pos_BP_P

                for m in range(len(pos)):
                    is_exterior = shape.check_exterior(pos[m, 0:3])
                    if not is_exterior:
                        orbits1[i].orbits[j][k].data.pos_err[m:len(pos)+1] = np.nan
                        orbits2[i].orbits[j][k].data.pos_err[m:len(pos)+1] = np.nan
                        #if i == 0:
                        #    orbits_gt.orbits[j][k].data.pos_BP_P[m:len(pos)+1, 0:3] = np.nan
                        break

        # Root mean square errors
        RMSE1 = np.zeros((n_a, n_inc))
        RMSE2 = np.zeros((n_a, n_inc))
        for j in range(n_a):
            for k in range(n_inc):
                # Get position errors
                pos_err1 = orbits1[i].orbits[j][k].data.pos_err
                pos_err2 = orbits2[i].orbits[j][k].data.pos_err
                RMSE1[j, k] = compute_RMSE(pos_err1)
                RMSE2[j, k] = compute_RMSE(pos_err2)
                #RMSE1[j, k] = orbits1[i].orbits[j][k].data.pos_err[-1]
                #RMSE2[j, k] = orbits2[i].orbits[j][k].data.pos_err[-1]

                # Inclinations
                inc0[k] = orbits1[i].orbits[j][k].oe[2]

            # Semi-major axes
            a0[j] = orbits1[i].orbits[j][0].oe[0]

        # Append results
        RMSE1_list.append(RMSE1)
        RMSE2_list.append(RMSE2)

    # Create grid of plots
    gs = gridspec.GridSpec(2, 2)
    ax = []
    fig = plt.figure(figsize=(10, 8))
    ax.append(plt.subplot(gs[0, 0]))
    ax.append(plt.subplot(gs[0, 1]))
    ax.append(plt.subplot(gs[1, 0]))
    ax.append(plt.subplot(gs[1, 1]))

    linestyle= ['-.', '-', '--']
    marker = ['^', '.', 's']
    markersize = [6, 10, 6]
    lines = []

    # Loop through plots
    for i in range(len(ax)):
        for j in range(len(RMSE1_list)):
            # Plots
            line, = ax[i].plot(inc0*rad2deg, RMSE1_list[j][i, :],
                               marker=marker[j], markersize=markersize[j], color=colors[0],
                               linestyle=linestyle[j], clip_on=False,
                               label='$n_M$=' + str(n_M[j]))
            ax[i].plot(inc0*rad2deg, RMSE2_list[j][i, :],
                       marker=marker[j], markersize=markersize[j], color=colors[1],
                       linestyle=linestyle[j], clip_on=False)
            dummy1, = ax[i].plot(np.nan, np.nan,
                                 color=colors[0], label='Mascon')
            dummy2, = ax[i].plot(np.nan, np.nan,
                                 color=colors[1], label='Mascon-PINN')
            if i == 0:
                lines.append(line)
                dummy = [dummy1, dummy2]

        # Fancyness
        ax[i].set_ylim(1e-2, 1e4)
        ax[i].grid()
        ax[i].set_yscale('log')
        ax[i].tick_params(axis='both', labelsize=font-5)
        ax[i].set_xlim(inc0[0]*rad2deg, inc0[-1]*rad2deg)
        ax[i].set_xticks((inc0*rad2deg).tolist())
        ax[i].set_title('$a_0$=' + str(int(a0[i]*m2km)) + ' km',
                        fontsize=font_map, pad=0)

    # Labels
    if model == 'poly':
        fig.suptitle('Constant density polyhedron', fontsize=font-5)
    elif model == 'polyheterogeneous':
        fig.suptitle('Heterogeneous polyhedron', fontsize=font-5)
    fig.supxlabel('$i_0$ [$^{\circ}$]', fontsize=font-5)
    fig.supylabel('Position RMSE [m]', fontsize=font-5)

    # Legend
    fig.legend(handles=lines, bbox_to_anchor=(0.97, 0.78),
               fontsize=font_legend)
    fig.legend(handles=dummy, bbox_to_anchor=(0.97, 0.37),
               fontsize=font_legend)
    fig.tight_layout()
    plt.savefig('Plots/RMSEorbits_' + model + '.pdf',
                format='pdf', bbox_inches='tight')


# This function computes RMSE
def compute_RMSE(err):
    # Compute RMSE
    RMSE = np.sqrt(np.nanmean(err**2))

    return RMSE


# Change working path
current_path = os.getcwd()
new_path = os.path.dirname(current_path)
os.chdir(new_path)

# Scenario
model = 'poly'
model = 'polyheterogeneous'
faces = '200700faces'

#asteroid = 'polyheterogeneous200700faces'
if model == 'poly':
    title = 'Constant density polyhedron'
elif model == 'polyheterogeneous':
    title = 'Heterogeneous polyhedron'

# Groundtruth orbits
file_gt = 'Results/eros/groundtruth/' + model + faces + '/propagation.pck'
orbits_gt = pck.load(open(file_gt, "rb"))
shape = orbits_gt.asteroid.shape
shape.create_shape()

# Number of masses
n_M = np.array([20,
                100,
                1000])
n_neurons = np.repeat(40, len(n_M))
file_path = 'Results/eros/results/' + model + faces + '/ideal/dense_alt50km_100000samples'

# Lists
mascon_list = []
pinn_list = []

# Loop through results
for i in range(len(n_M)):
    # Files
    file_mascon = file_path + '/mascon' + str(n_M[i]) \
                  + '_muxyz_quadratic_octantrand0_orbits.pck'
    file_pinn = file_path + '/pinn6x' + str(n_neurons[i]) \
                + 'SIREN_linear_mascon' + str(n_M[i]) + '_orbits.pck'

    # Scenarios
    orbits_mascon = pck.load(open(file_mascon, "rb"))
    orbits_pinn = pck.load(open(file_pinn, "rb"))

    # List of orbits
    mascon_list.append(orbits_mascon)
    pinn_list.append(orbits_pinn)

# Plots
plot_errors(mascon_list,
            pinn_list)
plot_orbits(orbits_gt)
plt.show()
