import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csinsc",
    version="1.0.4.2",
    author="Toan Huynh",
    author_email="toan@csinschools.io",
    description="Tools and libraries used in the CSinSchools course",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toanhuynhcsinsc/csinsc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
