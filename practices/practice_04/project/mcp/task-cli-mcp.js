#!/usr/bin/env node
// Minimal MCP-like JSON-RPC 2.0 server over stdio exposing one tool: task_count
// Content-Length framing is used. No external deps.

const fs = require('fs');

function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { return null; }
}

function countTasks(path, status) {
  const data = readJson(path);
  if (!data) return { error: { code: 'ENOFILE', message: `File not found or invalid JSON: ${path}` } };
  if (!Array.isArray(data)) return { error: { code: 'EBAD', message: 'Data is not an array' } };
  const s = status || 'all';
  if (!['open', 'done', 'all'].includes(s)) return { error: { code: 'EBADSTATUS', message: `Invalid status: ${s}` } };
  const filtered = s === 'all' ? data : data.filter((t) => t && t.status === s);
  return { result: { count: filtered.length, status: s } };
}

const tools = [{ name: 'task_count', description: 'Count tasks in JSON file', input_schema: {
  type: 'object', properties: { status: { enum: ['open','done','all'] }, path: { type: 'string' } }, required: []
} }];

function send(obj) {
  const s = JSON.stringify(obj);
  process.stdout.write(`Content-Length: ${Buffer.byteLength(s)}\r\n\r\n${s}`);
}

function handleCall(id, method, params) {
  if (method === 'initialize') {
    send({ jsonrpc: '2.0', id, result: { serverName: 'task-cli-mcp', protocolVersion: '2024-06-01' } });
    return;
  }
  if (method === 'tools/list') {
    send({ jsonrpc: '2.0', id, result: { tools } });
    return;
  }
  if (method === 'tools/call') {
    const name = params?.name;
    if (name !== 'task_count') {
      send({ jsonrpc: '2.0', id, error: { code: -32601, message: 'Tool not found' } });
      return;
    }
    const status = params?.arguments?.status || 'all';
    const path = params?.arguments?.path || 'data/tasks.json';
    const { result, error } = countTasks(path, status);
    if (error) {
      send({ jsonrpc: '2.0', id, error: { code: -32000, message: error.message, data: { code: error.code } } });
    } else {
      send({ jsonrpc: '2.0', id, result });
    }
    return;
  }
  send({ jsonrpc: '2.0', id, error: { code: -32601, message: 'Method not found' } });
}

// Simple Content-Length framed reader
let buf = Buffer.alloc(0);
process.stdin.on('data', (chunk) => {
  buf = Buffer.concat([buf, chunk]);
  while (true) {
    const headerEnd = buf.indexOf('\r\n\r\n');
    if (headerEnd === -1) break;
    const header = buf.slice(0, headerEnd).toString('utf8');
    const m = /Content-Length:\s*(\d+)/i.exec(header);
    if (!m) { buf = Buffer.alloc(0); break; }
    const len = parseInt(m[1], 10);
    const start = headerEnd + 4;
    if (buf.length < start + len) break;
    const body = buf.slice(start, start + len).toString('utf8');
    buf = buf.slice(start + len);
    let msg;
    try { msg = JSON.parse(body); } catch (e) { continue; }
    handleCall(msg.id, msg.method, msg.params);
  }
});

process.stdin.resume();
