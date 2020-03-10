from controls import PIDPhi
from simulation import simulate
from scipy.optimize import minimize
from bikemodel import MeijaardModel
import metrics
import numpy as np


def optimize(intial_val, vel, tspan, intial_constants, c_robust, c_response, max_torque, max_response, min_robust):
    def func(x):
        return simulate(MeijaardModel(), intial_val, tspan, vel, PIDPhi(k_p=x[0], k_i=x[1], k_d=x[2]), None)

    def time(x):
        results = func(x)
        con = metrics.settling_time(results['t'], results['phi'], 0)
        return con

    def robust(x):
        results = metrics.robustness(intial_val, vel, MeijaardModel(), PIDPhi(k_p=x[0], k_i=x[1], k_d=x[2]))
        con = results['phi']
        return con

    def con_torque(x):
        results = func(x)
        range_torque = []
        controller = PIDPhi(k_p=x[0], k_i=x[1], k_d=x[2])
        for i in range(0, np.size(results['phi'])-1):
            e = [results['phi'][i], results['delta'][i], results['dphi'][i], results['ddelta'][i]]
            temp = controller.get_control(goals=None)(t=results['t'][i], e=e, v=vel)
            range_torque.append(temp)

        con = max(range_torque) - max_torque
        return con

    def objective(x):
        time_obj = (time(x) - max_response) ** 2
        robust_obj = (robust(x) - min_robust) ** 2
        return c_response * time_obj + c_robust * robust_obj

    cons = {'type': 'ineq', 'fun': con_torque}

    res = minimize(objective, intial_constants, constraints=cons)
    print(res.success)
    return res.x


if __name__ == '__main__':
    test = optimize(intial_val=[10, 0, 0, 0], vel=6, tspan=60, intial_constants=[5, .00000001, 0], c_robust=1, c_response=1,
             max_torque=20, max_response=10, min_robust=10)
    print(test)
