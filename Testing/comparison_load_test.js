import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 100 }, // Ramp-up to 100 users over 1 minute
    { duration: '3m', target: 400 }, // Hold at 100 users for 3 minutes
    { duration: '30s', target: 100 },   // Ramp-down to 0 users over 1 second
  ],
};

// Main test function
export default function () {
  const url1 = 'http://127.0.0.1:7080/'; // Fast API HPA Endpoint
  const url2 = 'http://127.0.0.1:9080/'; // MY APP Endpoint

  let metricsData = [];

  // Function to perform the HTTP request and collect metrics
  function testEndpoint(url) {
    let response;
    let endpointMetrics = {};

    try {
      // Make an HTTP GET request
      response = http.get(url);

      // Check the response status and body
      check(response, {
          'status is 200': (r) => r.status === 200,
          'response contains expected text': (r) =>
            r.body && r.body.includes('Counted till random number: '),
        });
      // if (response && response.body) {
      //   check(response, {
      //     'status is 200': (r) => r.status === 200,
      //     'response contains expected text': (r) =>
      //       r.body && r.body.includes('Counted till random number: '),
      //   });
      //
      // } else {
      //   console.warn(`Response body is null or undefined for ${url}. Skipping validation.`);
      // }

      // Collect metrics for the endpoint
      endpointMetrics = {
        url: url,
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
      console.error(`Request failed for ${url}: ${error.message}`);

      endpointMetrics = {
        url: url,
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

    return endpointMetrics;
  }

  // Test both endpoints and log metrics
  metricsData.push(testEndpoint(url1));
  metricsData.push(testEndpoint(url2));

  // Log metrics for both endpoints
  metricsData.forEach((data) => {
    console.log(JSON.stringify(data));
  });

  sleep(1); // Simulate user think time
}