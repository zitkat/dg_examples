#!/usr/bin/env python
# -*- coding:utf-8 -*-
""""
Script for running DG conf files.
"""
import sys
import os
import time
from os.path import join as pjoin

import argparse
import numpy as nm

from sfepy.applications.pde_solver_app import PDESolverApp
from sfepy.base.conf import ProblemConf
from sfepy.base.ioutils import ensure_path
from sfepy.base.base import (get_default, output, assert_,
                             Struct, basestr, IndexedStruct)

from script.dg_plot_1D import load_and_plot_fun
from run_dg_utils import clear_folder, add_dg_arguments, param_names

from run_dg_utils import outputs_folder, output, configure_output


def create_argument_parser():
    parser = argparse.ArgumentParser(
        description='Run SfePy DG example conf python files',
        epilog='(c) 2019  Man-machine Interaction at NTC UWB, ' +
               '\nauthor: Tomas Zitka, email: zitkat@ntc.zcu.cz')

    parser.add_argument("problem_file",
                        help="File containing problem configuration, "+
                             "can include define method and dim variable",
                        metavar='path')

    parser.add_argument("--output",
                        help="Output directory, can contain {}, " +
                             "exampe name is than plugged in.",
                        dest="output_dir",
                        metavar='path', type=str, default=None)

    parser.add_argument("-m", "--mesh", help="File with starting mesh to use",
                        default=None, metavar='path', action='store',
                        dest='mesh_file',)

    parser.add_argument('-dp', '--display-plots', help="To show plots for 1D case",
                        dest="doplot", action="store_true")

    parser.add_argument("-v", "--verbose", help="To be verbose or",
                        default=False, action='store_true', dest='verbose',)

    parser.add_argument("--noscreenlog", help="Do not print log to screen",
                        default=False, action='store_true',
                        dest='no_output_screen', )

    parser.add_argument('--order', metavar="int", default=None,
                        help='Approximation order', type=int)

    add_dg_arguments(parser)
    return parser


def get_parametrized_conf(filename, args):
    import importlib
    prefix = ""

    problem_module_name = filename.replace(".py", "").strip("\\.") \
        .replace("\\", ".").replace("/", ".")
    if not problem_module_name.startswith(prefix):
        problem_module_name = prefix + problem_module_name

    problem_module = importlib.import_module(problem_module_name)

    dg_args = {dg_par_name: args.__dict__[dg_par_name]
               for dg_par_name in param_names + ["mesh_file", "order"]
               if args.__dict__[dg_par_name] is not None}

    if hasattr(problem_module, "define"):
        mod = sys.modules[problem_module_name]
        # noinspection PyCallingNonCallable
        problem_conf = ProblemConf.from_dict(
            problem_module.define(
                **dg_args
            ), mod, verbose=args.verbose)
        if args.mesh_file is not None:
            problem_conf.options.absolute_mesh_path = True
    else:
        output("Problem file is not parametrized, arguments ignored")
        problem_conf = ProblemConf.from_file(filename, verbose=False)
        problem_conf.verbose = args.verbose

    return problem_conf


def main(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = create_argument_parser()
    args = parser.parse_args(argv)

    conf_file_name = args.problem_file

    pc = get_parametrized_conf(conf_file_name, args)

    if args.output_dir is None:
        output_folder = pjoin(outputs_folder, "output", pc.example_name)
    elif "{}" in args.output_dir:
        output_folder = args.output_dir.format(pc.example_name)
    else:
        output_folder = args.output_dir

    output_name_trunk_folder = pjoin(output_folder, str(pc.approx_order) + "/")

    configure_output({'output_screen': not args.no_output_screen,
                      'output_log_name': pjoin(output_name_trunk_folder,
                                               "last_run.txt")})

    output("Processing conf file {}".format(conf_file_name))
    output("----------------Running--------------------------")
    output("{}: {}".format(pc.example_name, time.asctime()))

    output_name_trunk_name = pc.example_name + str(pc.approx_order)
    output_name_trunk = pjoin(output_name_trunk_folder, output_name_trunk_name)
    ensure_path(output_name_trunk_folder)
    output_format = "{}.*.{}".format(output_name_trunk,
                                      pc.options.output_format
                                      if hasattr(pc.options, "output_format")
                                      else "vtk")

    output("Output set to {}, clearing.".format(output_format))
    clear_folder(output_format, confirm=False)

    sa = PDESolverApp(pc, Struct(output_filename_trunk=output_name_trunk,
                                 save_ebc=False,
                                 save_ebc_nodes=False,
                                 save_region=False,
                                 save_regions=False,
                                 save_regions_as_groups=False,
                                 save_field_meshes=False,
                                 solve_not=False), "sfepy")
    tt = time.process_time()
    sa()
    elapsed = time.process_time() - tt
    output("{}: {}".format(pc.example_name, time.asctime()))
    output("------------------Finished------------------\n\n")

    if pc.dim == 1 and args.doplot:
        if pc.transient:
            load_times = min(pc.options.save_times, sa.problem.ts.n_step)
            load_and_plot_fun(output_name_trunk_folder, output_name_trunk_name,
                              pc.t0, pc.t1, load_times,
                              pc.get_ic,
                              # exact=getattr(pc, "analytic_sol", None),
                              polar=False, compare=False)
        else:
            load_times = 1
            load_and_plot_fun(output_name_trunk_folder, output_name_trunk_name,
                              pc.t0, pc.t1, load_times)


if __name__ == '__main__':
    main(sys.argv[1:])
