import matplotlib.pyplot as plt
import numpy as np
import pickle as pck
import os

from Basilisk.simulation import gravityEffector

from src.orbiters.spacecraft import Spacecraft
from plots.plots_orbits import plot_orb

# Import current directory
current_dir = os.getcwd()

# Conversion constants
km2m = 1e3


# This function defines a configuration dict
def configuration():
    # Orbits configuration
    config_orb = {
        'oe': {'a': np.linspace(28, 46, 4) * 1e3,
               'ecc': 0,
               'inc': np.array([0, 45, 90, 135, 180]) * np.pi/180,
               'omega': 48.2 * np.pi / 180,
               'RAAN': 347.8 * np.pi / 180,
               'f': 85.3 * np.pi / 180},
        'tf': 24 * 3600}

    # Groundtruth configuration
    config_gt = {'file': '',
                 'asteroid_name': 'eros',  # 'eros'
                 'grav_model': 'poly',  # 'poly'
                 'file_poly': current_dir + '/Polyhedron_files/eros/'
                              + 'eros007790.tab',
                 'mascon': {'add': False,
                            'mu_M': np.array([0.1,
                                              -0.1]) * 4.46275472004 * 1e5,
                            'xyz_M': np.array([[10, 0, 0],
                                               [-10, 0, 0]]) * 1e3},
                 'dt_sample': 60}

    # Gravity regression configuration
    config_regression = {'file': 'mascon100_muxyz_quadratic_octantrand0',
                         'model_path': '/ideal/dense_alt50km_100000samples/'}

    return config_orb, config_gt, config_regression


# Sets groundtruth file
def set_filegroundtruth(config_gt):
    # Set asteroid name and groundtruth gravity
    asteroid_name = config_gt['asteroid_name']

    # Create asteroid folder if it does not exist
    path_asteroid = 'Results/' + asteroid_name
    exist = os.path.exists(path_asteroid)
    if not exist:
        os.makedirs(path_asteroid)

    # Retrieve groundtruth parameters
    grav_gt = config_gt['grav_model']
    if config_gt['mascon']['add']:
        grav_gt += 'heterogeneous'

    # Obtain number of faces
    _, _, _, n_face = \
        gravityEffector.loadPolyFromFileToList(config_gt['file_poly'])
    config_gt['n_face'] = n_face

    # Create ground truth path if it does not exist and define ground truth file
    path = path_asteroid + '/groundtruth/' + grav_gt + str(n_face) + 'faces'
    exist = os.path.exists(path)
    if not exist:
        os.makedirs(path)
    file = path + '/propagation.pck'

    return file


# Sets results file
def set_fileresults(config_gt, config_regression):
    # Set asteroid name and groundtruth gravity
    asteroid_name = config_gt['asteroid_name']

    # Create asteroid folder if it does not exist
    path_asteroid = current_dir + '/Results/' + asteroid_name
    exist = os.path.exists(path_asteroid)
    if not exist:
        os.makedirs(path_asteroid)

    # Retrieve groundtruth parameters
    grav_gt = config_gt['grav_model']
    if config_gt['mascon']['add']:
        grav_gt += 'heterogeneous'

    # Obtain number of faces
    _, _, _, n_face = \
        gravityEffector.loadPolyFromFileToList(config_gt['file_poly'])
    config_gt['n_face'] = n_face

    # Set results file
    path = path_asteroid + '/regression/' + grav_gt + str(n_face) + 'faces'
    file = path + config_regression['model_path'] \
           + config_regression['file'] + '_orbits.pck'
    file_model = path + config_regression['model_path'] \
                 + config_regression['file'] + '.pck'

    return file, file_model


# This function launches orbital propagation
def launch_propagation(config_orb, config_gt, config_regression):
    # Number of semi-major axes and
    # orbital inclinations
    n_a = len(config_orb['oe']['a'])
    n_inc = len(config_orb['oe']['inc'])

    # Retrieve propagation time
    tf = config_orb['tf']

    # Files
    file, file_model = set_fileresults(config_gt, config_regression)

    # Create asteroid from a previously regressed model
    _, grav_optimized = pck.load(open(file_model, "rb"))
    asteroid = grav_optimized.asteroid
    asteroid.shape.create_shape()

    # Create a 2D list to store spacecraft objects
    sc_orbits = [[Spacecraft(grav_body=asteroid) for _ in range(n_inc)] for _ in range(n_a)]

    # Prepare initial orbital element
    oe0 = np.array([np.nan,
                    config_orb['oe']['ecc'],
                    np.nan,
                    config_orb['oe']['omega'],
                    config_orb['oe']['RAAN'],
                    config_orb['oe']['f']])

    # Propagation loop
    for i in range(n_a):
        # Change semi-major axis
        oe0[0] = config_orb['oe']['a'][i]

        for j in range(n_inc):
            # Change inclination
            oe0[2] = config_orb['oe']['inc'][j]

            # Propagate
            sc_orbits[i][j].propagate(oe0, tf)

    # Delete swigpy
    for i in range(n_a):
        for j in range(n_inc):
            # Delete swigpy
            sc_orbits[i][j].grav_body.delete_swigpy()

    # Save file
    with open(file, "wb") as f:
        pck.dump(sc_orbits, f)

    return sc_orbits


if __name__ == "__main__":
    # Obtain configuration dict
    config_orb, config_gt, config_regression = configuration()

    # Launch orbital propagation
    sc_orbits = launch_propagation(config_orb, config_gt, config_regression)

    # Plot orbits
    plot_orb(sc_orbits)
    plt.show()
