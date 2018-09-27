import setuptools
import fastentrypoints

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="botw_duplicator_tools",
    version="1.3",
    description="Tools for duplicating actors and models, for modding the game 'The Legend of Zelda: Breath of the Wild'.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/BravelyPeculiar/botw_duplicator_tools",
    download_url="https://github.com/BravelyPeculiar/botw_duplicator_tools/archive/1.0.tar.gz",
    author="BravelyPeculiar",
    author_email="joshuawaltonm@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['wszst_yaz0>=1.0', 'byml>=1.0', 'sarc>=1.0', 'aamp>=1.0'],
    entry_points = {
        'console_scripts': [
            'actorinfo_tool = botw_duplicator_tools.__main__:run_actorinfo_tool',
            'actorpack_tool = botw_duplicator_tools.__main__:run_actorpack_tool',
            'bfres_duplicator = botw_duplicator_tools.__main__:run_bfres_duplicator',
        ]
    },
)