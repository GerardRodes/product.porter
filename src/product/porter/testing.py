# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import product.porter


class ProductPorterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=product.porter)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'product.porter:default')


PRODUCT_PORTER_FIXTURE = ProductPorterLayer()


PRODUCT_PORTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCT_PORTER_FIXTURE,),
    name='ProductPorterLayer:IntegrationTesting'
)


PRODUCT_PORTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCT_PORTER_FIXTURE,),
    name='ProductPorterLayer:FunctionalTesting'
)


PRODUCT_PORTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PRODUCT_PORTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ProductPorterLayer:AcceptanceTesting'
)
