$env:PYTHONPATH = "C:\path\to\sfepy"

$mt2D01_4="'mesh/mesh_tensr_2D_01_4.vtk'"
$mt2D11_4="'mesh/mesh_tensr_2D_11_4.vtk'"

$ms2D01_4="'mesh/mesh_simp_2D_01_4.vtk'"
$ms2D11_4="'mesh/mesh_simp_2D_11_4.vtk'"

$mt1D01_2="'mesh/mesh_tensr_1D_01_2.vtk'"
$mt1D11_2="'mesh/mesh_tensr_1D_11_2.vtk'"

$od="outputs/parametric/"

# ADVECTION 2D
soops-run -o .\$od\example_dg_advection2D "problem_file='advection/example_dg_advection2D', --cfl=[0.1, .5], --adflux=[0.0, 0.5, 1.0] , --limit=[@defined, @undefined], mesh=[$mt2D01_4], output_dir='$od/example_dg_advection2D/%s'" .\run_dg_conv_study.py
soops-run -o .\$od\example_dg_advection2D_kriv "problem_file='advection/example_dg_advection2D_kriv', --cfl=[0.1, .5], --adflux=[0.0, 0.5, 1.0] , --limit=[@defined, @undefined], mesh=[$mt2D11_4], output_dir='$od/example_dg_advection2D_kriv/%s'" .\run_dg_conv_study.py
soops-run -o .\$od\example_dg_advection2D_kriv0 -c '--refines + --orders' "problem_file='advection/example_dg_advection2D_kriv', --dt=[1.0], --adflux=[0.0] , --limit=[@defined], --refines=[121, 81, 61, 49], --orders=[1, 2, 3, 4] , output_dir='$od/example_dg_advection2D_kriv0/%s'" .\run_dg_conv_study.py

# ADVECTION 1D
soops-run -o .\$od\example_dg_advection1D_smooth "problem_file='advection/example_dg_advection1D', --cfl=[0.1, .5], --adflux=[0.0, 0.5, 1.0] , --limit=[@defined, @undefined], mesh=[$mt1D01_2], output_dir='$od/example_dg_advection1D_smooth/%s'" .\run_dg_conv_study.py
soops-run -o .\$od\example_dg_advection1D_step "problem_file='advection/example_dg_advection1D', --cfl=[0.1, .5], --adflux=[0.0, 0.5, 1.0] , --limit=[@defined, @undefined], mesh=[$mt1D01_2], output_dir='$od/example_dg_advection1D_step/%s'" .\run_dg_conv_study.py
soops-run -o .\$od\example_dg_advection1D_sin "problem_file='advection/example_dg_advection1D_sin', --cfl=[0.1, 0.5], --adflux=[0.0, 0.5, 1.0] , --limit=[@defined, @undefined], mesh=[$mt1D11_2], --refines='[4,5,6,7,8]', output_dir='$od/example_dg_advection1D_sin/%s'" .\run_dg_conv_study.py

# ADVECTION DIFFUSION
soops-run -o .\$od\example_dg_quarteroni1 "problem_file='advdiff/example_dg_quarteroni1', --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-3, 1e-2, .1, 1], mesh=[$mt2D01_4, $ms2D01_4], output_dir='$od/example_dg_quarteroni1/%s'" .\run_dg_conv_study.py
soops-run -o .\$od\example_dg_quarteroni2 "problem_file='advdiff/example_dg_quarteroni2', --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-5, 1e-4, 1e-3, 1e-2], mesh=[$mt2D01_4, $ms2D01_4], output_dir='$od/example_dg_quarteroni2/%s'" .\run_dg_conv_study.py
soops-run -o .\$od\example_dg_quarteroni3 "problem_file='advdiff/example_dg_quarteroni3', --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-3, 1e-2, .1, 1], mesh=[$mt2D01_4, $ms2D01_4], output_dir='$od/example_dg_quarteroni3/%s'" .\run_dg_conv_study.py

# BURGERS
$ex="example_dg_burgers1D_hesthaven"
soops-run -o .\$od\$ex "problem_file='burgers/$ex', --limit=[@defined, @undefined], --cfl=[1e-3, 1e-2], --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-3, 1e-2], mesh=[$mt1D11_2], output_dir='$od/$ex/%s'" .\run_dg_conv_study.py

$ex='example_dg_burgers2D_kucera'
soops-run -o .\$od\$ex -c '--cw + --diffscheme' "problem_file='burgers/$ex', --dt=[1e-5], --cw=[1, 5 , 15], --diffcoef=[1e-2, 0.1], --diffscheme=[symmetric, non-symmetric, incomplete], mesh=[$mt2D11_4, $ms2D11_4], --refines='[1,2,3,4,5]', --orders='[1,2]', output_dir='$od/$ex/%s'" .\run_dg_conv_study.py

# DIFFUSION
$ex="example_dg_diffusion1D_hesthaven.py"
soops-run -o .\$od\$ex "problem_file='diffusion/$ex', --cfl=[1e-3, 1e-2], --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-2], mesh=['mesh/mesh_tensr_1D_0-2pi_100.vtk'], --refines='[0,1,2]', output_dir='$od/$ex/%s'" .\run_dg_conv_study.py

$ex="example_dg_diffusion2D_hartmann"
soops-run -o .\$od\$ex "problem_file='diffusion/$ex', --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-2], mesh=[$mt2D01_4, $ms2D01_4], output_dir='$od/$ex/%s'" .\run_dg_conv_study.py

$ex="example_dg_diffusion2D_qart"
soops-run -o .\$od\$ex "problem_file='diffusion/$ex', --cw=[1, 10, 100, 1e3, 1e4, 1e5], --diffcoef=[1e-2], mesh=[$mt2D01_4, $ms2D01_4], output_dir='$od/$ex/%s'" .\run_dg_conv_study.py


$ex="example_dg_laplace2D"
soops-run -o .\$od\$ex "problem_file='diffusion/$ex', --diffcoef=[1e-3, 1e-2, 0.1, 1] , --cw=[1, 10, 100, 1e3, 1e4, 1e5], mesh=[$mt2D01_4, $ms2D01_4], output_dir='$od/$ex/%s'" .\run_dg_conv_study.py

