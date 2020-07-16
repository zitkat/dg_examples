"""
Based on

Antonietti, P., & Quarteroni, A. (2013). Numerical performance of discontinuous
   and stabilized continuous Galerkin methods for convection–diffusion problems.
"""

from example_dg_common import *

def define(filename_mesh=None,
           approx_order=3,

           adflux=0.0,
           limit=False,

           cw=100,
           diffcoef=1e-9,
           diffscheme="symmetric",

           cfl=None,
           dt=None,
           ):

    cfl = None
    dt = None

    example_name = "quart4"
    dim = 2

    if filename_mesh is None:
        filename_mesh = get_gen_block_mesh_hook((1., 1.), (20, 20), (.5, .5))

    velo = [3., 0.]

    angle = nm.pi / 3
    rotm = nm.array([[nm.cos(angle), nm.sin(angle)],
                     [-nm.sin(angle), nm.cos(angle)]])
    velo = nm.sum(rotm.T * nm.array(velo), axis=-1)[:, None]


    regions = {
        'Omega'     : 'all',
        'bot_left' : ('vertices in (x < 0.01) & (y < 0.5)', 'edge'),
        'top_left' : ('vertices in (x < 0.01) & (y > 0.5)', 'edge'),
        'right': ('vertices in x == 1', 'edge'),
        'top' : ('vertices in y == 1', 'edge'),
        'bottom': ('vertices in y == 0', 'edge')
    }

    fields = {
        'density': ('real', 'scalar', 'Omega', str(approx_order) + 'd', 'DG', 'legendre')
    }

    variables = {
        'p': ('unknown field', 'density', 0),
        'v': ('test field', 'density', 'p'),
    }

    integrals = {
        'i': 2 * approx_order,
    }

    dgebcs = {
        'u_bot_left' : ('bot_left', {'p.all': 1, 'grad.p.all' : (0, 0)}),
        'u_top_left': ('top_left', {'p.all': 0, 'grad.p.all': (0, 0)}),
        'u_top'  : ('top', {'p.all': 0, 'grad.p.all': (0, 0)}),
        'u_bot'  : ('bottom', {'p.all': 1, 'grad.p.all': (0, 0)}),
        'u_right': ('right', {'p.all': 0, 'grad.p.all': (0, 0)}),
    }

    materials = {
        'a'     : ({'val': [velo], '.flux': adflux},),
        'D'     : ({'val': [diffcoef], '.cw': cw},),
        # 'g'     : 'source_fun'
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
                   # " + dw_volume_lvf.i.Omega(g.val, v)
                   " = 0"

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