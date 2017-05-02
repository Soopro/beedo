# coding=utf8
from __future__ import absolute_import

from .controllers import *

urlpatterns = [
    # interface
    ('/<token>', check, 'GET'),
    ('/<token>', receive, 'POST'),
]
