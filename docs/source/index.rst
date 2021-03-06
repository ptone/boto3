.. boto3 documentation master file, created by
   sphinx-quickstart on Wed Jul 10 15:24:23 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to boto3
================

Boto3 is a high-level interface to a growing number of Amazon Web
Services.


Requirements
------------

* Python 3.3+ first, but also works on Python 2.6+
* botocore==0.24.0
* six>=1.4.0
* jmespath==0.1.0
* python-dateutil>=2.1


Tutorials
---------

.. toctree::
   :maxdepth: 2

   tutorial/sqs


Design
------

.. toctree::
   :maxdepth: 1

   design/philosophy
   design/architecture
   design/resource_objects


Topics
------

.. toctree::
   :maxdepth: 1

   topics/configuration
   topics/sessions
   topics/connections
   topics/resources_collections
   topics/service_names


API References
--------------

Services
~~~~~~~~

.. toctree::
   :maxdepth: 1
   :glob:

   reference/*

Core
~~~~

.. toctree::
   :maxdepth: 1
   :glob:

   reference/*/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
