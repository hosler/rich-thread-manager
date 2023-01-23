from setuptools import setup

setup(
    name='rtmui',
    version='0.1.0',
    description='Python thread manager via Rich enabled terminal',
    url='https://github.com/shuds13/pyexample',
    author='Daniel Hosler',
    author_email='danhosler@gmail.com',
    license='MIT',
    packages=['rtmui'],
    install_requires=['rich>=13.2.0',
                      'sshkeyboard>=2.3.1'
                      ],
)