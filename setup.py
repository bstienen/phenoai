#from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='phenoai',
	version='0.1.3',
	author='Bob Stienen',
	author_email='b.stienen@science.ru.nl',
	description='Machine Learning interface for High Energy Physics Phenomenology',
	long_description=long_description,
	long_description_content_type="text/markdown",
	keywords='high energy physics machine learning phenomenology limits exclusion likleihood likelihoods',
	url='http://hef.ru.nl/~bstienen/phenoai',
	license='MIT',
	data_files = [("", ["LICENSE","README.md"])],
	packages=setuptools.find_packages(),
	classifiers=(
		'Development Status :: 4 - Beta',
		'Programming Language :: Python :: 3',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Topic :: Scientific/Engineering :: Physics',
		'Topic :: Scientific/Engineering :: Artificial Intelligence'),
	install_requires=['pyslha','requests','h5py','numpy','matplotlib','scipy']
)

