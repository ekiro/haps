.. _profiles:

Profiles
=================================

Haps allows you to attach dependencies to configuration profile. It helps
with development, testing, and some other stuff. You can set active profiles
using :class:`~haps.config.Configuration`.

Example
---------------------------------

One of many good use cases for profiles is mailing. Imagine you have to
implement mailer class. Your production environment uses AWS SES, stage
uses an internal SMTP system, on your local env every mail is printed to
stdout, and mailer for tests do nothing. You may ask, how to implement this
without nasty ifs? Well, it's quite easy with profiles:


.. code-block:: python

    from haps import base, egg


    @base
    class IMailer
        def send(self, to: str, message: str) -> None:
            raise NotImplementedError


    @egg(profile='production')
    class SESMailer(IMailer):
        def send(self, to: str, message: str) -> None:
            # SES implementation


    @egg(profile='stage')
    class SMTPMailer(IMailer):
        def send(self, to: str, message: str) -> None:
            # SMTP implementation


    @egg(profile='tests')
    class DummyMailer(IMailer):
        def send(self, to: str, message: str) -> None:
            pass


    @egg  # missing profile means default
    class LogMailer(IMailer):
        def send(self, to: str, message: str) -> None:
            print(f"Mail to {to}: {message})


And that's it. Now you only need to run your app with :code:`HAPS_PROFILES=production`
(or any other profile) and haps will choose proper dependency. You can set more than
one profile separating them by a comma: :code:`HAPS_PROFILES=stage,local-static,sqlite`

If there is more than one egg for the given profiles list, the order decides about
priority. e.g. for :code:`HAPS_PROFILES=tests,production` the :code:`DummyMailer`
class is chosen.

Profiles can be configured programmatically, **before** Container configuration:

.. code-block:: python

    from haps import PROFILES
    from haps.config import Configuration


    Configuration().set(PROFILES, ('tests', 'tmp-static', 'sqlite'))
    # Container config / autodiscover


.. note::
    Profiles that are set directly by :class:`~haps.config.Configuration`
    overrides profiles from the environment variable.
