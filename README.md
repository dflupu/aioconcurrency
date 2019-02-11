# aioconcurrency [![Build Status](https://travis-ci.org/dflupu/aioconcurrency.svg?branch=master)](https://travis-ci.org/dflupu/aioconcurrency)

Run a coroutine with each item in an iterable, concurrently

## Install

`pip install aioconcurrency`

## Usage example

```
import aioconcurrency

items = [1, 2, 3, 4]
async def f(item): return item * 2

await aioconcurrency.map(items, f, concurrency=2).results()  # Returns [2, 4, 6, 8]

async for result in aioconcurrency.each(items, f, concurrency=2):
    print(result)  # Prints 2 4 6 8 in random order
```

## Api

### aioconcurrency.map

Runs the given coroutine concurrently with each item in an iterable.
The list of the return values will be ordered as if the coroutine was ran serially.

`items`

An iterable object.

`coro`

Coroutine to feed each item to.

`optional: concurrency`

Number of concurrent runs of `coro`. Defaults to `aioconcurrency.Infinite`.

`property: results()`

Coroutine. Must be awaited to obtain the list of return values.

`property: processed_count`

The number of items that have been processed so far.

`property: cancel()`

Cancels all runs of `coro`.

### aioconcurrency.each

Runs the given coroutine concurrently with each item in an iterable.
Returns a generator that may be used to iterate over the return values. The generator yields values as soon as they are available.

`items`

An iterable object. If an `asyncio.Queue` is passed then `.each` will read from it indefinitely.

`coro`

Coroutine to feed each item to.

`optional: concurrency`

Number of concurrent runs of `coro`. Defaults to `aioconcurrency.Infinite`.

`optional: discard_results`

If truthy, discard the return value of `coro`. Defaults to false.

`property: wait()`

Coroutine. May be used to wait until all items have been processed.

`property: processed_count`

The number of items that have been processed so far.

`property: cancel()`

Cancels all runs of `coro`.

## Tests

`pytest .`
