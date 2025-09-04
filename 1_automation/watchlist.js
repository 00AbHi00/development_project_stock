const express = require('express')
const app= express()
const port =8000
const path=require('path')
const fs= require('fs')

app.listen(port,()=>
{
    console.log("server running")
})

app.get('/',(req,res)=>{
    res.send('Hello')
})

app.get('/update',(req,res)=>{
    res.sendFile(path.join(__dirname,'frontend','index.html',))
})



