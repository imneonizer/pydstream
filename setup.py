from setuptools import setup, Extension
from setuptools import find_packages

if __name__ == "__main__":
    setup(
        name="pydstream",
        version="0.0.1",
        description="Easy to use python wrapper around Deepstream Python bindings.",
        long_description_content_type="text/markdown",
        author="Nitin Rai",
        author_email="mneonizer@gmail.com",
        url="https://github.com/imneonizer/pydstream",
        license="MIT License",
        platforms=["linux", "unix"],
        python_requires=">3.5.2",
    )