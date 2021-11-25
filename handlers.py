from aiohttp import web

from ww3 import Bsc, web3

app = web.Application(debug=True)
routes = web.RouteTableDef()


@routes.post('/balance/')
async def get_balance(request):
    data = await request.post()
    bsc = Bsc(address=data['address'], private_key=data['private_key'])

    return web.json_response({'result': str(bsc.balance),
                              'human_readable': f'{web3.fromWei(bsc.balance, "ether")} '
                                                f'{bsc.contract.functions.symbol().call()}'
                              })


@routes.post('/sell/')
async def sell_token(request):
    data = await request.post()
    bsc = Bsc(address=data['address'], private_key=data['private_key'])

    response = Bsc.sell_token(data['contract_id'], data['amount'])
    return web.json_response({'result': response})


@routes.post('/buy/')
async def buy_token(request):
    data = await request.post()
    bsc = Bsc(address=data['address'], private_key=data['private_key'])

    response = Bsc.buy_token(data['token_to_buy'], data['amount'])
    return web.json_response({'result': response})


@routes.post('/get_currency/')
async def get_currency(request):
    data = await request.post()
    bsc = Bsc(address=None, private_key=None)

    return web.json_response({'course': bsc.get_currency(data["token_address"])})

