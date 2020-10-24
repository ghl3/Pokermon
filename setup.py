from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup_requires = ["setuptools-rust>=0.10.1", "wheel"]
install_requires = []

setup(
    name="pyholdthem",
    version="1.0",
    rust_extensions=[RustExtension("holdthem.pyholdthem", binding=Binding.PyO3)],
    packages=["pyholdthem"],
    install_requires=install_requires,
    setup_requires=setup_requires,
    include_package_data=True,
    zip_safe=False,
)
