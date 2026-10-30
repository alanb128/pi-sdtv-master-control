const path = require( 'path' );
const axios = require('axios');
const express = require( 'express' );
const {env} = require('process');


// create an express app
const app = express();

// Set EJS as the view engine to display dynamic content
app.set('view engine', 'ejs');

// Supervisor environment variables provided by balena
const SUPERVISOR_ADDRESS = process.env.BALENA_SUPERVISOR_ADDRESS;
const SUPERVISOR_API_KEY = process.env.BALENA_SUPERVISOR_API_KEY;

// Device variables
const sw_version = env.SW_VERSION || "0.22";

app.get('/', async (req, res) => {
  try {
    // Query the supervisor state endpoint
    const response = await axios.get(`${SUPERVISOR_ADDRESS}/v2/device/name`, {
      headers: {
        'Authorization': `Bearer ${SUPERVISOR_API_KEY}`
      }
    });

    const variableValue = response.data.deviceName

    // Query the supervisor state endpoint
    const response2 = await axios.get(`${SUPERVISOR_ADDRESS}/v1/device`, {
      headers: {
        'Authorization': `Bearer ${SUPERVISOR_API_KEY}`
      }
    });

    const sw_commit = response2.data.commit.slice(0,6)

    // Pass the value to your EJS template
    res.render('index', { deviceName: variableValue, sw_ver: sw_version, my_com: sw_commit  });
  } catch (error) {
    console.error('Error contacting the balena supervisor API:', error.message);
    res.status(500).send('Error loading data');
  }
});

app.get( '/waveform', ( request, response ) => {
  response.sendFile( path.resolve( __dirname, 'src/waveform.html' ), {
    headers: {
      'Content-Type': 'text/html',
    }
  } );
} );

app.get( '/vectorscope', ( request, response ) => {
  response.sendFile( path.resolve( __dirname, 'src/vectorscope.html' ), {
    headers: {
      'Content-Type': 'text/html',
    }
  } );
} );

app.get( '/vumeter', ( request, response ) => {
  response.sendFile( path.resolve( __dirname, 'src/vumeter.html' ), {
    headers: {
      'Content-Type': 'text/html',
    }
  } );
} );

app.get( '/full_video', ( request, response ) => {
  response.sendFile( path.resolve( __dirname, 'src/full_video.html' ), {
    headers: {
      'Content-Type': 'text/html',
    }
  } );
} );

app.get( '/video_vu', ( request, response ) => {
  response.sendFile( path.resolve( __dirname, 'src/video_vu.html' ), {
    headers: {
      'Content-Type': 'text/html',
    }
  } );
} );

app.get( '/info', ( request, response ) => {
  response.sendFile( path.resolve( __dirname, 'src/info.html' ), {
    headers: {
      'Content-Type': 'text/html',
    }
  } );
} );

// send asset files
app.use( express.static('src' ) );

// server listens on port 80
const server = app.listen( 80, () => console.log( 'Express server started!' ) );
