from haps import base


@base
class IHeater:
    def heat(self) -> None:
        raise NotImplementedError


@base
class IPump:
    pass
