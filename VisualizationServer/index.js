const {Worker, isMainThread } = require("worker_threads");
const express = require('express')
const webserver = express()
  .use((req, res) =>
    res.sendFile('/websocket-client.html', { root: __dirname })
  )
  .listen(3000, () => console.log(`Listening on ${3000}`))

const { WebSocketServer } = require('ws')
const sockserver = new WebSocketServer({ port: 443 })
sockserver.on('connection', (ws, req) => {
  console.log("Connection from " + req.socket.remoteAddress + ":" + req.socket.remotePort);
  console.log('New client connected!')
  ws.send('connection established')
  ws.on('close', () => console.log('Client has disconnected!'))
  ws.on('message', data => {
    sockserver.clients.forEach(client => {
      console.log(`distributing message: ${data}`)
      client.send(`${data}`)
    })
  })
  ws.onerror = function () {
    console.log('websocket error')
  }
})


workerData = {}
const kafka_worker = new Worker("./kafka_consumer.js", {workerData:"Hello"});
kafka_worker.on("message", data => {console.log(JSON.stringify(data.message));
				    sockserver.clients.forEach(client =>{
					    console.log(`distributing message: ${data}`)
					client.send(`${data.message}`)})});
kafka_worker.on("error", code => new Error(`Worker error with exit code ${code}`));
kafka_worker.on("exit", code => console.log(`Worker stopped with exit code ${code}`));
