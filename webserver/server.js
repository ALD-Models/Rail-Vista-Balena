const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 80;

// Create a server
const server = http.createServer((req, res) => {
  if (req.url === '/' || req.url === '/index.html') {
    // Serve index.html
    fs.readFile('index.html', (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading index.html');
      } else {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(data);
      }
    });
  } else if (req.url === '/favicon.ico') {
    // Serve favicon.ico
    const faviconPath = path.join(__dirname, 'favicon.ico');
    fs.readFile(faviconPath, (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading favicon.ico');
      } else {
        res.writeHead(200, { 'Content-Type': 'image/x-icon' });
        res.end(data);
      }
    });
  } else {
    // Handle other requests
    res.writeHead(404);
    res.end('Not found');
  }
});

// Start the server
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
