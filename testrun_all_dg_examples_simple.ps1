$env:PYTHONPATH = "C:\Users\tomas\PycharmProjects\Numerics\sfepy\;C:\Users\tomas\PycharmProjects\Numerics\meshio"

# ADVECTION PARAMETRIZED
python -m simple .\advection\example_dg_advection1D.py      -o .\outputs\output\advection1D\sol
python -m simple .\advection\example_dg_advection1D_sin.py  -o .\outputs\output\advection1D_sin\sol
python -m simple .\advection\example_dg_advection2D.py      -o .\outputs\output\advection2D\sol
python -m simple .\advection\example_dg_advection2D_kriv.py -o .\outputs\output\advection2D_kriv\sol
python -m simple .\advection\example_dg_advection2D_sin.py  -o .\outputs\output\advection2D_sin\sol

# DIFFUSION PARAMETRIZED
python -m simple .\diffusion\example_dg_diffusion1D.py           -o .\outputs\output\diffusion1D\sol
python -m simple .\diffusion\example_dg_diffusion1D_hesthaven.py -o .\outputs\output\diffusion1D_hesthaven\sol
python -m simple .\diffusion\example_dg_diffusion2D_hartmann.py  -o .\outputs\output\diffusion2D_hartmann\sol
python -m simple .\diffusion\example_dg_diffusion2D_qart.py      -o .\outputs\output\diffusion2D_qart\sol
python -m simple .\diffusion\example_dg_laplace2D.py             -o .\outputs\output\laplace2D\sol

# ADVECTION DIFFUSION PARAMETRIZED
python -m simple .\advdiff\example_dg_quarteroni1.py -o .\outputs\output\quarteroni1\sol
python -m simple .\advdiff\example_dg_quarteroni2.py -o .\outputs\output\quarteroni2\sol
python -m simple .\advdiff\example_dg_quarteroni3.py -o .\outputs\output\quarteroni3\sol
python -m simple .\advdiff\example_dg_quarteroni4.py -o .\outputs\output\quarteroni4\sol

# BURGERS PARAMETRIZED
python -m simple .\burgers\example_dg_burgers1D_hesthaven.py -o .\outputs\output\burgers1D_hesthaven\sol
python -m simple .\burgers\example_dg_burgers2D_kucera.py    -o .\outputs\output\burgers2D_kucera\sol
