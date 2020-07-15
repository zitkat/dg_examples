#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Script for plotting 1D DG FEM data stored in VTK files, uses values at QPs for
close approximation.
"""
import glob

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import argparse

from os.path import join as pjoin
import os
import sys
from glob import glob
import numpy as nm
import pandas as pd
import numpy as nm

from sfepy.discrete.equations import Equation, Equations
from sfepy.discrete.variables import FieldVariable
from sfepy.discrete.fem import FEDomain
from sfepy.discrete.fem.meshio import MeshioLibIO
from sfepy.discrete.fem.mesh import Mesh
from sfepy.discrete.functions import make_sfepy_function, Function
from sfepy.discrete.integrals import Integral, Integrals
from sfepy.discrete.materials import Material
from sfepy.discrete.problem import Problem
from sfepy.terms.terms_basic import SurfaceTerm
from sfepy.discrete.dg.fields import DGField

from sfepy.discrete.dg.dg_1D_vizualizer import \
    (load_1D_vtks, animate_1D_DG_sol, load_state_1D_vtk, plot1D_legendre_dofs,
    reconstruct_legendre_dofs)

def head(l):
    if l:
        return l[0]
    else:
        return None

def analytic_sol(coors, t, uset=False, diffcoef=0.001):
    x = coors[..., 0]

    t1 = 1.
    D = diffcoef
    tanh = nm.tanh
    if not uset:
        res = -tanh(-1 / 4 * (2 * t1 - 2 * x - 1) / D) + 1
    else:
        res = -tanh(
            -1 / 4 * (2 * t[None, ...] - 2 * x[..., None] - 1) / D) + 1
    return res


# @local_register_function
def sol_fun(ts, coors, mode="qp", **kwargs):
    t = ts.time
    if mode == "qp":
        return {"u": analytic_sol(coors, t)[..., None, None]}

def load_and_plot_fun(folder, filename, exact=None):
    """
    Parameters
    ----------
    folder : str
        folder where to look for files
    filename : str
        used in {name}.i.vtk, i = 0,1, ... tns - 1
        number of time steps
    exact : callable
        exact solution at the last frame
    """
    in_file = head(glob(pjoin(folder, "*.vtk")))

    coors, data = load_state_1D_vtk(in_file)

    approx_order = data.shape[0] - 1

    dmesh = Mesh.from_file(in_file)
    domain = FEDomain("", dmesh)
    omega = domain.create_region('Omega', 'all')

    field = DGField('f', nm.float64, 'scalar', omega,
                    approx_order=approx_order)
    # Sufficient quadrature order for the analytical expression.
    idiff = Integral('idiff', 20)

    u = FieldVariable("u", "unknown", field)

    eqs = Equations(
        [Equation('balance', SurfaceTerm("s()", "u", idiff, omega, u=u))])
    pb = Problem("err_est", equations=eqs)

    u.set_data(field.ravel_sol(data.swapaxes(0, 1)))

    num_qp = pb.evaluate('ev_volume_integrate.idiff.Omega(u)',
                         u=u,
                         integrals=Integrals([idiff]), mode='qp')

    aux = Material('aux', function=sol_fun)
    ana_qp = pb.evaluate('ev_volume_integrate_mat.idiff.Omega(aux.u, u)',
                         aux=aux, u=u,
                         integrals=Integrals([idiff]), mode='qp')
    qps = pb.fields["f"].mapping.get_physical_qps(idiff.get_qp("1_2")[0])
    fqps = qps.flatten()

    plt.figure("Reconstructed solution")
    plt.gca().set_ylim(-.5, 3.)

    ww_approx, xx = reconstruct_legendre_dofs(coors, None, data)
    ww_exact = exact(xx)

    XN = xx[-1]
    X1 = xx[0]
    plt.plot([X1, XN], [2, 2], 'grey', alpha=.6)
    plt.plot([X1, XN], [0, 0], 'grey', alpha=.6)
    plt.plot(fqps, ana_qp.flatten(), label="$p_{exact}(1, x)$")
    plt.plot(fqps, num_qp.flatten(), label="$p_h(1, x)$")
    plt.legend()
    plt.show()


def main(argv):
    parser = argparse.ArgumentParser(
        description='Plotting of 1D DG data in VTK files',
        epilog='(c) 2019 T. Zitka , Man-machine'
               + ' Interaction at NTC UWB')
    parser.add_argument("input_name",
                        help="Path to the solution .vtk file")
    parser.add_argument("-r", "--refine", type=int, default=4,
                        help="Refirement")
    parser.add_argument("-o", "--order", type=int, default=2,
                        help="Approx order")

    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    input_name = args.input_name

    results_infolder_path = os.path.abspath(input_name)
    full_infolder_path = pjoin(results_infolder_path,
                               f"h{args.refine}", f"o{args.order}")
    results_df = pd.read_csv(head(glob(pjoin(results_infolder_path,
                                             "results.csv"))))
    diffcoef = results_df["diffcoef"].unique()[0]

    contents = glob(pjoin(full_infolder_path, "*.vtk"))
    base_name = os.path.basename(contents[0]).split(".")[0]
    load_and_plot_fun(full_infolder_path, base_name,
                      exact=lambda x: analytic_sol(x, 1., diffcoef=diffcoef))


if __name__ == '__main__':
    main(sys.argv[1:])
