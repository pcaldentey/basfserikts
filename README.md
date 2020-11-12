# basfserikts

## How to run this software

We use several docker containers for running this software

So run:

    docker-compose up


Once all containers are up and running you must go to [*http://0.0.0.0/docs* ](http://0.0.0.0/docs) and upload the patents file

In a minute you will see traces like this

    INFO:root:consumer patents1: 100 messages consumed

Then the process is running

You can check the evolution of the process in the database

    psql -h localhost -p 5432 -U jat -d jat_db

Or checking the rabbit queues in the container

    rabbitmqctl list_queues

## Description, techs and design decisions

* api container: frontend of this software. REST API built with [FastAPI](https://fastapi.tiangolo.com/). Go to [*http://0.0.0.0/docs*](http://0.0.0.0/docs).
    * Code: api folder
    * Desc: Two endpoints. **upload_file** will take care of big zip file, and **clear** will empty database and rabbit queues
* dev_rabbit container: Queues. Api upload_file endpoint unzips patents file and sends each of one of the xml patent files to rabbitmq (this container)
* dev_postgresql container: Database, postgresql.
* dev_worker container: Runs different consumers, one for each queue defined. Multiprocessing
    * Code: worker folder
    * Desc: launcher.py will launch so many consumers (consumer.py) as queues exists (queue names: patents1, patents2,..). Each consumer conects to rabbitmq and to postgresql and calls to pipeline
        class (pipeline.py) where the pipeline is defined.

### Desing decisions

* rabbit: just a matter of deeper knowledge in developer side.
* Database: just a matter of deeper knowledge in developer side
* Api: Big zipfile is unzipped inside **upload_file** endpoint. This is WRONG, is the first weak point of this design. We should unzip the file in a background job, and not in the environment of an
    api call. You can take down the container with a bunch of concurrent calls. We do this in order to simplify, we could queue this files in a shared folder(S3) and unzip it and queue the xml files
    in a background job
* Consumer/Pipeline: Due to a lack of knowledge and time I decided to develop a hand-made solution. But with enough time I would use an workflow orchestrator, airflow type, and containerize each step
    of the pipeline, using i.e. kubernetes, calling these containers within workflow, in this way we would have a scalable solution


## Potential challenges

* Maintanibility: Modify and deploy pipeline.py each time a change is required.
* Scalability: Limited to the number of process a container can handle. You can run more then one *worker* containers, but requires code changes in the producer (api) and in the consumer.
               Rabbitmq, is other limit that we could reach, we could use a rabbitmq cluster to mitigate it.
               API. Very limited as we said before, due to a bad design.
