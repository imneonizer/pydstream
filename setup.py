from distutils.core import setup

if __name__ == '__main__':
    setup(
        name = 'pydstream',
        packages = ['pydstream'],
        version = '0.0.1',
        license='MIT',
        description = 'Easy to use python wrapper around Deepstream Python bindings',
        author = 'Nitin Rai',
        author_email = 'mneonizer@gmail.com',
        url = 'https://github.com/imneonizer/pydstream',
        keywords = ['python deepstream', 'pyds', 'deepstream', 'nvidia'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
    )