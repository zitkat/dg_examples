"""
Based on

Krivodonova, L. (2007). Limiters for high-order discontinuous Galerkin methods.
Journal of Computational Physics, 226(1), 879–896.
https://doi.org/10.1016/j.jcp.2007.05.011
"""

from example_dg_common import *

mesh_center = (0, 0)
mesh_size = (2.0, 2.0)


import numpy as nm
dofs = 57600
orders = [1, 2, 3, 4]
ncells = [ dofs / (ord + 1)**2 for ord in orders ]
nnodes = [nm.sqrt(nc) + 1 for nc in ncells]

def define(filename_mesh=None,
           approx_order=2,

           adflux=0,
           limit=True,

           cw=None,
           diffcoef=None,
           diffscheme="symmetric",

           cfl=None,
           dt=1.,
           ):
    """
    NOTE in this example filename_mesh may instead contain int denoting number
    of nodes of tensor product mesh aldong one dimension
    """
    functions = {}

    def local_register_function(fun):
        try:
            functions.update({fun.__name__: (fun,)})

        except AttributeError:  # Already a sfepy Function.
            fun = fun.function
            functions.update({fun.__name__: (fun,)})

        return fun

    example_name = "adv__kriv_2D"
    dim = 2

    diffcoef = None
    cw = None

    nnodes = None
    try:
        nnodes = int(filename_mesh)
    except:
        pass


    if filename_mesh is None or nnodes is not None:
        filename_mesh = get_gen_block_mesh_hook((2., 2.), (nnodes, nnodes), (.0, .0))

    t0 = 0.
    t1 = 1.

    angle = 0
    rotm = nm.array([[nm.cos(angle), -nm.sin(angle)],
                     [nm.sin(angle), nm.cos(angle)]])
    velo = nm.sum(rotm.T * nm.array([3., 1.]), axis=-1)[:, None]

    @local_register_function
    def get_velocity(ts, coors, problem, equations=None, mode=None,
                         **kwargs):
        if mode == 'qp':
            x = coors[..., 0:1]
            y = coors[..., 1:]
            pi = nm.pi
            val = nm.stack((2*pi*y, 2*pi*x), axis=1)
            return {'val': val}


    materials = {
        'a': 'get_velocity',
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
        return get_ic(coors, ic=None)


    @local_register_function
    def sol_fun(ts, coors, mode="qp", **kwargs):
        t = ts.time
        if mode == "qp":
            return {"p": analytic_sol(coors, t)[..., None]}

    @local_register_function
    def get_ic(coors, ic=None):
        sin = nm.sin
        pi = nm.pi
        x = coors[..., 0:1]
        y = coors[..., 1:]

        square =  ((0.1 <= x) & (x <= 0.6)) * ((- 0.25 <= y) & (y <= 0.25))

        r = (x + .5)**2 + y**2
        circle = (nm.cos(2*pi*r)**2) * (r <= 0.25).astype(nm.float64)

        return square.astype(nm.float64) + circle

    ics = {
        'ic': ('Omega', {'p.0': 'get_ic'}),
    }

    dgebcs = {
        'u_left' : ('left', {'p.all': 0}),
        'u_right' : ('right', {'p.all': 0}),
        'u_bottom' : ('bottom', {'p.all': 0}),
        'u_top' : ('top', {'p.all': 0}),

    }

    integrals = {
        'i': 3 * approx_order,
    }

    equations = {
        'Advection': """
                       dw_volume_dot.i.Omega(v, p)
                       - dw_s_dot_mgrad_s.i.Omega(a.val, p[-1], v)
                       + dw_dg_advect_laxfrie_flux.i.Omega(a.val, v, p[-1]) = 0
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
