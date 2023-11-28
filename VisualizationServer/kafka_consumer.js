console.log("In Worker")
const {workerData, parentPort, isMainThread} = require("worker_threads");


const ip = require('ip')
const {Kafka} = require('kafkajs')

const kafka = new Kafka({
  clientId: 'PawPrints-CNC',
  brokers: ['localhost:9092', 'localhost:9092'],
})

const consumer = kafka.consumer({ groupId: 'test-group' })
const host = process.env.HOST_IP || ip.address()

const topic = 'sampleTopic'


const run = async () => {
    await consumer.connect()
    console.log("Kafka Consumer connected to broker.");
    await consumer.subscribe({ topic, fromBeginning: true })
    await consumer.run({
	eachMessage: async ({ topic, partition, message }) => {
	    console.log("received message" + `${message}`);
	    const prefix = `${topic}[${partition}] / ${message.timestamp}`
	    formatted_message = `- ${prefix} #${message.value}`
	    console.log(formatted_message)
	    parentPort.postMessage({message: formatted_message, topic: topic });
    },
  })
}

run().catch(e => console.error(`[example/consumer] ${e.message}`, e))
