# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from product.porter.testing import PRODUCT_PORTER_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that product.porter is properly installed."""

    layer = PRODUCT_PORTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if product.porter is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'product.porter'))

    def test_browserlayer(self):
        """Test that IProductPorterLayer is registered."""
        from product.porter.interfaces import (
            IProductPorterLayer)
        from plone.browserlayer import utils
        self.assertIn(IProductPorterLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PRODUCT_PORTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['product.porter'])

    def test_product_uninstalled(self):
        """Test if product.porter is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'product.porter'))

    def test_browserlayer_removed(self):
        """Test that IProductPorterLayer is removed."""
        from product.porter.interfaces import \
            IProductPorterLayer
        from plone.browserlayer import utils
        self.assertNotIn(IProductPorterLayer, utils.registered_layers())
