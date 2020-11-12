import os
import consumer
from multiprocessing import Process
from multiprocessing import Pool


NUM_CONSUMERS = os.getenv('NUM_CONSUMERS', 1)


if __name__ == '__main__':
    with Pool(int(NUM_CONSUMERS)) as p:
        p.map(consumer.consume, list(range(1, int(NUM_CONSUMERS) + 1)))
