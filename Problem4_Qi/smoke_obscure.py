"""
Simulate smoke cloud obscuration of a cylindrical target.

- Assumptions made (explicit):
- Missile M1 starts at (20000, 0, 2000) and flies toward the cylindrical target center at (0, 200, 0) at 300 m/s.
- Drone FY1 starts at (17800, 0, 1800) and flies toward the decoy target at (0, 0, 1800) at 120 m/s.
- Drone releases a smoke bomb at t_release = 1.5 s. The bomb detonates 3.6 s after release (t_det = 5.1 s).
- After release the bomb's x,y follow the drone's x,y (same horizontal motion). Its z-motion is under gravity with initial vertical velocity equal to the drone's vertical velocity at release.
- At detonation the smoke cloud appears as a sphere of radius 10 m centered at the detonation point; it then sinks at 3 m/s (no horizontal displacement). The cloud expires 20 s after detonation.
- The cloud obscures the target when every sampled point on the cylinder surface is occluded (the line segment from the missile to that point intersects the smoke sphere).
- We sample the cylinder surface (theta, z) to decide visibility (72 azimuth samples, 21 height samples).

Outputs: printed intervals (start, end) when the cloud fully obscures M1, and the total obscuration duration in seconds.

Note: parameters (missile speed, sampling density) can be adjusted below.
"""

import math
import time
import numpy as np


def norm(v):
    return math.sqrt(np.dot(v, v))


def line_segment_intersects_sphere(A, B, C, r):
    # returns True if segment AB intersects sphere(center C, radius r)
    AB = B - A
    AC = C - A
    ab2 = np.dot(AB, AB)
    if ab2 == 0:
        return np.dot(A - C, A - C) <= r * r
    t = float(np.dot(AC, AB) / ab2)
    t_clamped = max(0.0, min(1.0, t))
    closest = A + t_clamped * AB
    return np.dot(closest - C, closest - C) <= r * r


def simulate(
    missile_start=np.array([20000.0, 0.0, 2000.0]),
    missile_speed=300.0,
    drone_start=np.array([17800.0, 0.0, 1800.0]),
    # drone target (decoy) at (0, 0, 1800)
    decoy=np.array([0.0, 0.0, 1800.0]),
    drone_speed=120.0,
    t_release=1.5,
    dt_det_after_release=3.6,
    cloud_radius=10.0,
    cloud_sink_speed=3.0,
    cloud_lifetime=20.0,
    # optional continuous verification / AUC helpers
    enable_continuous_verification=False,
    continuous_pct_threshold=99.5,
    continuous_theta_resolution=720,
    continuous_tol_z=0.01,
    continuous_max_depth=12,
    g=9.81,
    # finer spatial and temporal sampling for higher accuracy
    sample_theta=180,
    sample_z=41,
    # finer time resolution (s) for calculation
    dt=0.001,
    # verbose progress printing for long runs
    verbose=False,
    # optional path to write progress heartbeats (text file updated periodically)
    progress_path=None,
):
    # compute drone velocity vector (constant)
    dir_drone = decoy - drone_start
    dist_drone = np.linalg.norm(dir_drone)
    v_drone = (dir_drone / dist_drone) * drone_speed

    # drone position function
    def drone_pos(t):
        return drone_start + v_drone * t

    # release and detonation times
    t_release = float(t_release)
    t_det = t_release + float(dt_det_after_release)
    cloud_end = t_det + cloud_lifetime

    # drone velocity components
    v_drone_z = v_drone[2]

    # bomb motion: x,y follow drone's x,y; z follows projectile motion from release
    pos_release = drone_pos(t_release)
    z_release = pos_release[2]

    def bomb_pos(t):
        # valid for t >= t_release
        dtb = t - t_release
        x = drone_start[0] + v_drone[0] * t
        y = drone_start[1] + v_drone[1] * t
        z = z_release + v_drone_z * dtb - 0.5 * g * dtb * dtb
        return np.array([x, y, z])

    # detonation position at t_det
    pos_det = bomb_pos(t_det)

    # cylinder center placed on y=0 plane (target at ground level)
    cyl_center = np.array([0.0, 200.0, 0.0])
    cyl_radius = 7.0
    cyl_height = 10.0

    # missile motion: fly straight to the false target at the origin (0,0,0).
    # The real cylinder (the line-of-sight we want to block) remains at cyl_center.
    false_target = np.array([0.0, 0.0, 0.0])
    dir_missile = false_target - missile_start
    dist_missile = np.linalg.norm(dir_missile)
    # guard against zero distance
    if dist_missile == 0:
        v_missile = np.zeros_like(dir_missile)
        t_missile_arrival = 0.0
    else:
        v_missile = (dir_missile / dist_missile) * missile_speed
        t_missile_arrival = dist_missile / missile_speed

    def missile_pos(t):
        t_clamped = min(float(t), float(t_missile_arrival))
        return missile_start + v_missile * t_clamped

    # sample points on cylinder surface (angles and heights)
    thetas = np.linspace(0.0, 2 * math.pi, sample_theta, endpoint=False)
    zs = np.linspace(0.0, cyl_height, sample_z)
    sample_points = []
    for z in zs:
        for th in thetas:
            x = cyl_center[0] + cyl_radius * math.cos(th)
            y = cyl_center[1] + cyl_radius * math.sin(th)
            sample_points.append(np.array([x, y, z]))
    sample_points = np.array(sample_points)

    # simulate over cloud existence interval with step dt
    times = np.arange(t_det, cloud_end + dt / 2, dt)
    obscured_flags = []
    pct_sampled_obscured = []
    # matrix times x points: True if that sampled point is obscured at that time
    obsc_matrix = np.zeros((len(times), len(sample_points)), dtype=bool)

    total_steps = len(times)
    if verbose:
        t0 = time.perf_counter()
        report_every = max(1, total_steps // 100)  # report ~every 1% of progress
        print(f"simulate: starting simulation from t={times[0]:.3f}s to {times[-1]:.3f}s, dt={dt}, steps={total_steps}", flush=True)
        print(f"  detonation at t={t_det:.3f}s, detonation position {pos_det}", flush=True)
        # make behavior explicit for users: the spherical smoke cloud does not exist
        # before detonation; it is generated at t_det and then sinks and may block LOS.
        print("  Note: the smoke sphere is generated at detonation time (t >= t_det). Before t_det there is no smoke to block the view.", flush=True)
        # missile target info (helpful when debugging where the missile is aimed)
        try:
            print(f"  missile_target(cyl_center)={cyl_center} dist_to_target={dist_missile:.3f}m t_missile_arrival={t_missile_arrival:.3f}s", flush=True)
        except Exception:
            # variables may not be available in some call paths; ignore silently
            pass
        if progress_path is not None:
            try:
                with open(progress_path, 'w') as f:
                    f.write('start\n')
            except Exception:
                # don't fail simulation due to progress file issues
                pass
    for ti, t in enumerate(times):
        # cloud center at time t
        dt_since_det = t - t_det
        center = pos_det.copy()
        center[2] = pos_det[2] - cloud_sink_speed * dt_since_det

        missile = missile_pos(t)

        # check visibility for each sampled point: if line missile->point intersects sphere
        intersects = [line_segment_intersects_sphere(missile, p, center, cloud_radius) for p in sample_points]
        # percent of sampled points obscured at this time
        pct = 100.0 * sum(intersects) / len(intersects) if len(intersects) > 0 else 0.0
        pct_sampled_obscured.append(pct)
        # if all True, then entire sampled cylinder is obscured
        fully_obscured = all(intersects)
        obscured_flags.append(bool(fully_obscured))
        obsc_matrix[ti, :] = intersects
        if verbose and ((ti % report_every) == 0 or ti == total_steps - 1):
            elapsed = time.perf_counter() - t0
            frac = (ti + 1) / total_steps
            eta = (elapsed / frac) * (1 - frac) if frac > 0 else float('inf')
            msg = f"simulate: t={t:.3f}s ({ti+1}/{total_steps})  sampled pct obscured={pct:.2f}%  elapsed={elapsed:.1f}s  ETA={eta:.1f}s"
            print(msg, flush=True)
            if progress_path is not None:
                try:
                    with open(progress_path, 'a') as f:
                        f.write(msg + '\n')
                except Exception:
                    pass

    # find contiguous intervals where obscured_flags True
    intervals = []
    cur_start = None
    for i, flag in enumerate(obscured_flags):
        t = times[i]
        if flag and cur_start is None:
            cur_start = t
        if not flag and cur_start is not None:
            intervals.append((cur_start, times[i-1] + dt))
            cur_start = None
    if cur_start is not None:
        intervals.append((cur_start, times[-1] + dt))

    # total duration
    total = sum(max(0.0, b - a) for a, b in intervals)

    # area-under-curve (seconds of equivalent full coverage) — smoother objective
    auc_seconds = float(np.trapz(np.array(pct_sampled_obscured) / 100.0, times)) if len(times) > 1 else 0.0

    # optional expensive continuous verification using theta_fully_obscured
    total_continuous = None
    continuous_intervals = None
    if enable_continuous_verification:
        # helper to reuse missile motion and detonation center
        missile_start_local = missile_start
        v_missile_local = v_missile
        t_missile_arrival_local = t_missile_arrival
        pos_det_local = pos_det
        cloud_sink_speed_local = cloud_sink_speed

        def missile_pos_local(t):
            t_clamped = min(float(t), float(t_missile_arrival_local))
            return missile_start_local + v_missile_local * t_clamped

        def theta_fully_obscured(theta, t, tol_z=continuous_tol_z, max_depth=continuous_max_depth):
            x0 = cyl_center[0] + cyl_radius * math.cos(theta)
            y0 = cyl_center[1] + cyl_radius * math.sin(theta)

            missile = missile_pos_local(t)
            dt_since_det = t - t_det
            center = pos_det_local.copy()
            center[2] = pos_det_local[2] - cloud_sink_speed_local * dt_since_det

            def visible_at_z(z):
                p = np.array([x0, y0, z])
                return not line_segment_intersects_sphere(missile, p, center, cloud_radius)

            def recurse(z_lo, z_hi, depth):
                if depth > max_depth or (z_hi - z_lo) <= tol_z:
                    return visible_at_z(0.5 * (z_lo + z_hi))
                if visible_at_z(z_lo) or visible_at_z(z_hi):
                    return True
                zm = 0.5 * (z_lo + z_hi)
                if visible_at_z(zm):
                    return True
                return recurse(z_lo, zm, depth + 1) or recurse(zm, z_hi, depth + 1)

            return not recurse(0.0, cyl_height, 0)

        # determine times where continuous full-obscuration holds
        continuous_flags = np.zeros(len(times), dtype=bool)
        candidate_indices = [i for i, pct in enumerate(pct_sampled_obscured) if pct >= continuous_pct_threshold]
        if candidate_indices:
            thetas = np.linspace(0.0, 2 * math.pi, continuous_theta_resolution, endpoint=False)
            for i in candidate_indices:
                t = times[i]
                all_theta_ok = True
                for th in thetas:
                    if not theta_fully_obscured(th, t, tol_z=continuous_tol_z, max_depth=continuous_max_depth):
                        all_theta_ok = False
                        break
                continuous_flags[i] = all_theta_ok

        # extract contiguous continuous intervals
        continuous_intervals = []
        cur_start = None
        for i, flag in enumerate(continuous_flags):
            t = times[i]
            if flag and cur_start is None:
                cur_start = t
            if not flag and cur_start is not None:
                continuous_intervals.append((cur_start, times[i-1] + dt))
                cur_start = None
        if cur_start is not None:
            continuous_intervals.append((cur_start, times[-1] + dt))
        total_continuous = sum(max(0.0, b - a) for a, b in continuous_intervals)

    return {
        't_release': t_release,
        't_det': t_det,
        'pos_det': pos_det,
        'cloud_end': cloud_end,
        'intervals': intervals,
        'total_duration': total,
        'total_duration_sampled': total,
        'auc_seconds': auc_seconds,
        'total_duration_continuous': total_continuous,
        'continuous_intervals': continuous_intervals,
        'times': times,
    'flags': obscured_flags,
    'pct_sampled_obscured': np.array(pct_sampled_obscured),
    'sample_points': sample_points,
    'obsc_matrix': obsc_matrix,
    'v_missile': v_missile,
    't_missile_arrival': t_missile_arrival,
    'dt': dt,
    # return key parameters for external verification
    'missile_start': missile_start,
    'cloud_sink_speed': cloud_sink_speed,
    'cloud_radius': cloud_radius,
    'cyl_center': cyl_center,
    'cyl_radius': cyl_radius,
    'cyl_height': cyl_height,
    }




if __name__ == '__main__':
    res = simulate()
    print('Release time:', res['t_release'])
    print('Detonation time:', res['t_det'])
    print('Detonation position:', res['pos_det'])
    print('Cloud end:', res['cloud_end'])
    print('Obscuration intervals (s):')
    for a, b in res['intervals']:
        print(f'  {a:.3f} -> {b:.3f} (duration {b-a:.3f}s)')
    print('Total obscuration duration (s):', res['total_duration'])

    # --- Adaptive verification: ensure we didn't miss narrow visible gaps ---
    # Use values returned by simulate() for consistency
    pct_arr = res['pct_sampled_obscured']
    sample_points = res['sample_points']
    missile_start = res['missile_start']
    v_missile = res['v_missile']
    t_missile_arrival = res['t_missile_arrival']
    pos_det = res['pos_det']
    cloud_sink_speed = res['cloud_sink_speed']
    cloud_radius = res['cloud_radius']
    cyl_center = res['cyl_center']
    cyl_radius = res['cyl_radius']
    cyl_height = res['cyl_height']

    def missile_pos_local(t):
        t_clamped = min(t, t_missile_arrival)
        return missile_start + v_missile * t_clamped

    def theta_fully_obscured(theta, t, tol_z=0.01, max_depth=12):
        x0 = cyl_center[0] + cyl_radius * math.cos(theta)
        y0 = cyl_center[1] + cyl_radius * math.sin(theta)

        missile = missile_pos_local(t)
        dt_since_det = t - res['t_det']
        center = pos_det.copy()
        center[2] = pos_det[2] - cloud_sink_speed * dt_since_det

        def visible_at_z(z):
            p = np.array([x0, y0, z])
            return not line_segment_intersects_sphere(missile, p, center, cloud_radius)

        def recurse(z_lo, z_hi, depth):
            if depth > max_depth or (z_hi - z_lo) <= tol_z:
                return visible_at_z(0.5 * (z_lo + z_hi))
            if visible_at_z(z_lo) or visible_at_z(z_hi):
                return True
            zm = 0.5 * (z_lo + z_hi)
            if visible_at_z(zm):
                return True
            return recurse(z_lo, zm, depth + 1) or recurse(zm, z_hi, depth + 1)

        return not recurse(0.0, cyl_height, 0)

    print('\nRunning adaptive verification across times...')
    any_full = False
    max_pct = 0.0
    for i, t in enumerate(res['times']):
        pct = pct_arr[i]
        if pct > max_pct:
            max_pct = pct
        # trigger adaptive continuous check when sampled coverage is very high
        if pct > 99.5:
            thetas = np.linspace(0.0, 2 * math.pi, 720, endpoint=False)
            all_theta_ok = True
            for th in thetas:
                if not theta_fully_obscured(th, t, tol_z=0.0025, max_depth=16):
                    all_theta_ok = False
                    break
            if all_theta_ok:
                print(f'Adaptive verification: full cylinder obscured at t={t:.4f}s')
                any_full = True
                break

    if not any_full:
        print('Adaptive verification found no time with full continuous obscuration (within tolerances).')
    print(f'Max percent of sampled points obscured over simulation: {max_pct:.3f}%')
