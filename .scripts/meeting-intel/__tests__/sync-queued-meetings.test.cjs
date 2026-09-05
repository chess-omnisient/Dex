'use strict';

const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { PassThrough } = require('node:stream');
const https = require('node:https');
const test = require('node:test');

const { getNewMeetingsFromApi } = require('../sync-from-granola.cjs');

test('API sync skips queued meetings unless force-today is set', async (t) => {
  const originalRequest = https.request;
  const detailRequests = [];
  const createdAt = new Date().toISOString();

  https.request = (url, options, callback) => {
    const request = new EventEmitter();
    request.destroy = () => {};
    request.end = () => setImmediate(() => {
      const response = new PassThrough();
      response.statusCode = 200;
      response.headers = {};
      callback(response);

      const isDetailRequest = String(url).includes('include=transcript');
      if (isDetailRequest) detailRequests.push(String(url));
      const body = isDetailRequest
        ? {
            id: 'already-queued',
            title: 'Queued customer sync',
            created_at: createdAt,
            summary_text: 'This fixture has enough meaningful meeting content to pass the detail filter.',
          }
        : {
            notes: [{ id: 'already-queued', title: 'Queued customer sync', created_at: createdAt }],
            hasMore: false,
            cursor: null,
          };
      response.end(JSON.stringify(body));
    });
    return request;
  };
  t.after(() => {
    https.request = originalRequest;
  });

  const state = {
    processedMeetings: {},
    queuedMeetings: {
      'already-queued': { queueFile: 'already-queued.json' },
    },
  };

  const ordinaryMeetings = await getNewMeetingsFromApi('fixture-key', state);
  assert.deepEqual(ordinaryMeetings, []);
  assert.equal(detailRequests.length, 0);

  const forcedMeetings = await getNewMeetingsFromApi('fixture-key', state, true);
  assert.deepEqual(forcedMeetings.map((meeting) => meeting.id), ['already-queued']);
  assert.equal(detailRequests.length, 1);
});
