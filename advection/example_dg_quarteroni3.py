"""
Based on

Antonietti, P., & Quarteroni, A. (2013). Numerical performance of discontinuous and stabilized
    continuous Galerkin methods for convection–diffusion problems.
"""

from example_dg_common import *


def define(filename_mesh=None,
           approx_order=2,

           adflux=0,
           limit=False,

           cw=100,
           diffcoef=1,
           diffscheme="symmetric",

           cfl=None,
           dt=None,
           ):

    cfl = None
    dt = None

    functions = {}
    def local_register_function(fun):
        try:
            functions.update({fun.__name__: (fun,)})

        except AttributeError:  # Already a sfepy Function.
            fun = fun.function
            functions.update({fun.__name__: (fun,)})

        return fun
    example_name = "quart3"
    dim = 2

    if filename_mesh is None:
        filename_mesh = get_gen_block_mesh_hook((1., 1.), (20, 20), (.5, .5))

    velo = [1., 1.]

    angle = 0.0  # - nm.pi / 5
    rotm = nm.array([[nm.cos(angle), -nm.sin(angle)],
                     [nm.sin(angle), nm.cos(angle)]])
    velo = nm.sum(rotm.T * nm.array(velo), axis=-1)[:, None]


    regions = {
        'Omega'     : 'all',
        'left' : ('vertices in x == 0', 'edge'),
        'right': ('vertices in x == 1', 'edge'),
        'top' : ('vertices in y == 1', 'edge'),
        'bottom': ('vertices in y == 0', 'edge')
    }

    fields = {
        'f': ('real', 'scalar', 'Omega', str(approx_order) + 'd', 'DG', 'legendre')
    }

    variables = {
        'p': ('unknown field', 'f', 0),
        'v': ('test field', 'f', 'p'),
    }

    integrals = {
        'i': 2 * approx_order,
    }

    @local_register_function
    def bc_funs(ts, coors, bc, problem):
        # return 2*coors[..., 1]
        t = ts.dt*ts.step
        x_1 = coors[..., 0]
        x_2 = coors[..., 1]
        res = nm.zeros(nm.shape(x_1))

        sin = nm.sin
        cos = nm.cos
        exp = nm.exp
        pi = nm.pi
        arctan = nm.arctan
        sqrt = nm.sqrt

        eps = diffcoef

        if bc.diff == 0:
            if "left" in bc.name:
                res[:] = x_2 + (exp((x_2 - 1)/eps) - exp(-1/eps))/(exp(-1/eps) - 1)
            elif "right" in bc.name:
                res[:] = 0
            elif "bot" in bc.name:
                res[:] = x_1 + (exp((x_1 - 1)/eps) - exp(-1/eps))/(exp(-1/eps) - 1)
            elif "top" in bc.name:
                res[:] = 0

        elif bc.diff == 1:
            if "left" in bc.name:
                res = nm.stack((-x_2 - (x_2 - 1)*exp((x_2 - 1)/eps)/(eps*(exp(-1/eps) - 1)) + 1,
                                exp((x_2 - 1)/eps)/(eps*(exp(-1/eps) - 1)) + 1),
                               axis=-2)
            elif "right" in bc.name:
                res = nm.stack((-x_2 - (x_2 - 1)/(eps*(exp(-1/eps) - 1)) + 1,
                                res),
                               axis=-2)
            elif "bot" in bc.name:
                res = nm.stack((exp((x_1 - 1)/eps)/(eps*(exp(-1/eps) - 1)) + 1,
                                -x_1 - (x_1 - 1)*exp((x_1 - 1)/eps)/(eps*(exp(-1/eps) - 1)) + 1),
                               axis=-2)
            elif "top" in bc.name:
                res = nm.stack((res,
                                -x_1 - (x_1 - 1)/(eps*(exp(-1/eps) - 1)) + 1),
                               axis=-2)

        return res


    @local_register_function
    def source_fun(ts, coors, mode="qp", **kwargs):
        # t = ts.dt * ts.step
        eps = diffcoef
        sin = nm.sin
        cos = nm.cos
        exp = nm.exp
        sqrt = nm.sqrt
        pi = nm.pi
        if mode == "qp":
            x_1 = coors[..., 0]
            x_2 = coors[..., 1]
            res = -eps*((x_1 - 1)**2*exp(-(x_1 - 1)*(x_2 - 1)/eps)/(eps**2*(exp(-1/eps) - 1)) +
                        (x_2 - 1)**2*exp(-(x_1 - 1)*(x_2 - 1)/eps)/(eps**2*(exp(-1/eps) - 1))) \
                  - x_1 - x_2 - (x_1 - 1)*exp(-(x_1 - 1)*(x_2 - 1)/eps)/(eps*(exp(-1/eps) - 1)) - \
                  (x_2 - 1)*exp(-(x_1 - 1)*(x_2 - 1)/eps)/(eps*(exp(-1/eps) - 1)) + 2
            return {"val": res[..., None, None]}


    def analytic_sol(coors, t):
        x_1 = coors[..., 0]
        x_2 = coors[..., 1]
        sin = nm.sin
        pi = nm.pi
        exp = nm.exp
        eps = diffcoef
        res = -x_1*x_2 + x_1 + x_2 + (exp(-(x_1 - 1)*(x_2 - 1)/eps) - exp(-1/eps))/(exp(-1/eps) - 1)
        return res


    @local_register_function
    def sol_fun(ts, coors, mode="qp", **kwargs):
        t = ts.time
        if mode == "qp":
            return {"p": analytic_sol(coors, t)[..., None, None]}


    dgebcs = {
        'u_left' : ('left', {'p.all': "bc_funs", 'grad.p.all' : "bc_funs"}),
        'u_top'  : ('top', {'p.all': "bc_funs", 'grad.p.all' :  "bc_funs"}),
        'u_bot'  : ('bottom', {'p.all': "bc_funs", 'grad.p.all' :  "bc_funs"}),
        'u_right': ('right', {'p.all': "bc_funs", 'grad.p.all' :  "bc_funs"}),
    }

    materials = {
        'a'     : ({'val': [velo], '.flux': adflux},),
        'D'     : ({'val': [diffcoef], '.cw': cw},),
        'g'     : 'source_fun'
    }

    equations = {
        'balance': """
                    - dw_s_dot_mgrad_s.i.Omega(a.val, p, v)
                    + dw_dg_advect_laxfrie_flux.i.Omega(a.flux, a.val, v, p)
                   """
                   +
                   " + dw_laplace.i.Omega(D.val, v, p) " +
                   diffusion_schemes_implicit[diffscheme] +
                   " + dw_dg_interior_penalty.i.Omega(D.val, D.cw, v, p)" +
                   " - dw_volume_lvf.i.Omega(g.val, v) " +
                   "= 0"

    }

    solver_0 = {
        'name' : 'ls',
        'kind' : 'ls.scipy_direct',
    }

    solver_1 = {
        'name' : 'newton',
        'kind' : 'nls.newton',

        'i_max'      : 5,
        'eps_a'      : 1e-8,
        'eps_r'      : 1.0,
        'macheps'   : 1e-16,
        'lin_red'    : 1e-2,  # Linear system error < (eps_a * lin_red).
        'ls_red'     : 0.1,
        'ls_red_warp' : 0.001,
        'ls_on'      : 0.99999,
        'ls_min'     : 1e-5,
        'check'     : 0,
        'delta'     : 1e-6,
    }

    options = {
        'nls'             : 'newton',
        'ls'              : 'ls',
        'output_format'   : 'msh',
		'file_format'     : 'gmsh-dg',
    }

    return locals()

globals().update(define())
