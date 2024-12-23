from setuptools import setup, find_packages  # noqa: H301


with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='edenaiapis',
    version='0.1.3-RC1',
    description='Providers connectors',
    url='https://github.com/edenai/edenai-apis',
    author='Eden AI',
    author_email='tech@edenai.co',
    license='Apache License 2',
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
)
