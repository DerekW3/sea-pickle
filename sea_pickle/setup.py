from setuptools import Extension, setup

ext_modules = [
    Extension("sea_pickle.seapickle", sources=["src/sea_pickle//sea_pickle.c"])
]

setup(
    name="sea-pickle",
    version="0.1.0",
    description="A C implementation of Pickle",
    author="DerekW3",
    author_email="92753567+DerekW3@users.noreply.github.com",
    ext_modules=ext_modules,
)
