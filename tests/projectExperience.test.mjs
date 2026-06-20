import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import test from 'node:test';

import {
  buildExperienceUrl,
  parseExperienceState,
} from '../src/lib/projectExperience.ts';

const slugs = ['heaven', 'lady', 'white-collared-dreams'];

test('parses project and view from a homepage URL', () => {
  assert.deepEqual(
    parseExperienceState('https://example.com/?project=heaven&view=info', slugs),
    {
      projectSlug: 'heaven',
      view: 'info',
    }
  );
});

test('ignores invalid project and view values', () => {
  assert.deepEqual(
    parseExperienceState('https://example.com/?project=unknown&view=cast', slugs),
    {
      projectSlug: null,
      view: null,
    }
  );
});

test('drops a valid view when no valid project is open', () => {
  assert.deepEqual(parseExperienceState('https://example.com/?view=bts', slugs), {
    projectSlug: null,
    view: null,
  });
});

test('builds URL state for player and detail page states', () => {
  assert.equal(
    buildExperienceUrl('https://example.com/?project=heaven', {
      projectSlug: 'lady',
      view: 'credits',
    }),
    'https://example.com/?project=lady&view=credits'
  );

  assert.equal(
    buildExperienceUrl('https://example.com/?project=lady&view=credits', {
      projectSlug: null,
      view: null,
    }),
    'https://example.com/'
  );
});

test('removes stale panel params when building view URLs', () => {
  assert.equal(
    buildExperienceUrl('https://example.com/?project=heaven&panel=info', {
      projectSlug: 'heaven',
      view: 'bts',
    }),
    'https://example.com/?project=heaven&view=bts'
  );
});

test('project content is wired to the four Cloudinary project folders', () => {
  const projectDir = new URL('../src/content/projects/', import.meta.url);
  const files = readdirSync(projectDir).filter((file) => file.endsWith('.md')).sort();

  assert.deepEqual(files, ['heaven.md', 'lady.md', 'one-call.md', 'sunkissed.md']);

  for (const file of files) {
    const slug = file.replace(/\.md$/, '');
    const content = readFileSync(new URL(file, projectDir), 'utf8');
    assert.match(content, new RegExp(`simply-living/projects/${slug}/`));
    assert.doesNotMatch(content, /samples\//);
  }
});

test('one call is represented as an image-first project', () => {
  const oneCall = readFileSync(
    new URL('../src/content/projects/one-call.md', import.meta.url),
    'utf8'
  );

  assert.match(oneCall, /heroImage: "simply-living\/projects\/one-call\/gallery\/01"/);
  assert.doesNotMatch(oneCall, /heroVideo:/);
  assert.doesNotMatch(oneCall, /fullVideo:/);
});

test('video-first projects declare stable full player durations', () => {
  const projectDir = new URL('../src/content/projects/', import.meta.url);
  const files = readdirSync(projectDir).filter((file) => file.endsWith('.md')).sort();

  for (const file of files) {
    const content = readFileSync(new URL(file, projectDir), 'utf8');

    if (content.match(/^fullVideo:/m)) {
      assert.match(content, /^fullVideoDuration: \d+(\.\d+)?$/m, file);
    }
  }
});

test('custom player exposes play pause controls without native controls', () => {
  const component = readFileSync(
    new URL('../src/components/svelte/ProjectExperience.svelte', import.meta.url),
    'utf8'
  );

  assert.match(component, /togglePlayerPlayback/);
  assert.match(component, /aria-label=\{isPlayerPaused \? 'Play video' : 'Pause video'\}/);
  assert.doesNotMatch(component, /\scontrols\s/);
});
