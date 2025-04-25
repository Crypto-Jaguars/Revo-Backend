import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '20s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% requests <500ms
    http_req_failed: ['rate<0.01'], // <1% errors
  },
};

export default function () {
  const res = http.get(
    'http://localhost:3000/products/f9648213-dd26-4aeb-9317-fc5668e02369',
  );

  check(res, {
    'Status is 200': (r) => r.status === 200,
    'Response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
