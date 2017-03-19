#!/usr/bin/env python
# encoding=utf-8
from avengersassemble.application import create_app, celery

app = create_app()
app.app_context().push()
