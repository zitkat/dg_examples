"""
Based on

Krivodonova, L. (2007). Limiters for high-order discontinuous Galerkin methods.
Journal of Computational Physics, 226(1), 879–896.
https://doi.org/10.1016/j.jcp.2007.05.011
"""

from example_dg_common import *

mesh_center = (0, 0)
mesh_size = (2.0, 2.0)

def define(filename_mesh=None,
           approx_order=2,

           adflux=0,
           limit=True,

           cw=None,
           diffcoef=None,
           diffscheme="symmetric",

           cfl=0.5,
           dt=None,
           ):

    example_name = "adv__kriv_2D"
    dim = 2

    diffcoef = None
    cw = None

    if filename_mesh is None:
        filename_mesh = get_gen_block_mesh_hook((2., 2.), (20, 20), (.0, .0))

    t0 = 0.
    t1 = 1.

    angle = 0
    rotm = nm.array([[nm.cos(angle), -nm.sin(angle)],
                     [nm.sin(angle), nm.cos(angle)]])
    velo = nm.sum(rotm.T * nm.array([3., 1.]), axis=-1)[:, None]
    materials = {
        'a': ({'val': [velo], '.flux': adflux},),
    }

    regions = {
        'Omega'     : 'all',
        'left': ('vertices in x == -1', 'edge'),
        'right': ('vertices in x == 1', 'edge'),
        'top': ('vertices in y == 1', 'edge'),
        'bottom': ('vertices in y == -1', 'edge')
    }

    fields = {
        'f': ('real', 'scalar', 'Omega', str(approx_order) + 'd', 'DG', 'legendre')  #
    }

    variables = {
        'p': ('unknown field', 'f', 0, 1),
        'v': ('test field', 'f', 'p'),
    }

    def analytic_sol(coors, t):
        x_1 = coors[..., 0]
        x_2 = coors[..., 1]
        sin = nm.sin
        pi = nm.pi
        exp = nm.exp
        res = sin(pi*(x_1 - 2 * x_2))
        return res


    @local_register_function
    def sol_fun(ts, coors, mode="qp", **kwargs):
        t = ts.time
        if mode == "qp":
            return {"p": analytic_sol(coors, t)[..., None, None]}

    def get_ic(x, ic=None):
        sin = nm.sin
        pi = nm.pi
        return sin(pi*(x[..., 0:1] - 2*x[..., 1:]))


    functions = {
        'get_ic': (get_ic,)
    }

    ics = {
        'ic': ('Omega', {'p.0': 'get_ic'}),
    }

    dgepbc_1 = {
        'name': 'u_rl',
        'region': ['right', 'left'],
        'dofs': {'p.all': 'p.all'},
        'match': 'match_y_line',
    }

    dgepbc_2 = {
        'name': 'u_tb',
        'region': ['top', 'bottom'],
        'dofs': {'p.all': 'p.all'},
        'match': 'match_y_line',
    }

    integrals = {
        'i': 3 * approx_order,
    }

    equations = {
        'Advection': """
                       dw_volume_dot.i.Omega(v, p)
                       - dw_s_dot_mgrad_s.i.Omega(a.val, p[-1], v)
                       + dw_dg_advect_laxfrie_flux.i.Omega(a.flux, a.val, v, p[-1]) = 0
                      """
    }

    solvers = {
        "tss": ('ts.tvd_runge_kutta_3',
                {"t0"     : t0,
                 "t1"     : t1,
                 'limiters': {"f": MomentLimiter2D} if limit else {},
                 'verbose': False}),
        'nls': ('nls.newton',{}),
        'ls' : ('ls.scipy_direct', {})
    }

    options = {
        'ts'              : 'tss',
        'nls'             : 'newton',
        'ls'              : 'ls',
        'save_times'      : 100,
        'active_only'     : False,
        'output_format'   : 'msh',
        'file_format'     : 'gmsh-dg',
        'pre_process_hook': get_cfl_setup(cfl) if dt is None else get_cfl_setup(dt=dt)
    }

    return locals()


globals().update(define())
