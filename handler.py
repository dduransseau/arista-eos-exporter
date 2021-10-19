import logging
import re
import socket


from aiohttp import web
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from prometheus_client.exposition import generate_latest

from collector import AristaMetricsCollector

class metricHandler:
    def __init__(self, config):
        self._config = config
        self._target = None

    def get(self, req):
        params = req.query
        # print(params)
        self._target = params.get('target')
        modules = params.get('modules')
        if modules:
            if re.match(r"^([a-zA-Z]+)(,[a-zA-Z]+)*$", modules):
                self._config['module_names'] = modules
            else:
                msg = 'Invalid modules specified'
                logging.error(msg)
                # resp.status = 404
                # resp.text = msg
                return web.Response(status=404, text=msg)

        # resp.headers['Content-Type'] = CONTENT_TYPE_LATEST
        if not self._target:
            msg = 'No target parameter provided!'
            logging.error(msg)
            # resp.status = 400
            # resp.text = msg
            return web.Response(status=400, text=msg)

        try:
            socket.getaddrinfo(self._target, None)
        except socket.gaierror as e:
            msg = f'Target does not exist in DNS: {e}'
            logging.error(msg)
            # resp.status = 400
            # resp.text = msg
            return web.Response(status=400, text=msg)

        else:
            registry = AristaMetricsCollector(
                self._config,
                target=self._target
                )

            collected_metric = generate_latest(registry)
            # resp.text = collected_metric
            return web.Response(headers={'Content-Type': CONTENT_TYPE_LATEST}, body=collected_metric)