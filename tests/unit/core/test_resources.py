import mock
import os

from boto3.core.connection import ConnectionFactory
from boto3.core.exceptions import APIVersionMismatchError
from boto3.core.resources import ResourceJSONLoader, ResourceDetails
from boto3.core.resources import Resource, ResourceFactory
from boto3.core.session import Session

from tests import unittest
from tests.unit.fakes import FakeParam, FakeOperation, FakeService, FakeSession


class TestCoreService(FakeService):
    api_version = '2013-08-23'
    operations = [
        FakeOperation(
            'CreateQueue',
            " <p>Creates a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
                FakeParam('Attributes', required=False, ptype='map'),
            ],
            output={
                'shape_name': 'CreateQueueResult',
                'type': 'structure',
                'members': {
                    'QueueUrl': {
                        'shape_name': 'String',
                        'type': 'string',
                        'documentation': '\n    <p>The URL for the created SQS queue.</p>\n  ',
                    },
                },
            },
            result=(None, {
                'QueueUrl': 'http://example.com',
            })
        ),
        FakeOperation(
            'SendMessage',
            " <p>Sends a message to a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
                FakeParam('MessageBody', required=True, ptype='string'),
                FakeParam('MessageType', required=False, ptype='string'),
            ],
            output=True,
            result=(None, True)
        ),
        FakeOperation(
            'ReceiveMessage',
            " something something something ",
            params=[
                FakeParam('QueueUrl', required=True, ptype='string'),
                FakeParam('AttributeNames', required=False, ptype='list'),
                FakeParam('MaxNumberOfMessages', required=False, ptype='integer'),
                FakeParam('VisibilityTimeout', required=False, ptype='integer'),
                FakeParam('WaitTimeSeconds', required=False, ptype='integer'),
            ],
            output={
                'shape_name': 'ReceiveMessageResult',
                'type': 'structure',
                'members': {
                    'Messages': {
                        'shape_name': 'MessageList',
                        'type': 'list',
                        'members': {
                            'shape_name': 'Message',
                            'type': 'structure',
                            'members': {
                                'MessageId': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'ReceiptHandle': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'MD5OfBody': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'Body': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'Attributes': {
                                    'shape_name': 'AttributeMap',
                                    'type': 'map',
                                    'keys': {
                                        'shape_name': 'QueueAttributeName',
                                        'type': 'string',
                                        'enum': [
                                            'Policy',
                                            'VisibilityTimeout',
                                            'MaximumMessageSize',
                                            'MessageRetentionPeriod',
                                            'ApproximateNumberOfMessages',
                                            'ApproximateNumberOfMessagesNotVisible',
                                            'CreatedTimestamp',
                                            'LastModifiedTimestamp',
                                            'QueueArn',
                                            'ApproximateNumberOfMessagesDelayed',
                                            'DelaySeconds',
                                            'ReceiveMessageWaitTimeSeconds'
                                        ],
                                        'documentation': '\n    <p>The name of a queue attribute.</p>\n  ',
                                        'xmlname': 'Name'
                                    },
                                    'members': {
                                        'shape_name': 'String',
                                        'type': 'string',
                                        'documentation': '\n    <p>The value of a queue attribute.</p>\n  ',
                                        'xmlname': 'Value'
                                    },
                                    'flattened': True,
                                    'xmlname': 'Attribute',
                                    'documentation': None,
                                },
                            },
                            'documentation': None,
                            'xmlname': 'Message'
                        },
                        'flattened': True,
                        'documentation': '\n    <p>A list of messages.</p>\n  '
                    }
                },
                'documentation': None
            },
            result=(None, {
                'Messages': [
                    {
                        'MessageId': 'msg-12345',
                        'ReceiptHandle': 'hndl-12345',
                        'MD5OfBody': '6cd3556deb0da54bca060b4c39479839',
                        'Body': 'Hello, world!',
                        'Attributes': {
                            'QueueArn': 'arn:aws:example:example:sqs:something',
                            'ApproximateNumberOfMessagesDelayed': '2',
                            'DelaySeconds': '10',
                            'CreatedTimestamp': '2013-10-17T21:52:46Z',
                            'LastModifiedTimestamp': '2013-10-17T21:52:46Z',
                        },
                    },
                    {
                        'MessageId': 'msg-12346',
                        'ReceiptHandle': 'hndl-12346',
                        'MD5OfBody': '6cd355',
                        'Body': 'Another message!',
                        'Attributes': {},
                    },
                ]
            })
        ),
        FakeOperation(
            'DeleteQueue',
            " <p>Deletes a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
            ],
            output=True,
            result=(None, True)
        ),
    ]


class ResourceDetailsTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceDetailsTestCase, self).setUp()
        self.test_dirs = [
            os.path.join(os.path.dirname(__file__), 'test_data')
        ]
        self.test_loader = ResourceJSONLoader(self.test_dirs)
        self.session = Session(FakeSession(TestCoreService()))

        self.rd = ResourceDetails(
            self.session,
            'test',
            'Preset',
            loader=self.test_loader
        )

    def test_init(self):
        self.assertEqual(self.rd.session, self.session)
        self.assertEqual(self.rd.service_name, 'test')
        self.assertEqual(self.rd.loader, self.test_loader)
        self.assertEqual(self.rd._loaded_data, None)
        self.assertEqual(self.rd._api_versions, None)

    def test_service_data_uncached(self):
        self.assertEqual(self.rd._loaded_data, None)

        data = self.rd.service_data
        self.assertEqual(len(data.keys()), 4)
        self.assertTrue('api_versions' in self.rd._loaded_data)

    def test_resource_data_uncached(self):
        self.assertEqual(self.rd._loaded_data, None)

        data = self.rd.resource_data
        self.assertEqual(len(data.keys()), 4)
        self.assertTrue('identifier' in data)
        self.assertTrue('operations' in data)
        self.assertTrue('api_versions' in self.rd._loaded_data)

    def test_api_version_uncached(self):
        self.assertEqual(self.rd._api_versions, None)

        av = self.rd.api_versions
        self.assertEqual(av, [
            '2012-09-25',
        ])
        self.assertEqual(self.rd._api_versions, [
            '2012-09-25',
        ])

    def test_cached(self):
        # Fake in data.
        self.rd._loaded_data = {
            'api_versions': [
                '20XX-MM-II',
            ],
            'hello': 'world',
        }

        data = self.rd.service_data
        av = self.rd.api_versions
        self.assertTrue('hello' in data)
        self.assertTrue('20XX-MM-II' in av)


class FakeConn(object):
    def __init__(self, *args, **kwargs):
        super(FakeConn, self).__init__()

    def delete_pipeline(self, *args, **kwargs):
        return {
            'RequestId': '1234-1234-1234-1234',
            'Id': '1872baf45',
            'Title': 'A pipe',
        }


class PipeResource(Resource):
    def update_params(self, conn_method_name, params):
        params['global'] = True
        return super(PipeResource, self).update_params(conn_method_name, params)

    def update_params_delete(self, params):
        params['id'] = self.get_identifier()
        return params

    def post_process(self, conn_method_name, result):
        self.identifier = result.pop('Id')
        return result

    def post_process_delete(self, result):
        self.deleted = True
        return result


class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.fake_details = ResourceDetails(self.session, 'test', 'Pipe')
        self.fake_details._loaded_data = {
            'api_versions': ['something'],
            'resources': {
                'Pipe': {
                    'identifier': {
                        'var_name': 'id',
                        'api_name': 'Id',
                    },
                    'operations': {
                        'delete': {
                            'api_name': 'DeletePipe',
                            'docs': '',
                            'params': {},
                        }
                    }
                }
            }
        }
        self.fake_conn = FakeConn()
        PipeResource._details = self.fake_details
        self.resource = PipeResource(
            connection=self.fake_conn,
            id='1872baf45'
        )

    def tearDown(self):
        del PipeResource._details
        super(ResourceTestCase, self).tearDown()

    def test_full_update_params(self):
        params = {
            'notify': True,
        }
        prepped = self.resource.full_update_params('delete', params)
        self.assertEqual(prepped, {
            'global': True,
            'id': '1872baf45',
            'notify': True,
        })

    def test_full_post_process(self):
        results = {
            'Id': '1872baf45',
            'Title': 'A pipe',
        }
        processed = self.resource.full_post_process('delete', results)
        self.assertEqual(processed, {
            'Title': 'A pipe'
        })
        self.assertEqual(self.resource.deleted, True)


class ResourceFactoryTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceFactoryTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.test_dirs = [
            os.path.join(os.path.dirname(__file__), 'test_data')
        ]
        self.test_loader = ResourceJSONLoader(self.test_dirs)
        self.rd = ResourceDetails(
            self.session,
            'test',
            'Preset',
            loader=self.test_loader
        )
        self.rf = ResourceFactory(session=self.session, loader=self.test_loader)

    def test_init(self):
        self.assertEqual(self.rf.session, self.session)
        self.assertTrue(isinstance(self.rf.loader, ResourceJSONLoader))
        self.assertEqual(self.rf.base_resource_class, Resource)
        self.assertEqual(self.rf.details_class, ResourceDetails)

        # Test overrides (invalid for actual usage).
        import boto3
        rf = ResourceFactory(
            loader=False,
            base_resource_class=PipeResource,
            details_class=True
        )
        self.assertEqual(rf.session, boto3.session)
        self.assertEqual(rf.loader, False)
        self.assertEqual(rf.base_resource_class, PipeResource)
        self.assertEqual(rf.details_class, True)

    def test_build_class_name(self):
        self.assertEqual(
            self.rf._build_class_name('Pipeline'),
            'PipelineResource'
        )
        self.assertEqual(
            self.rf._build_class_name('TestName'),
            'TestNameResource'
        )

    def test_build_methods(self):
        attrs = self.rf._build_methods(self.rd)
        self.assertEqual(len(attrs), 1)
        self.assertTrue('delete' in attrs)

    def test_create_operation_method(self):
        class StubbyResource(Resource):
            pass

        op_method = self.rf._create_operation_method('delete', {
            "api_name": "DeletePipeline",
            "docs": "Dusts off & nukes a pipeline from orbit.",
            "params": {
                "id": {
                    "api_name": "Id",
                    "type": "string"
                }
            }
        })
        self.assertEqual(op_method.__name__, 'delete')
        self.assertEqual(
            op_method.__doc__,
            'Dusts off & nukes a pipeline from orbit.'
        )

        # Assign it & call it.
        StubbyResource._details = self.rd
        StubbyResource.delete = op_method
        sr = StubbyResource(connection=FakeConn())
        self.assertEqual(sr.delete(), {
            'Id': '1872baf45',
            'RequestId': '1234-1234-1234-1234',
            'Title': 'A pipe'
        })

    def test_construct_for(self):
        res_class = self.rf.construct_for('test', 'Pipeline')