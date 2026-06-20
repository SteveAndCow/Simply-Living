export type ProjectView = 'bts' | 'info' | 'credits';

export interface ExperienceState {
  projectSlug: string | null;
  view: ProjectView | null;
}

const views = new Set<ProjectView>(['bts', 'info', 'credits']);

export function isProjectView(value: string | null): value is ProjectView {
  return value === 'bts' || value === 'info' || value === 'credits';
}

export function parseExperienceState(inputUrl: string | URL, validSlugs: string[]): ExperienceState {
  const url = typeof inputUrl === 'string' ? new URL(inputUrl) : inputUrl;
  const project = url.searchParams.get('project');
  const view = url.searchParams.get('view');
  const hasProject = project !== null && validSlugs.includes(project);

  return {
    projectSlug: hasProject ? project : null,
    view: hasProject && isProjectView(view) && views.has(view) ? view : null,
  };
}

export function buildExperienceUrl(inputUrl: string | URL, state: ExperienceState): string {
  const url = typeof inputUrl === 'string' ? new URL(inputUrl) : new URL(inputUrl.toString());

  if (state.projectSlug) {
    url.searchParams.set('project', state.projectSlug);
  } else {
    url.searchParams.delete('project');
  }

  url.searchParams.delete('panel');

  if (state.projectSlug && state.view) {
    url.searchParams.set('view', state.view);
  } else {
    url.searchParams.delete('view');
  }

  return url.toString();
}
