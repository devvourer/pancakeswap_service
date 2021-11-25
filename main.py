from handlers import app, routes
from aiohttp import web


def main():
    app.add_routes(routes)
    web.run_app(app, host='localhost', port=8000)


if __name__ == '__main__':
    main()
