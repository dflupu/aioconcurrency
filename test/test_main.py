import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest

import aioconcurrency


async def return_same(i):
    await asyncio.sleep(0.01)
    return i


def return_same_sync(i):
    return i


@pytest.mark.asyncio
async def test_each_limit_with_array():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    gen = aioconcurrency.each(items, return_same, concurrency=4)
    async for item in gen:
        results.append(item)

    assert gen.count_processed == len(items)
    assert sorted(results) == items


@pytest.mark.asyncio
async def test_each_limit_with_queue():

    items = [1, 2, 3, 4, 5, 6, 7]
    items_queue = asyncio.Queue()
    results = []

    for item in items:
        items_queue.put_nowait(item)

    gen = aioconcurrency.each(items, return_same, concurrency=4)
    async for item in gen:
        results.append(item)

        if len(results) == len(items):
            break

    assert gen.count_processed == len(items)
    assert sorted(results) == items


@pytest.mark.asyncio
async def test_each_limit_with_discard_results():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    gen = aioconcurrency.each(items, return_same, concurrency=4, discard_results=True)
    await gen.wait()

    async for item in gen:
        results.append(item)

    assert gen.count_processed == len(items)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_each_with_array():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    gen = aioconcurrency.each(items, return_same)
    async for item in gen:
        results.append(item)

    assert gen.count_processed == len(items)
    assert sorted(results) == items


@pytest.mark.asyncio
async def test_each_with_queue():

    items = [1, 2, 3, 4, 5, 6, 7]
    items_queue = asyncio.Queue()
    results = []

    for item in items:
        items_queue.put_nowait(item)

    gen = aioconcurrency.each(items, return_same)
    async for item in gen:
        results.append(item)

        if len(results) == len(items):
            break

    assert gen.count_processed == len(items)
    assert sorted(results) == items


@pytest.mark.asyncio
async def test_each_with_discard_results():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    gen = aioconcurrency.each(items, return_same, discard_results=True)
    await gen.wait()

    async for item in gen:
        results.append(item)

    assert gen.count_processed == len(items)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_map_limit_with_array():

    items = [1, 2, 3]
    results = await aioconcurrency.map(items, return_same, concurrency=4)
    assert results == items


@pytest.mark.asyncio
async def test_each_limit_with_empty_array():

    items = []
    results = []

    async for result in aioconcurrency.each(items, return_same, concurrency=4):
        results.append(result)

    assert results == items


@pytest.mark.asyncio
async def test_each_with_empty_array():

    items = []
    results = []

    async for result in aioconcurrency.each(items, return_same):
        results.append(result)

    assert results == items


@pytest.mark.asyncio
async def test_map_with_empty_array():

    items = []
    results = await aioconcurrency.map(items, return_same)
    assert results == items


@pytest.mark.asyncio
async def test_map_limit_with_empty_array():
    items = []
    results = await aioconcurrency.map(items, return_same, concurrency=4)
    assert results == items


@pytest.mark.asyncio
async def test_map_with_array():

    items = [1, 2, 3]
    results = await aioconcurrency.map(items, return_same)
    assert results == items


@pytest.mark.asyncio
async def test_each_with_queue_piping_more():

    items_a = [1, 2, 3]
    items_b = [4, 5, 6, 7]
    count = len(items_a) + len(items_b)

    items_queue = asyncio.Queue()
    results = []

    for item in items_a:
        items_queue.put_nowait(item)

    gen = aioconcurrency.each(items_queue, return_same)
    await asyncio.sleep(0.1)

    for item in items_b:
        items_queue.put_nowait(item)

    async for item in gen:
        results.append(item)

        if len(results) == count:
            break

    gen.cancel()
    assert gen.count_processed == count
    assert sorted(results) == items_a + items_b


@pytest.mark.asyncio
async def test_map_exception_bubbles_up():

    class TestException(Exception):
        pass

    async def throws(_):
        raise TestException('test')

    items = [1]

    try:
        await aioconcurrency.map(items, throws)
    except TestException as ex:
        assert isinstance(ex, TestException)
    else:
        raise Exception('expected throw')


@pytest.mark.asyncio
async def test_each_limit_with_executor():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    pool = ThreadPoolExecutor(10)
    gen = aioconcurrency.each(items, return_same, concurrency=4, executor=pool)
    async for item in gen:
        results.append(item)

    assert gen.count_processed == len(items)
    assert sorted(results) == items


@pytest.mark.asyncio
async def test_map_limit_with_executor():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    pool = ThreadPoolExecutor(10)
    items = [1, 2, 3]
    results = await aioconcurrency.map(items, return_same, concurrency=4, executor=pool)
    assert results == items


@pytest.mark.asyncio
async def test_map_with_sync_function():

    items = [1, 2, 3]
    results = []

    results = await aioconcurrency.map(items, return_same_sync)
    assert results == items


@pytest.mark.asyncio
async def test_each_with_sync_function():

    items = [1, 2, 3]
    results = []

    async for result in aioconcurrency.each(items, return_same_sync):
        results.append(result)

    assert results == items
