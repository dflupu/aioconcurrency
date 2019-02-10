# aioconcurrency

Run a coroutine with each item in an iterable, optionally limiting concurrency

## Install

`pip install aioconcurrency`

## Usage example

```
import aioconcurrency

async def f(item):
	return item * 2

items = [1, 2, 3, 4]

async for result in aioconcurrency.each(items, f, concurrency_limit=2):
	print(result)  # Prints 2 4 6 8 in random order

await aioconcurrency.map(items, f, concurrency_limit=2).results()  # Returns [2, 4, 6, 8]
```

## Api

### aioconcurrency.each

Runs the given coroutine concurrently with each item in an iterable. Returns a generator that may be used to iterate over the return values.

##### `items`

An iterable object. If an `asyncio.Queue` is passed `.each` will read from it indefinitely.

##### `coro`

Coroutine to feed each item to.

##### `optional: concurrency_limit`

Maximum concurrent runs of `coro`. Defaults to infinite.

##### `optional: discard_results`

If truthy, discard the return value of `coro`. Defaults to false.

##### `property: wait()`

Coroutine. May be awaited to wait until all items have been processed.

##### `property: processed_count`

The number of items that have been processed so far.

### aioconcurrency.map

Runs the given coroutine concurrently with each item in an iterable. May be used to obtain a list of the return values in the expected order.

##### `items`

An iterable object.

##### `coro`

Coroutine to feed each item to.

##### `optional: concurrency_limit`

Maximum concurrent runs of `coro`. Defaults to infinite.

##### `property: results()`

Coroutine. Returns the list of return values.

##### `property: processed_count`

The number of items that have been processed so far.

## Tests

`pytest .`
