from setuptools import find_packages, setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='haps',
    version='1.0.4',
    packages=find_packages(),
    url='https://github.com/ekiro/haps',
    license='MIT License',
    author='Piotr Karkut',
    author_email='karkucik@gmail.com',
    description='Simple DI Library',
    long_description_content_type='text/markdown',
    long_description=readme(),
    platforms='any',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable"]
)
