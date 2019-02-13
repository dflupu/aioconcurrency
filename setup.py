from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='aioconcurrency',
    version='0.3.1',
    description='Run a coroutine with each item in an iterable, concurrently',
    keywords='asyncio aio each map limit semaphore concurrency generator synchronization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://github.com/dflupu/aioconcurrency',
    author='Daniel Lupu',
    author_email='dflupu@gmail.com',
    license='MIT',
    packages=['aioconcurrency'],
    zip_safe=False
)
