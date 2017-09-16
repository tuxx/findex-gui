class AmqpSend:
    def __init__(self):
        self.amqp_queue_name = settings.amqp_queue_name
        self.amqp_username = settings.amqp_username
        self.amqp_password = settings.amqp_password
        self.amqp_host = settings.amqp_host
        self.amqp_vhost = settings.amqp_vhost

        self.channel = None
        self.connection = None

        creds = credentials.PlainCredentials(username=self.amqp_username, password=self.amqp_password, erase_on_connect=True)
        params = pika.ConnectionParameters(host=self.amqp_host, port=5672, virtual_host=self.amqp_vhost, credentials=creds)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=self.amqp_queue_name, durable=True)

        self.channel = channel
        self.connection = connection

    @staticmethod
    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def send_tasks(self, resources):
        """
        converts resource objects to crawl requests
        :param resources: a list of resources
        :return:
        """
        tasks = []

        for resource in resources:
            t = {
                "address": resource.server.address,
                "method": FileProtocols().name_by_id(resource.protocol),
                "basepath": resource.basepath,
                "resource_id": resource.id,
                "options": {
                    "user-agent": resource.meta.web_user_agent,
                    "recursive_foldersizes": True,
                    "port": resource.port,
                    "auth_user": resource.meta.auth_user,
                    "auth_pass": resource.meta.auth_pass
                }
            }
            tasks.append(t)

        for t in tasks:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.amqp_queue_name,
                                       body=json.dumps(t),
                                       properties=pika.BasicProperties(
                                           delivery_mode=2
                                       ))

        print(" [x] Sent %s tasks to queue %s" % (str(len(tasks)), self.amqp_queue_name))
        self.connection.close()
