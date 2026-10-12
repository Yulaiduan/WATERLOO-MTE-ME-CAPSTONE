"""Integrate an experimental angular ODE with unilateral inelastic stops.

Invoke integrate(evaluate, inertia, times_s, initial_state, bounds_rad).
Inputs: SI angle/speed and work/dissipation states; positive scalar inertia.
Outputs: sampled states, cumulative impact loss (J), impact times (s).
Uses SciPy dense integration/events. A held stop releases only when free
acceleration points inward; no position controller or damping is added.
Limits: rigid zero-restitution stops, fixed-J1 angular model, no floor contact.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


def integrate(evaluate, inertia, times, initial, bounds):
    lo, hi = bounds
    states = np.zeros((len(initial), len(times)))
    losses = np.zeros(len(times))
    y = np.asarray(initial, dtype=float)
    t, index, loss = float(times[0]), 0, 0.
    end = float(times[-1])
    dt = float(times[1] - times[0])
    impacts = []

    def sample(until, value, include_end=False):
        nonlocal index
        while index < len(times) and (times[index] < until - 1e-12 or include_end and times[index] <= until + 1e-12):
            states[:, index] = value(float(times[index]))
            losses[index] = loss
            index += 1

    def lower(time, state):
        distance=state[0]-lo
        if abs(distance)<1e-10 and state[1]>=-1e-10 and evaluate(time,state)[1]>=-1e-10:return 1e-12
        return distance
    def upper(time, state):
        distance=hi-state[0]
        if abs(distance)<1e-10 and state[1]<=1e-10 and evaluate(time,state)[1]<=1e-10:return 1e-12
        return distance
    lower.terminal = upper.terminal = True
    lower.direction = upper.direction = -1

    for _ in range(200):
        at_lower = abs(y[0] - lo) < 1e-10 and abs(y[1]) < 1e-10
        at_upper = abs(y[0] - hi) < 1e-10 and abs(y[1]) < 1e-10
        if at_lower or at_upper:
            inward = 1 if at_lower else -1
            acceleration = lambda time: inward * evaluate(time, y)[1]
            if acceleration(t) <= 1e-10:
                # During rest only the explicit time-dependent input changes.
                release = None
                previous = t
                for future in np.r_[np.arange(t + dt, end, dt), end]:
                    future = min(float(future), end)
                    if acceleration(future) > 1e-10:
                        release = brentq(acceleration, previous, future, xtol=1e-13)
                        break
                    previous = future
                if release is None:
                    sample(end, lambda time: y, True)
                    return states, losses, impacts
                sample(release, lambda time: y)
                t = release
        solution = solve_ivp(evaluate, (t, end), y, dense_output=True,
                             events=(lower, upper), max_step=dt,
                             rtol=2e-8, atol=1e-10)
        if not solution.success:
            raise ValueError(solution.message)
        reached = float(solution.t[-1])
        if solution.status != 1:
            sample(end, solution.sol, True)
            return states, losses, impacts
        sample(reached, solution.sol)
        y = solution.y[:, -1].copy()
        y[0] = lo if len(solution.t_events[0]) else hi
        loss += .5 * inertia(y[0]) * y[1] ** 2
        impacts.append(reached)
        y[1] = 0.
        if reached >= end - 1e-12:
            sample(end, lambda time: y, True)
            return states, losses, impacts
        t = reached
    raise ValueError('Too many angular stop events; reduce the input or timestep.')
