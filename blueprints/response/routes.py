# coding=utf8
from __future__ import absolute_import

from .controllers import *

urlpatterns = [
    # interface
    ('/interface/<token>', check, 'GET'),
    ('/interface/<token>', receive, 'POST'),
]
