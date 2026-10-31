// schema-load.js - the indexed schema, loaded once for modules that only need
// labels (the Library drawer, the kit recipe). main.js loads its own copy for
// the panels; this one is the same file, fetched without a token.

import {loadStatic} from './api.js';
import {indexSchema} from './schema.js';

let promise = null;

export function schemaIndex() {
  if (!promise) promise = loadStatic('/schema/silica_keys.json').then(indexSchema, (error) => { promise = null; throw error; });
  return promise;
}
