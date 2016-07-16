#!/usr/bin/env python
# -*- coding:utf8 -*-

import falcon
from models import *
import jinja2

api = application = falcon.API()

def render(template_file,params):
    loader = jinja2.FileSystemLoader('templates')
    render_env = jinja2.Environment(loader=loader)
    template = render_env.get_template(template_file)

    try:
        output = template.render(**params)
    except jinja2.UndefinedError as e:
        raise Exception(e)

    return output


class Test(object):
    def on_get(self, req, resp):
        table = req.get_param()
        result = ''
        resp.data = render(template_file=table,)
        resp.content_type = 'application/html'
        resp.status = falcon.HTTP_200


test = Test()
api.add_route('/test', test)
