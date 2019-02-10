import asyncio

import pytest

import aioconcurrency


@pytest.mark.asyncio
async def test_each_limit_with_array():

    items = [1, 2, 3, 4, 5, 6, 7]
    results = []

    gen = aioconcurrency.each(items, return_same, 4)
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

    gen = aioconcurrency.each(items, return_same, 4)
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

    gen = aioconcurrency.each(items, return_same, 4, discard_results=True)
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
    results = await aioconcurrency.map(items, return_same, concurrency_limit=4).results()
    assert results == items


@pytest.mark.asyncio
async def test_map_with_array():

    items = [1, 2, 3]
    results = await aioconcurrency.map(items, return_same).results()
    assert results == items


async def return_same(i):
    return i
