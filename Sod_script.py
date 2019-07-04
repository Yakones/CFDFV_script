#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import numpy as np
import matplotlib.pyplot as plt


###############################################################################
# USER Input
n = 500  # spacing
simulation = 'Sod.ini'

###############################################################################
variables = ['rho', 'v1', 'v2', 'p']
error_variables = ['L_1', 'L_2', 'L_inf']


def main():
    """
    Main file
    """
    cfl_logspace = np.logspace(-2, 2, n)  # (log_min,log_max,stuetzstellen)
    L_2_rho = []
    times = []
    for cfl in cfl_logspace:
        try:
            print('Excplicit, CFL = %s' % cfl)
            [error, time] = loop_exp(simulation, cfl, 1)
            times.append(time)
            L_2_rho.append(error['L_2']['rho'])
        except IndexError:
            print('Not Converged at CFL= %s' % cfl)
            cfl_logspace = cfl_logspace[cfl_logspace != cfl]
    plt.loglog(cfl_logspace, L_2_rho, basex=10, marker='x')
    plt.xticks(np.linspace(0.01, 10, 20))
    plt.yticks(np.linspace(0.02, 0.06, 10))
    plt.xlabel('CFL')
    plt.ylabel('L_2 rho')
    plt.grid(True)


    print(80*'#')
    cfl_logspace = np.logspace(-2, 2, n)
    L_2_rho = []
    times = []
    for cfl in cfl_logspace:
        try:
            print('Implicit, CFL = %s' % cfl)
            [error, time] = loop_imp(simulation, cfl, 1)
            times.append(time)
            L_2_rho.append(error['L_2']['rho'])
        except IndexError:
            print('Not Converged at CFL= %s' % cfl)
            cfl_logspace = cfl_logspace[cfl_logspace != cfl]

    plt.loglog(cfl_logspace, L_2_rho, basex=10, marker='x')
    plt.show()


def loop_exp(simulation, cfl, n):
    """
    Set cfl for simulation and start run function n times
    """
    set_cfl(simulation, cfl)
    for _ in range(n):
        errors = []
        times = []
        (time, error) = run_exp(simulation)
        times.append(float(time))
        errors.append(error)
    avg_error = {}
    for category in error:
        avg_error[category] = {}
        for variable in error[category]:
            avg_error[category][variable] = avg(errors, variable, category)
    return [avg_error, sum(times)/len(times)]


def loop_imp(simulation, cfl, n):
    """
    Set cfl for simulation and start run function n times
    """
    set_cfl(simulation, cfl)
    for _ in range(n):
        errors = []
        times = []
        (time, error) = run_imp(simulation)
        times.append(float(time))
        errors.append(error)
    avg_error = {}
    for category in error:
        avg_error[category] = {}
        for variable in error[category]:
            avg_error[category][variable] = avg(errors, variable, category)
    return [avg_error, sum(times)/len(times)]


def run_exp(simulation):
    """
    Run explicit simulation in subprocess and return computation time and resiudals
    """
    set_implicit(False)
    # Run Simulation
    output = subprocess.check_output(
       ['/home/dominik/Documents/CFDFV/bin/cfdfv',
        simulation])
    # Evaluate Simulation
    error = {}
    lines = output.decode('utf-8').split('\n')
    computation_time = lines[-3].split(' ')[-2]
    for i in range(1, len(error_variables)+1):
        error[error_variables[i-1]] = {}
        for j in range(len(variables)):
            error[error_variables[i-1]][variables[j]] = \
                float(lines[-8+i].split('   ')[-4+j])
    return [computation_time, error]


def run_imp(simulation):
    """
    Run implicit simulation in subprocess and return computation time and resiudals
    """
    set_implicit(True)
    # Run Simulation
    output = subprocess.check_output(
       ['/home/dominik/Documents/CFDFV/bin/cfdfv',
        simulation])
    # Evaluate Simulation
    error = {}
    lines = output.decode('utf-8').split('\n')
    computation_time = lines[-5].split(' ')[-2]
    for i in range(1, len(error_variables)+1):
        error[error_variables[i-1]] = {}
        for j in range(len(variables)):
            error[error_variables[i-1]][variables[j]] = \
                float(lines[-10+i].split('   ')[-4+j])
    return [computation_time, error]


def avg(errors, variable, category):
    """
    create specific average for error category(L1,L2...)
    and varriable(rho,v_1,_v2...) from error dict
    """
    sum = 0
    for each in errors:
        sum += each[category][variable]
    return sum / len(errors)


def set_implicit(implicit):
    """
    change time intefration scheme in cfdfv input file
    """
    with open('./%s' % simulation, 'r') as file:
        lines = file.readlines()
    with open('./%s' % simulation, 'w') as file:
        for line in lines:
            if line.startswith('implicit='):
                if implicit:
                    file.write('implicit=T\n')
                else:
                    file.write('implicit=F\n')
            else:
                file.write(line)


def set_cfl(simulation, cfl):
    """
    change CFL value in cfdfv input file
    """
    with open('./%s' % simulation, 'r') as file:
        lines = file.readlines()
    with open('./%s' % simulation, 'w') as file:
        for line in lines:
            if line.startswith('CFL'):
                file.write('CFL=%s\n'
                           % cfl)
            else:
                file.write(line)


main()
