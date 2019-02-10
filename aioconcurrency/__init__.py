import asyncio


def map(seq, coro, concurrency_limit=None):
    if concurrency_limit is not None:
        assert concurrency_limit > 0
        return _AioMapLimitSeq(seq, coro, concurrency_limit)
    else:
        return _AioMapSeq(seq, coro)


def each(seq, coro, concurrency_limit=None, *, discard_results=False):
    if concurrency_limit is not None:
        assert concurrency_limit > 0
        obj_type = isinstance(seq, asyncio.Queue) and _AioEachLimitQueue or _AioEachLimitSeq
        return obj_type(seq, coro, concurrency_limit, discard_results)
    else:
        obj_type = isinstance(seq, asyncio.Queue) and _AioEachQueue or _AioEachSeq
        return obj_type(seq, coro, discard_results=discard_results)


class _AioMapLimitSeq():

    def __init__(self, seq, coro, concurrency_limit=None):
        self._seq = seq
        self._coro = coro
        self._limit = concurrency_limit

        self._pending = 0
        self._processed = 0

        self._i = 0
        self._results = [None] * len(seq)

        self._completion_handler_task = asyncio.ensure_future(self._completion_handler())
        self._can_queue_next = asyncio.Event()
        self._can_yield_result = asyncio.Event()

    @property
    def count_processed(self):
        return self._processed

    async def results(self):
        await self._completion_handler_task
        return self._results

    async def _run_next(self):
        try:
            item_index = self._i
            item = self._get_next_item()
            result = await self._coro(item)

            self._results[item_index] = result
            self._processed += 1
        except _AioOutOfItems:
            pass

        self._pending -= 1
        self._can_queue_next.set()

    async def _completion_handler(self):
        for _ in range(self._limit):
            self._pending += 1
            asyncio.shield(self._run_next())

        while self._pending > 0:
            await self._can_queue_next.wait()
            self._can_queue_next.clear()

            while self._pending < self._limit and self._has_next_item():
                self._pending += 1
                asyncio.shield(self._run_next())

        return self._results

    def _has_next_item(self):
        return self._i < len(self._seq)

    def _get_next_item(self):
        if not self._has_next_item():
            raise _AioOutOfItems

        next_item = self._seq[self._i]
        self._i += 1

        return next_item


class _AioMapSeq(_AioMapLimitSeq):

    async def _completion_handler(self):
        for _ in range(len(self._seq)):
            self._pending += 1
            asyncio.shield(self._run_next())

        while self._pending > 0:
            await self._can_queue_next.wait()


class _AioEachLimit():

    def __init__(self, seq, coro, concurrency_limit=None, discard_results=False):
        self._seq = seq
        self._coro = coro
        self._limit = concurrency_limit
        self._discard_results = discard_results

        self._completed = asyncio.Queue()
        self._pending = 0
        self._processed = 0

        self._completion_handler_task = asyncio.ensure_future(self._completion_handler())
        self._can_queue_next = asyncio.Event()
        self._can_yield_result = asyncio.Event()

    @property
    def count_processed(self):
        return self._processed

    async def wait(self):
        return await self._completion_handler_task

    async def _run_next(self):
        try:
            item = await self._get_next_item()
            result = await self._coro(item)

            if not self._discard_results:
                await self._completed.put(result)

            self._processed += 1
        except _AioOutOfItems:
            pass

        self._pending -= 1
        self._can_queue_next.set()
        self._can_yield_result.set()

    async def _completion_handler(self):
        for _ in range(self._limit):
            self._pending += 1
            asyncio.shield(self._run_next())

        while self._pending > 0:
            await self._can_queue_next.wait()
            self._can_queue_next.clear()

            while self._pending < self._limit and self._has_next_item():
                self._pending += 1
                asyncio.shield(self._run_next())

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            if not self._completed.empty():
                return self._completed.get_nowait()

            if self._completion_handler_task.done():
                raise StopAsyncIteration

            await self._can_yield_result.wait()
            self._can_yield_result.clear()


class _AioEachLimitSeq(_AioEachLimit):

    def __init__(self, *args, **kwargs):
        self._i = 0
        super().__init__(*args, **kwargs)

    def _has_next_item(self):
        return self._i < len(self._seq)

    async def _get_next_item(self):
        if not self._has_next_item():
            raise _AioOutOfItems

        next_item = self._seq[self._i]
        self._i += 1

        return next_item


class _AioEachLimitQueue(_AioEachLimit):

    def _has_next_item(self):
        return True

    async def _get_next_item(self):
        return await self._seq.get()


class _AioEachSeq(_AioEachLimitSeq):

    async def _completion_handler(self):
        while self._has_next_item():
            self._pending += 1
            asyncio.shield(self._run_next())
            await asyncio.sleep(0)  # Yield


class _AioEachQueue(_AioEachLimitQueue):

    async def _completion_handler(self):
        while self._has_next_item():
            self._pending += 1
            asyncio.shield(self._run_next())

            while self._seq.empty():
                await self._can_yield_result.wait()


class _AioOutOfItems(Exception):
    pass


class _AioNoConcurrencyLimit():
    pass
