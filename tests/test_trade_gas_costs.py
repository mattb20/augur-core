from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from datetime import timedelta
from trading.test_claimTradingProceeds import acquireLongShares, finalizeMarket
from reporting_utils import proceedToNextRound, proceedToFork, finalizeFork, proceedToDesignatedReporting

#pytestmark = mark.skip(reason="Just for testing gas cost")

# Trading Max Costs

CREATE_ORDER_BEST_CASE    =   [
    547694,
    562138,
    576582,
    591026,
    605470,
    619914,
    634358,
]

CREATE_ORDER_BEST_CASE_2    =   [
    617678,
    632122,
    646566,
    661010,
    675454,
    689898,
    704342,
]

CREATE_ORDER_MAXES    =   [
    695034,
    794664,
    894294,
    993924,
    1093554,
    1193184,
    1292814,
]

CREATE_ORDER_MAXES_2    =   [
    765018,
    864648,
    964278,
    1063908,
    1163538,
    1263168,
    1362798,
]

CANCEL_ORDER_MAXES    =   [
    289826,
    379095,
    468364,
    557633,
    646902,
    736171,
    825440,
]

FILL_ORDER_TAKE_SHARES   =   [
    464780,
    479514,
    494248,
    508981,
    523715,
    538449,
    553183,
]

FILL_ORDER_BOTH_ETH    =   [
    839050,
    1029970,
    1220890,
    1411809,
    1602729,
    1793649,
    1984569,
]

FILL_ORDER_MAKER_REVERSE_POSITION    =   [
    933495,
    1172245,
    1410995,
    1649744,
    1888494,
    2127244,
    2365994,
]

FILL_ORDER_TAKER_REVERSE_POSITION    =   [
    939239,
    1115159,
    1291079,
    1466998,
    1642918,
    1818838,
    1994758,
]

FILL_ORDER_DOUBLE_REVERSE_POSITION    =   [
    2134777,
    2455117,
    2775457,
    3095796,
    3416136,
    3736476,
    4056816,
]

tester.STARTGAS = long(6.7 * 10**6)

@mark.parametrize('numOutcomes', range(2,9))
def test_order_creation_best_case(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    maxGas = 0
    cost = fix('1', '5000')

    outcome = 0

    startGas = localFixture.chain.head_state.gas_used
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == CREATE_ORDER_BEST_CASE_2[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_orderCreationMax(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    maxGas = 0
    cost = fix('1', '5000')

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a7, 100)

    startGas = localFixture.chain.head_state.gas_used
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == CREATE_ORDER_MAXES_2[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_orderCancelationMax(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    cancelOrder = localFixture.contracts['CancelOrder']
    completeSets = localFixture.contracts['CompleteSets']
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a7, 100)

    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    cancelOrder.cancelOrder(orderID)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == CANCEL_ORDER_MAXES[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_order_filling_take_shares(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    cost = 500000

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    orderID = createOrder.publicCreateOrder(ASK, 100, 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = cost)

    startGas = localFixture.chain.head_state.gas_used
    fillOrder.publicFillOrder(orderID, fix(1), tradeGroupID, sender = tester.k1, value=cost)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == FILL_ORDER_TAKE_SHARES[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_order_filling_both_eth(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    cost = fix('1', '5000')

    outcome = 0
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    fillOrder.publicFillOrder(orderID, fix(1), tradeGroupID, sender = tester.k1, value=cost)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == FILL_ORDER_BOTH_ETH[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_order_filling_maker_reverse(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    cost = fix('1', '5000')

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a2, 100)
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    fillOrder.publicFillOrder(orderID, fix(1), tradeGroupID, sender = tester.k1, value=cost)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == FILL_ORDER_MAKER_REVERSE_POSITION[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_order_filling_taker_reverse(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    cost = fix('1', '5000')

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000, sender = tester.k2)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a1, 100, sender = tester.k2)
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    fillOrder.publicFillOrder(orderID, fix(1), tradeGroupID, sender = tester.k1, value=cost)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == FILL_ORDER_TAKER_REVERSE_POSITION[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_order_filling_double_reverse(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder2']
    completeSets = localFixture.contracts['CompleteSets']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    cost = fix('1', '5000')

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a1, 100)
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    fillOrder.publicFillOrder(orderID, fix(1), tradeGroupID, sender = tester.k1, value=cost)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == FILL_ORDER_DOUBLE_REVERSE_POSITION[marketIndex]


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    cash = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    fixture.markets = [
        fixture.createReasonableCategoricalMarket(universe, 2, cash),
        fixture.createReasonableCategoricalMarket(universe, 3, cash),
        fixture.createReasonableCategoricalMarket(universe, 4, cash),
        fixture.createReasonableCategoricalMarket(universe, 5, cash),
        fixture.createReasonableCategoricalMarket(universe, 6, cash),
        fixture.createReasonableCategoricalMarket(universe, 7, cash),
        fixture.createReasonableCategoricalMarket(universe, 8, cash)
    ]

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def universe(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@fixture
def markets(localFixture, kitchenSinkSnapshot):
    return localFixture.markets