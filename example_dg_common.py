"""
Functions common to DG examples
"""
import numpy as nm
from glob import glob
import os

from sfepy.mesh.mesh_generators import gen_block_mesh
from sfepy.discrete.fem import Mesh

from sfepy.base.base import (get_default, output, configure_output, assert_,
                             Struct, basestr, IndexedStruct)

# import various ICs
from inits_consts import ghump, gsmooth, \
    left_par_q, left_cos, superic, three_step_u, sawtooth_q, const_q, quadr_cub,\
    four_step_u, cos_const_q, quadr_cub


from sfepy.discrete.dg.limiters import IdentityLimiter, MomentLimiter1D, \
    MomentLimiter2D

from examples.dg.example_dg_common import *


