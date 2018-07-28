import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rpi_stream_img",
    version="0.0.1",
    author="Theo Cooper and Ian Huang",
    author_email="theoac2009@outlook.com",
    description="A very simple library built for streaming video from a remote Raspberry Pi server in realtime."
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)