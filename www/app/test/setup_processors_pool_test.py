import pytest
from unittest.mock import create_autospec, patch, ANY

from setup_processors_pool import SetupProcessorsPool, AlreadyInProgressError
from setup_processor import SetupProcessor
from logger import Logger

from test_globals import *


KEYS = tuple(f'key{i}' for i in range(1, 4))


@pytest.fixture
def f():
    class F:
        SetupProcessorMock = create_autospec(SetupProcessor, spec_set=True)
        processor_mocks = tuple(create_autospec(SetupProcessor, spec_set=True, instance=True) for _ in range(0, 3))
        SetupProcessorMock.side_effect = processor_mocks
        logger_mock = create_autospec(spec=Logger, spec_set=True, instance=True)
        sut = SetupProcessorsPool(app_dir=APP_DIR, logger=logger_mock, setup_processor_class=SetupProcessorMock)

        for k in KEYS:
            sut.spawn(k, **PARAMS)
    return F


@pytest.mark.asyncio
async def test_run_once_must_process_all(f):
    assert f.sut.is_pending(KEYS[0])
    assert len(f.sut.pending()) == 3
    assert len(f.sut.completed()) == 0
    assert tuple(f.sut.pending().keys()) == KEYS

    await f.sut.run_once()

    assert not f.sut.is_pending(KEYS[0])
    assert len(f.sut.pending()) == 0
    assert len(f.sut.completed()) == 3
    assert tuple(f.sut.completed().keys()) == KEYS

    for k in KEYS:
        f.sut.completed()[k].run.assert_called_once_with()


@pytest.mark.asyncio
async def test_run_once_must_process_all_regardless_of_exception(f):
    f.processor_mocks[0].run.side_effect = RuntimeError()

    await f.sut.run_once()

    assert len(f.sut.pending()) == 0
    assert len(f.sut.completed()) == 3
    assert tuple(f.sut.completed().keys()) == KEYS

    f.logger_mock.error.assert_called_once_with(ANY)

    for k in KEYS:
        f.sut.completed()[k].run.assert_called_once_with()


@pytest.mark.asyncio
async def test_get_must_return_none_if_no_key_found(f):
    f.sut.pending().clear()

    assert f.sut.get(KEYS[0]) == None
    await f.sut.run_once()
    assert f.sut.get(KEYS[0]) == None


@pytest.mark.asyncio
async def test_get_must_return_object_if_key_found(f):
    assert f.sut.get(KEYS[0]) is f.sut.pending()[KEYS[0]]
    await f.sut.run_once()
    assert f.sut.get(KEYS[0]) is f.sut.completed()[KEYS[0]]


def test_spawn_must_raise_if_setup_pending(f):
    with pytest.raises(AlreadyInProgressError):
        f.sut.spawn(key=KEYS[0])


@pytest.mark.asyncio
async def test_spawn_must_clear_completed_processor(f):
    await f.sut.run_once()
    assert len(f.sut.completed()) == 3
    assert tuple(f.sut.completed().keys()) == KEYS

    f.SetupProcessorMock.return_value = create_autospec(SetupProcessor, spec_set=True, instance=True)
    f.SetupProcessorMock.side_effect = None

    f.sut.spawn(key=KEYS[0])
    assert len(f.sut.completed()) == 2
    assert KEYS[0] not in f.sut.completed()
