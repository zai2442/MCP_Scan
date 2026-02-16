import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 200,
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
  thresholds: {
    http_req_duration: ['p(99)<300'], // P99 < 300ms
    errors: ['rate<0.001'], // Error rate < 0.1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000/api/v1';
// Need a valid job_id that exists. 
// Ideally we should insert one in setup() but k6 setup cannot do SQL directly easily without xk6-sql.
// We assume 'load-test-job' exists.

export function setup() {
  // Optional: Call an endpoint to create data if API supported it.
  // For now, we assume the DB has been seeded with 'load-test-job'.
}

export default function () {
  const jobId = 'load-test-job';
  const res = http.get(`${BASE_URL}/jobs/${jobId}/export`);
  
  const result = check(res, {
    'status is 200': (r) => r.status === 200,
    'file returned': (r) => r.json('file') === `${jobId}_result.json`,
  });

  errorRate.add(!result);
}
