"use strict";
const express = require('express')
const path = require('path')
const app = express()
const port = 3000

const MongoClient = require('mongodb').MongoClient;
const dbUrl = '';
const dbName = '';
const dbCollectionName = '';
const dbClient = new MongoClient(dbUrl);
var db;
var collection;

dbClient.connect(function(err, client) {
  if(err !== null){
    throw new Error("DB connection error.")
  }
  console.log("Connected successfully to server")

  db = client.db(dbName)
  collection = db.collection(dbCollectionName);
});

const FIELDS = new Set(["email", "domain", "username", "password", "hash", "firstname", "lastname", "phone", "dumpsource"]);

async function search(searchTerm, field, limit, useRegex) {
  console.log("Searching: " + searchTerm + " " + field + " " + useRegex)
  var pr;
  if(useRegex) {
    pr = await collection.find({[field]: {"$regex": searchTerm}}).limit(limit).toArray()
  } else {
    pr = await collection.find({[field]: searchTerm}).limit(limit).toArray()
  }
  return pr
}

app.get('/search', function(req, res) {
  if(typeof req.query.field === "undefined" ||
     !FIELDS.has(req.query.field) ||
     typeof req.query.query === "undefined" ||
     typeof req.query.regex === "undefined" ||
     typeof req.query.limit === "undefined") {
    res.json({})
    return
  }
  var useRegex = (req.query.regex === "true")

  var limit = parseInt(req.query.limit)
  limit = limit !== NaN ? limit : 10; 
  limit = limit >= 0 ? limit : 10;
  
  search(req.query.query, req.query.field, limit, useRegex).then(function(items) {
    for(var item of items){
      delete item["_id"]
      delete item["domain"]
    }
    res.json({result:items})
  })
})

app.get('/', function(req, res) {
  res.sendFile("/index.html", {"root": path.join(__dirname, "html")})
})

app.get('/indexes', function(req, res) {
  res.sendFile("/indexes.html", {"root": path.join(__dirname, "html")})
})

app.get('/getIndexes', function(req, res) {
  collection.stats(function(err, result){
    var indexInfo = {totalIndexSize: result.totalIndexSize, indexSizes: result.indexSizes}
    res.json(indexInfo)
  })
})

app.get('/buildIndexes', function(req, res) {
  var fieldsArray = Array.from(FIELDS)
  for(var field of fieldsArray) {
    collection.createIndex({[field]: 1}, {partialFilterExpression: {[field]: {$exists: true}}})
  }
})

app.listen(port, () => console.log(`App listening on port ${port}!`))
