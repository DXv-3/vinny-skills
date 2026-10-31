#!/usr/bin/env node
// Wrapper to call explode.mjs from Python
import { explode } from './explode.mjs';
const topic = process.argv[2] || 'test';
console.log(JSON.stringify(explode(topic)));
