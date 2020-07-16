$env:PYTHONPATH = "C:\Users\tomas\PycharmProjects\Numerics\sfepy\;C:\Users\tomas\PycharmProjects\Numerics\meshio"

# ADVECTION  PARAMETRIZED
python .\run_dg_example.py .\advection\example_dg_advection1D.py
python .\run_dg_example.py .\advection\example_dg_advection1D_sin.py
python .\run_dg_example.py .\advection\example_dg_advection2D.py
python .\run_dg_example.py .\advection\example_dg_advection2D_kriv.py
python .\run_dg_example.py .\advection\example_dg_advection2D_sin.py

# DIFFUSION PARAMETRIZED
python .\run_dg_example.py .\diffusion\example_dg_diffusion1D.py
python .\run_dg_example.py .\diffusion\example_dg_diffusion1D_hesthaven.py -dp
python .\run_dg_example.py .\diffusion\example_dg_diffusion2D_hartmann.py
python .\run_dg_example.py .\diffusion\example_dg_laplace2D.py
python .\run_dg_example.py .\diffusion\example_dg_diffusion2D_qart.py

# ADVECTION DIFFUSION PARAMETRIZED
python .\run_dg_example.py .\advection\example_dg_quarteroni1.py
python .\run_dg_example.py .\advection\example_dg_quarteroni2.py
python .\run_dg_example.py .\advection\example_dg_quarteroni3.py
python .\run_dg_example.py .\advection\example_dg_quarteroni4.py

# BURGERS PARAMETRIZED
python .\run_dg_example.py .\burgers\example_dg_burgers1D_hesthaven.py -dp
python .\run_dg_example.py .\burgers\example_dg_burgers2D_kucera.py
