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

    example_name = "quart2"
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
        'u': ('unknown field', 'f', 0),
        'v': ('test field', 'f', 'u'),
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
                res[:] = -arctan(1/16*(4*(2*x_2 - 1)**2 + 3)/sqrt(eps))
            elif "right" in bc.name:
                res[:] = -arctan(1/16*(4*(2*x_2 - 1)**2 + 3)/sqrt(eps))
            elif "bot" in bc.name:
                res[:] = -arctan(1/16*(4*(2*x_1 - 1)**2 + 3)/sqrt(eps))
            elif "top" in bc.name:
                res[:] = -arctan(1/16*(4*(2*x_1 - 1)**2 + 3)/sqrt(eps))

        elif bc.diff == 1:
            if "left" in bc.name:
                res = nm.stack((256/(((4*(2*x_2 - 1)**2 + 3)**2/eps + 256)*sqrt(eps)),
                                -256*(2*x_2 - 1)/(((4*(2*x_2 - 1)**2 + 3)**2/eps + 256)*sqrt(eps))),
                               axis=-2)
            elif "right" in bc.name:
                res = nm.stack((-256/(((4*(2*x_2 - 1)**2 + 3)**2/eps + 256)*sqrt(eps)),
                                -256*(2*x_2 - 1)/(((4*(2*x_2 - 1)**2 + 3)**2/eps + 256)*sqrt(eps))),
                               axis=-2)
            elif "bot" in bc.name:
                res = nm.stack(((-256*(2*x_1 - 1)/(((4*(2*x_1 - 1)**2 + 3)**2/eps + 256)*sqrt(eps)),
                                 256/(((4*(2*x_1 - 1)**2 + 3)**2/eps + 256)*sqrt(eps)))),
                               axis=-2)
            elif "top" in bc.name:
                res = nm.stack(((-256*(2*x_1 - 1)/(((4*(2*x_1 - 1)**2 + 3)**2/eps + 256)*sqrt(eps)),
                                 -256/(((4*(2*x_1 - 1)**2 + 3)**2/eps + 256)*sqrt(eps)))),
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
            res = (-1024 * eps * (8 * (4 * (2 * x_1 - 1) ** 2 +
                                       4 * (2 * x_2 - 1) ** 2 - 1) * (2 * x_1 - 1) ** 2 /
                                  (((4 * (2 * x_1 - 1) ** 2 + 4 * (2 * x_2 - 1) ** 2 - 1) ** 2 / eps + 256) ** 2 * eps ** (3 / 2))
                                  + 8 * (4 * (2 * x_1 - 1) ** 2 +
                                         4 * (2 * x_2 - 1) ** 2 - 1) * (2 * x_2 - 1) ** 2 /
                                  (((4 * (2 * x_1 - 1) ** 2 + 4 * (2 * x_2 - 1) ** 2 - 1) ** 2 / eps + 256) ** 2 * eps ** (3 / 2))
                                  - 1 / (((4 * (2 * x_1 - 1) ** 2 + 4 * (2 * x_2 - 1) ** 2 - 1) ** 2 / eps + 256) * sqrt(eps)))
                   - 256 * (2 * x_1 - 1) / (((4 * (2 * x_1 - 1) ** 2 + 4 * (2 * x_2 - 1) ** 2 - 1) ** 2 / eps + 256) * sqrt(eps))
                   - 256 * (2 * x_2 - 1) / (((4 * (2 * x_1 - 1) ** 2 + 4 * (2 * x_2 - 1) ** 2 - 1) ** 2 / eps + 256) * sqrt(eps))
                   )
            return {"val": res[..., None, None]}


    def analytic_sol(coors, t):
        x_1 = coors[..., 0]
        x_2 = coors[..., 1]
        sin = nm.sin
        pi = nm.pi
        arctan = nm.arctan
        sqrt = nm.sqrt
        res = -arctan(1/16*(4*(2*x_1 - 1)**2 + 4*(2*x_2 - 1)**2 - 1)/sqrt(diffcoef))

        return res


    @local_register_function
    def sol_fun(ts, coors, mode="qp", **kwargs):
        t = ts.time
        if mode == "qp":
            return {"u": analytic_sol(coors, t)[..., None, None]}

    dgebcs = {
        'u_left' : ('left', {'u.all': "bc_funs", 'grad.u.all' : "bc_funs"}),
        'u_top'  : ('top', {'u.all': "bc_funs", 'grad.u.all' :  "bc_funs"}),
        'u_bot'  : ('bottom', {'u.all': "bc_funs", 'grad.u.all' :  "bc_funs"}),
        'u_right': ('right', {'u.all': "bc_funs", 'grad.u.all' :  "bc_funs"}),
    }

    materials = {
        'a'     : ({'val': [velo], '.flux': adflux},),
        'D'     : ({'val': [diffcoef], '.cw': cw},),
        'g'     : 'source_fun'
    }

    equations = {
        'balance': """
                    - dw_s_dot_mgrad_s.i.Omega(a.val, u, v)
                    + dw_dg_advect_laxfrie_flux.i.Omega(a.flux, a.val, v, u)
                   """
                   +
                   " + dw_laplace.i.Omega(D.val, v, u) " +
                   diffusion_schemes_implicit[diffscheme] +
                   " + dw_dg_interior_penalty.i.Omega(D.val, D.cw, v, u)" +
                   " - dw_volume_lvf.i.Omega(g.val, v) = 0"

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
pass
