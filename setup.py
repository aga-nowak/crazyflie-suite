from setuptools import setup, find_packages

setup(
    name="crazyflie-suite",
    packages=find_packages(),
    install_requires=[
        "cflib",
        "cfclient",
        "numpy",
        "pandas",
        "matplotlib",
        "jupyterlab",
        "pyyaml==5.3.1",
        "pre-commit",
        "scipy",
        "IPython",
    ],
)
