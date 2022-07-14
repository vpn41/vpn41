import pytest
from unittest.mock import create_autospec, patch, ANY

from setup_processors_pool import SetupProcessorsPool, AlreadyInProgressError
from setup_processor import SetupProcessor
from logger import Logger

from test_globals import *


KEYS = tuple(f'key{i}' for i in range(1, 4))


@pytest.fixture
def logger_mock():
    return create_autospec(spec=Logger, spec_set=True, instance=True)


@pytest.fixture
def setup_processor_mocks():
    return tuple(create_autospec(SetupProcessor, spec_set=True, instance=True) for _ in range(0, 3))


@pytest.fixture
def setup_processor_class_mock(setup_processor_mocks):
    mock = create_autospec(SetupProcessor, spec_set=True)
    mock.side_effect = setup_processor_mocks
    return mock


@pytest.fixture
def sut(logger_mock, setup_processor_class_mock):
    sut = SetupProcessorsPool(app_dir=APP_DIR, logger=logger_mock, setup_processor_class=setup_processor_class_mock)

    for k in KEYS:
        sut.spawn(k, **PARAMS)

    return sut


@pytest.mark.asyncio
async def test_run_once_must_process_all(sut):
    assert sut.is_pending(KEYS[0])
    assert len(sut.pending()) == 3
    assert len(sut.completed()) == 0
    assert tuple(sut.pending().keys()) == KEYS

    await sut.run_once()

    assert not sut.is_pending(KEYS[0])
    assert len(sut.pending()) == 0
    assert len(sut.completed()) == 3
    assert tuple(sut.completed().keys()) == KEYS

    for k in KEYS:
        sut.completed()[k].run.assert_called_once_with()


@pytest.mark.asyncio
async def test_run_once_must_process_all_regardless_of_exception(sut, setup_processor_mocks, logger_mock):
    setup_processor_mocks[0].run.side_effect = RuntimeError()

    await sut.run_once()

    assert len(sut.pending()) == 0
    assert len(sut.completed()) == 3
    assert tuple(sut.completed().keys()) == KEYS

    logger_mock.error.assert_called_once_with(ANY)

    for k in KEYS:
        sut.completed()[k].run.assert_called_once_with()


@pytest.mark.asyncio
async def test_get_must_return_none_if_no_key_found(sut):
    sut.pending().clear()

    assert sut.get(KEYS[0]) == None
    await sut.run_once()
    assert sut.get(KEYS[0]) == None


@pytest.mark.asyncio
async def test_get_must_return_object_if_key_found(sut):
    assert sut.get(KEYS[0]) is sut.pending()[KEYS[0]]
    await sut.run_once()
    assert sut.get(KEYS[0]) is sut.completed()[KEYS[0]]


def test_spawn_must_raise_if_setup_pending(sut):
    with pytest.raises(AlreadyInProgressError):
        sut.spawn(key=KEYS[0])


@pytest.mark.asyncio
async def test_spawn_must_clear_completed_processor(sut, setup_processor_class_mock):
    await sut.run_once()
    assert len(sut.completed()) == 3
    assert tuple(sut.completed().keys()) == KEYS

    setup_processor_class_mock.return_value = create_autospec(SetupProcessor, spec_set=True, instance=True)
    setup_processor_class_mock.side_effect = None

    sut.spawn(key=KEYS[0])
    assert len(sut.completed()) == 2
    assert KEYS[0] not in sut.completed()
