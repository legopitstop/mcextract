import setuptools

with open('README.md') as f:
    long_description = f.read()

required_modules = ['customtkinter', 'UserFolder', 'serverjars-api', 'requests']

setuptools.setup(
    name='mcextract',
    version='1.1.0',
    author='Legopitstop',
    description='Extract assets and data from the Minecraft jar.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/legopitstop/mcextract',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'': ['assets/**']},
    install_requires=required_modules,
    license='MIT',
    keywords=['Minecraft', 'java', 'jar', 'assets', 'data', 'reports', 'UserFolder', 'customtkinter', 'ServerJars'],
    author_email='officiallegopitstop@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable', # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.10'
)