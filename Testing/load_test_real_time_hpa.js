import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 20 }, // Ramp-up to 50 users over 30 seconds
    { duration: '1m', target: 20 },  // Hold at 50 users for 1 minute
    { duration: '30s', target: 0 },  // Ramp-down to 0 users over 30 seconds
  ],
};

// Main test function
export default function () {
  const url = 'http://127.0.0.1:9080/'; // Replace with your API endpoint

  let response;
  let metricsData = {};

  try {
    // Make an HTTP GET request
    response = http.get(url);

    // Check if the response body is valid before attempting to access it
    if (response && response.body) {
      check(response, {
        'status is 200': (r) => r.status === 200,
        'response contains expected text': (r) =>
          r.body && r.body.includes('Counted till random number: '),
      });
    } else {
      console.warn('Response body is null or undefined. Skipping validation of body contents.');
    }

    // Collect metrics
    metricsData = {
      timestamp: new Date().toISOString(),
      vus: __VU, // Number of active virtual users
      iterations: __ITER, // Current iteration
      http_req_duration: response ? response.timings.duration : null, // Duration of the request
      http_req_waiting: response ? response.timings.waiting : null,   // Time spent waiting for the response
      http_req_failed: response ? (response.status !== 200 ? 1 : 0) : 1, // Failed requests
      iteration_duration: response ? Date.now() - response.timings.start : null, // Duration of the iteration
      http_reqs: 1, // Total HTTP requests
    };
  } catch (error) {
    // Handle exceptions and unexpected errors
    console.error(`Request failed: ${error.message}`);

    metricsData = {
      timestamp: new Date().toISOString(),
      vus: __VU, // Number of active virtual users
      iterations: __ITER, // Current iteration
      http_req_duration: null, // No duration because the request failed
      http_req_waiting: null,   // No waiting time because the request failed
      http_req_failed: 1, // Mark request as failed
      iteration_duration: null, // Cannot calculate iteration duration
      http_reqs: 0, // No HTTP requests recorded
    };
  }

  // Log metrics data
  console.log(JSON.stringify(metricsData));

  sleep(1); // Simulate user think time
}
