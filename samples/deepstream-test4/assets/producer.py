import time
from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='192.168.1.9:9092',
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

idx = 0
while True:
    data = {'idx': idx}
    producer.send('test', value=data)
    print(data)
    time.sleep(0.03)
    idx += 1