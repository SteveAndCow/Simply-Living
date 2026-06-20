<script lang="ts">
  import { onMount, tick } from 'svelte';
  import {
    buildExperienceUrl,
    parseExperienceState,
    type ProjectView,
  } from '@lib/projectExperience';

  type ProjectMedia = {
    type: 'image' | 'video';
    src: string;
    alt: string;
    caption?: string;
    layout?: 'small' | 'medium' | 'large' | 'wide';
  };

  type ProjectCredit = {
    role: string;
    name: string;
  };

  export type ExperienceProject = {
    slug: string;
    displayTitle: string;
    client: string;
    category: string;
    description: string;
    previewMedia:
      | { type: 'video'; src: string; poster: string }
      | { type: 'image'; src: string };
    fullMedia:
      | { type: 'video'; src: string; poster: string; duration?: number }
      | { type: 'image'; src: string };
    btsMedia: ProjectMedia[];
    info: {
      text: string[];
      media: ProjectMedia[];
    };
    credits: ProjectCredit[];
  };

  export let projects: ExperienceProject[] = [];

  const viewLabels: Record<ProjectView, string> = {
    bts: 'BTS',
    info: 'Info',
    credits: 'Credits',
  };

  const viewOrder: ProjectView[] = ['bts', 'info', 'credits'];

  let activeIndex = 0;
  let openProjectSlug: string | null = null;
  let activeView: ProjectView | null = null;
  let openedFromGesture = false;
  let mounted = false;
  let lastWheelAt = 0;
  let playerVideo: HTMLVideoElement | null = null;
  let playerShell: HTMLDivElement | null = null;
  let isPlayerPaused = true;
  let isPlayerMuted = false;
  let playerCurrentTime = 0;
  let playerDuration = 0;
  let previewVideos: HTMLVideoElement[] = [];
  let validSlugs: string[] = [];

  $: validSlugs = projects.map((project) => project.slug);
  $: activeProject = projects[activeIndex] ?? projects[0];
  $: openProject = projects.find((project) => project.slug === openProjectSlug) ?? null;
  $: isPlayerOpen = openProject !== null;
  $: playerDisplayDuration =
    openProject?.fullMedia.type === 'video' && openProject.fullMedia.duration
      ? openProject.fullMedia.duration
      : playerDuration;
  $: playerProgressPercent =
    playerDisplayDuration > 0
      ? Math.min(100, (playerCurrentTime / playerDisplayDuration) * 100)
      : 0;
  $: if (mounted && typeof document !== 'undefined') {
    document.body.classList.toggle('experience-open', isPlayerOpen);
  }

  onMount(() => {
    mounted = true;
    applyUrlState(window.location.href);
    window.addEventListener('popstate', handlePopState);
    window.addEventListener('keydown', handleKeydown);
    playActivePreview();

    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('keydown', handleKeydown);
      document.body.classList.remove('experience-open');
    };
  });

  function applyUrlState(url: string) {
    const previousView = activeView;
    const state = parseExperienceState(url, validSlugs);
    openProjectSlug = state.projectSlug;
    activeView = state.view;

    if (state.projectSlug) {
      const projectIndex = projects.findIndex((project) => project.slug === state.projectSlug);
      if (projectIndex >= 0) {
        activeIndex = projectIndex;
      }
    }

    if (!state.projectSlug) {
      openedFromGesture = false;
      isPlayerPaused = true;
      isPlayerMuted = false;
      playerCurrentTime = 0;
      playerDuration = 0;
    }

    if (previousView && !state.view && state.projectSlug) {
      restartPlayerVideo();
    }

    if (state.view) {
      resetPlayerVideo();
    }
  }

  function writeUrl(view: ProjectView | null, projectSlug = openProjectSlug, mode: 'push' | 'replace' = 'push') {
    if (!mounted) {
      return;
    }

    const nextUrl = buildExperienceUrl(window.location.href, {
      projectSlug,
      view,
    });

    if (nextUrl === window.location.href) {
      return;
    }

    if (mode === 'replace') {
      window.history.replaceState({}, '', nextUrl);
    } else {
      window.history.pushState({}, '', nextUrl);
    }
  }

  function handlePopState() {
    applyUrlState(window.location.href);
  }

  function handleKeydown(event: KeyboardEvent) {
    const isTypingTarget =
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement ||
      (event.target as HTMLElement | null)?.getAttribute?.('contenteditable') === 'true';

    if (isTypingTarget || projects.length === 0) {
      return;
    }

    if (event.key === 'Escape') {
      if (activeView) {
        event.preventDefault();
        returnToVideo();
      } else if (isPlayerOpen) {
        event.preventDefault();
        closePlayer();
      }
      return;
    }

    if (isPlayerOpen) {
      return;
    }

    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
      event.preventDefault();
      selectProject((activeIndex + 1) % projects.length);
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
      event.preventDefault();
      selectProject((activeIndex - 1 + projects.length) % projects.length);
    }
  }

  function selectProject(index: number) {
    if (index < 0 || index >= projects.length || index === activeIndex) {
      return;
    }

    activeIndex = index;
    playActivePreview();
  }

  async function playActivePreview() {
    await tick();

    previewVideos.forEach((video, index) => {
      if (!video) {
        return;
      }

      if (index === activeIndex && !isPlayerOpen) {
        const playPromise = video.play();
        if (playPromise && typeof playPromise.catch === 'function') {
          playPromise.catch(() => {});
        }
      } else {
        video.pause();
      }
    });
  }

  function pausePreviewVideos() {
    previewVideos.forEach((video) => video?.pause());
  }

  function resetPlayerVideo() {
    if (!playerVideo) {
      return;
    }

    playerVideo.pause();
    playerVideo.currentTime = 0;
    isPlayerPaused = true;
    playerCurrentTime = 0;
  }

  async function restartPlayerVideo() {
    await tick();

    if (!playerVideo) {
      return;
    }

    playerVideo.currentTime = 0;
    isPlayerPaused = true;
    playerCurrentTime = 0;

    if (openedFromGesture) {
      const playPromise = playerVideo.play();
      if (playPromise && typeof playPromise.catch === 'function') {
        playPromise.catch(() => {});
      }
      isPlayerPaused = false;
    }
  }

  async function openPlayer(project = activeProject) {
    if (!project) {
      return;
    }

    openedFromGesture = true;
    activeIndex = projects.findIndex((candidate) => candidate.slug === project.slug);
    openProjectSlug = project.slug;
    activeView = null;
    pausePreviewVideos();
    playerDuration = project.fullMedia.type === 'video' ? (project.fullMedia.duration ?? 0) : 0;
    writeUrl(null, project.slug);

    await tick();

    if (playerVideo) {
      playerVideo.currentTime = 0;
      playerVideo.muted = false;
      isPlayerPaused = false;
      isPlayerMuted = false;
      updatePlayerTiming();
      const playPromise = playerVideo.play();
      if (playPromise && typeof playPromise.catch === 'function') {
        playPromise.catch(() => {});
      }
    }
  }

  function closePlayer() {
    resetPlayerVideo();
    isPlayerPaused = true;
    isPlayerMuted = false;
    playerCurrentTime = 0;
    playerDuration = 0;
    activeView = null;
    openProjectSlug = null;
    openedFromGesture = false;
    writeUrl(null, null, 'replace');
    playActivePreview();
  }

  function openView(view: ProjectView) {
    if (!openProject) {
      return;
    }

    resetPlayerVideo();
    activeView = view;
    writeUrl(view, openProject.slug, 'push');
  }

  function returnToVideo() {
    activeView = null;
    writeUrl(null, openProject?.slug ?? null, 'replace');
    restartPlayerVideo();
  }

  function togglePlayerSound() {
    if (!playerVideo) {
      return;
    }

    isPlayerMuted = !isPlayerMuted;
    playerVideo.muted = isPlayerMuted;
  }

  function togglePlayerPlayback() {
    if (!playerVideo) {
      return;
    }

    if (playerVideo.paused || playerVideo.ended) {
      const playPromise = playerVideo.play();
      if (playPromise && typeof playPromise.catch === 'function') {
        playPromise
          .then(() => {
            isPlayerPaused = false;
          })
          .catch(() => {
            isPlayerPaused = true;
          });
      } else {
        isPlayerPaused = false;
      }
    } else {
      playerVideo.pause();
      isPlayerPaused = true;
    }
  }

  function requestPlayerFullscreen() {
    const fullscreenTarget = playerShell ?? playerVideo;

    if (!fullscreenTarget?.requestFullscreen) {
      return;
    }

    fullscreenTarget.requestFullscreen().catch(() => {});
  }

  function updatePlayerTiming() {
    if (!playerVideo) {
      return;
    }

    playerCurrentTime = Number.isFinite(playerVideo.currentTime) ? playerVideo.currentTime : 0;

    const fixedDuration =
      openProject?.fullMedia.type === 'video' ? openProject.fullMedia.duration : undefined;
    if (fixedDuration && Number.isFinite(fixedDuration)) {
      playerDuration = fixedDuration;
      return;
    }

    if (Number.isFinite(playerVideo.duration) && playerVideo.duration > playerCurrentTime + 0.25) {
      playerDuration = playerVideo.duration;
    }
  }

  function updatePlayerPlaybackState() {
    if (!playerVideo) {
      return;
    }

    isPlayerPaused = playerVideo.paused || playerVideo.ended;
  }

  function seekPlayer(event: Event) {
    if (!playerVideo || !(event.currentTarget instanceof HTMLInputElement)) {
      return;
    }

    const nextTime = Number(event.currentTarget.value);
    if (!Number.isFinite(nextTime)) {
      return;
    }

    const clampedTime =
      playerDisplayDuration > 0 ? Math.min(nextTime, playerDisplayDuration) : nextTime;

    playerVideo.currentTime = clampedTime;
    playerCurrentTime = clampedTime;
  }

  function formatPlayerTime(seconds: number) {
    if (!Number.isFinite(seconds) || seconds <= 0) {
      return '00:00';
    }

    const roundedSeconds = Math.floor(seconds);
    const minutes = Math.floor(roundedSeconds / 60);
    const remainingSeconds = roundedSeconds % 60;

    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds
      .toString()
      .padStart(2, '0')}`;
  }

  function handleWheel(event: WheelEvent) {
    if (isPlayerOpen || projects.length <= 1 || Math.abs(event.deltaY) < 22) {
      return;
    }

    const now = Date.now();
    if (now - lastWheelAt < 420) {
      return;
    }

    lastWheelAt = now;
    const direction = event.deltaY > 0 ? 1 : -1;
    selectProject((activeIndex + direction + projects.length) % projects.length);
  }

  function renderFallbackInfo(project: ExperienceProject) {
    return project.info.text.length > 0 ? project.info.text : [project.description];
  }

  function mediaClass(media: ProjectMedia, index: number) {
    return `media-card media-card--${media.layout ?? 'medium'} media-card--tilt-${(index % 5) + 1}`;
  }
</script>

<svelte:head>
  {#if isPlayerOpen}
    <meta name="theme-color" content="#050505" />
  {/if}
</svelte:head>

<section class:player-open={isPlayerOpen} class="experience" aria-label="Featured work">
  <button
    class="preview-open-target"
    type="button"
    aria-label={activeProject ? `Open ${activeProject.displayTitle}` : 'Open project'}
    on:click={() => openPlayer()}
  ></button>

  <div class="hero-media" aria-hidden="true">
    {#each projects as project, index}
      {#if project.previewMedia.type === 'video'}
        <video
          class:active={index === activeIndex}
          class="hero-video"
          src={project.previewMedia.src}
          poster={project.previewMedia.poster}
          muted
          loop
          playsinline
          preload={index === 0 ? 'auto' : 'metadata'}
          bind:this={previewVideos[index]}
        ></video>
      {:else}
        <img
          class:active={index === activeIndex}
          class="hero-video"
          src={project.previewMedia.src}
          alt=""
        />
      {/if}
    {/each}
    <div class="hero-overlay"></div>
  </div>

  <div class="hero-shell" on:wheel={handleWheel}>
    <div class="hero-title-stack" role="tablist" aria-label="Featured projects">
      {#each projects as project, index}
        <button
          class:active={index === activeIndex}
          class="hero-title-button"
          type="button"
          role="tab"
          aria-selected={index === activeIndex}
          on:mouseenter={() => selectProject(index)}
          on:focus={() => selectProject(index)}
          on:click={() => openPlayer(project)}
        >
          <span class="hero-title-name">{project.displayTitle}</span>
          <span class="hero-title-client">{project.client}</span>
        </button>
      {/each}
    </div>
  </div>

  {#if openProject}
    {#if activeView}
      <section
        class={`detail-page detail-page--${activeView}`}
        aria-label={`${viewLabels[activeView]} page for ${openProject.displayTitle}`}
      >
        <button class="detail-return" type="button" on:click={returnToVideo}>
          Return
        </button>

        <div class="detail-shell">
          <header class="detail-header">
            <p class="detail-kicker">{viewLabels[activeView]} / {openProject.client}</p>
            <h1>{openProject.displayTitle}</h1>
            <p>{openProject.category}</p>
          </header>

          {#if activeView === 'info'}
            <div class="detail-grid detail-grid--info">
              <div class="detail-copy">
                {#each renderFallbackInfo(openProject) as paragraph}
                  <p>{paragraph}</p>
                {/each}
              </div>

              <div class="detail-media">
                {#if openProject.info.media.length > 0}
                  {#each openProject.info.media as media, index}
                    <figure class={mediaClass(media, index)}>
                      {#if media.type === 'video'}
                        <video src={media.src} aria-label={media.alt} muted loop autoplay playsinline></video>
                      {:else}
                        <img src={media.src} alt={media.alt} loading="lazy" />
                      {/if}
                      {#if media.caption}
                        <figcaption>{media.caption}</figcaption>
                      {/if}
                    </figure>
                  {/each}
                {:else}
                  <p class="detail-empty">Info media can be added for this project.</p>
                {/if}
              </div>
            </div>
          {:else if activeView === 'bts'}
            <div class="detail-collage">
              {#if openProject.btsMedia.length > 0}
                {#each openProject.btsMedia as media, index}
                  <figure class={mediaClass(media, index)}>
                    {#if media.type === 'video'}
                      <video src={media.src} aria-label={media.alt} muted loop autoplay playsinline></video>
                    {:else}
                      <img src={media.src} alt={media.alt} loading="lazy" />
                    {/if}
                    {#if media.caption}
                      <figcaption>{media.caption}</figcaption>
                    {/if}
                  </figure>
                {/each}
              {:else}
                <p class="detail-empty">Behind the scenes media can be added for this project.</p>
              {/if}
            </div>
          {:else}
            <div class="detail-credits">
              {#if openProject.credits.length > 0}
                <div class="credits-grid">
                  {#each openProject.credits as credit}
                    <article class="credit-card">
                      <p>{credit.role}</p>
                      <h2>{credit.name}</h2>
                    </article>
                  {/each}
                </div>
              {:else}
                <p class="detail-empty">Credits can be added for this project.</p>
              {/if}
            </div>
          {/if}
        </div>
      </section>
    {:else}
      <div
        class="player-shell"
        aria-label={`${openProject.displayTitle} video player`}
        bind:this={playerShell}
      >
        {#if openProject.fullMedia.type === 'video'}
          <video
            class="player-video"
            src={openProject.fullMedia.src}
            poster={openProject.fullMedia.poster}
            playsinline
            preload="metadata"
            on:durationchange={updatePlayerTiming}
            on:loadedmetadata={updatePlayerTiming}
            on:timeupdate={updatePlayerTiming}
            on:play={updatePlayerPlaybackState}
            on:pause={updatePlayerPlaybackState}
            on:ended={updatePlayerPlaybackState}
            on:click={togglePlayerPlayback}
            bind:this={playerVideo}
          ></video>
        {:else}
          <img class="player-video" src={openProject.fullMedia.src} alt={openProject.displayTitle} />
        {/if}

        <div class="player-meta">
          <h2>{openProject.displayTitle}</h2>
          <p>{openProject.client}</p>
          {#if openProject.fullMedia.type === 'video'}
            <div class="player-progress-meta" aria-live="off">
              <span>{formatPlayerTime(playerCurrentTime)}</span>
              <span aria-hidden="true">/</span>
              <span>{formatPlayerTime(playerDisplayDuration)}</span>
            </div>
            <input
              class="player-progress"
              type="range"
              min="0"
              max={playerDisplayDuration || 0}
              step="0.01"
              value={playerCurrentTime}
              style={`--player-progress: ${playerProgressPercent}%`}
              aria-label={`Seek ${openProject.displayTitle}`}
              on:input={seekPlayer}
            />
          {/if}
        </div>

        {#if openProject.fullMedia.type === 'video'}
          <div class="player-controls" aria-label="Video controls">
            <button
              class="player-icon-button"
              type="button"
              aria-label={isPlayerPaused ? 'Play video' : 'Pause video'}
              on:click={togglePlayerPlayback}
            >
              {#if isPlayerPaused}
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8 5v14l11-7-11-7Z"></path>
                </svg>
              {:else}
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8 5v14"></path>
                  <path d="M16 5v14"></path>
                </svg>
              {/if}
            </button>
            <button
              class="player-icon-button"
              type="button"
              aria-label={isPlayerMuted ? 'Turn sound on' : 'Turn sound off'}
              on:click={togglePlayerSound}
            >
              {#if isPlayerMuted}
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M4 9v6h4l5 4V5L8 9H4Z"></path>
                  <path d="m18 9-5 5"></path>
                  <path d="m13 9 5 5"></path>
                </svg>
              {:else}
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M4 9v6h4l5 4V5L8 9H4Z"></path>
                  <path d="M16 8.5a5 5 0 0 1 0 7"></path>
                  <path d="M18.5 6a8.5 8.5 0 0 1 0 12"></path>
                </svg>
              {/if}
            </button>
            <button
              class="player-icon-button"
              type="button"
              aria-label="Enter fullscreen"
              on:click={requestPlayerFullscreen}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8 4H4v4"></path>
                <path d="M16 4h4v4"></path>
                <path d="M20 16v4h-4"></path>
                <path d="M4 16v4h4"></path>
              </svg>
            </button>
          </div>
        {/if}

        <button class="player-close" type="button" aria-label="Close video" on:click={closePlayer}>
          ×
        </button>
      </div>
    {/if}

    <nav
      class:detail-active={activeView !== null}
      class="project-nav"
      aria-label={`${openProject.displayTitle} project sections`}
    >
      {#each viewOrder as view}
        <button
          class:active={activeView === view}
          type="button"
          aria-current={activeView === view ? 'page' : undefined}
          on:click={() => openView(view)}
        >
          {viewLabels[view]}
        </button>
      {/each}
    </nav>
  {/if}
</section>

<style>
  :global(body.experience-open) {
    overflow: hidden;
  }

  .experience {
    position: relative;
    min-height: 100vh;
    min-height: 100svh;
    overflow: clip;
    background: #050505;
    color: #f7f1e8;
  }

  .preview-open-target,
  .hero-media,
  .hero-overlay {
    position: absolute;
    inset: 0;
  }

  .preview-open-target {
    z-index: 1;
    width: 100%;
    height: 100%;
    cursor: pointer;
  }

  .hero-video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transform: scale(1.06);
    filter: contrast(1.04) brightness(0.86);
    transition:
      opacity 0.9s var(--ease-smooth),
      transform 1.6s var(--ease-emphasis);
  }

  .hero-video.active {
    opacity: 1;
    transform: scale(1);
  }

  .hero-overlay {
    background:
      radial-gradient(circle at 70% 52%, rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.28) 42%, rgba(0, 0, 0, 0.62) 82%),
      linear-gradient(90deg, rgba(0, 0, 0, 0.58) 0%, rgba(0, 0, 0, 0.12) 42%, rgba(0, 0, 0, 0.46) 100%),
      linear-gradient(180deg, rgba(0, 0, 0, 0.24), rgba(0, 0, 0, 0.06) 48%, rgba(0, 0, 0, 0.42));
  }

  .hero-shell {
    position: relative;
    z-index: 3;
    min-height: 100vh;
    min-height: 100svh;
    display: flex;
    align-items: start;
    justify-content: flex-start;
    padding: clamp(7.4rem, 9vw, 9.2rem) clamp(1.35rem, 3.55vw, 4.25rem) clamp(2.2rem, 4.5vw, 4.2rem);
    transition:
      opacity 0.32s var(--ease-smooth),
      transform 0.42s var(--ease-emphasis);
  }

  .player-open .hero-shell {
    opacity: 0;
    pointer-events: none;
    transform: translateY(1rem);
  }

  .hero-title-stack {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: clamp(0.45rem, 1.3vw, 1.1rem);
    width: min(58vw, 58rem);
  }

  .hero-title-button {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: clamp(0.08rem, 0.45vw, 0.28rem);
    width: max-content;
    max-width: 100%;
    min-height: 54px;
    padding: 0;
    color: rgba(238, 234, 229, 0.53);
    text-align: left;
    transform-origin: left center;
    transition:
      color 0.32s var(--ease-smooth),
      opacity 0.32s var(--ease-smooth),
      transform 0.42s var(--ease-emphasis);
  }

  .hero-title-button:hover,
  .hero-title-button:focus-visible,
  .hero-title-button.active {
    opacity: 1;
    color: rgba(255, 251, 245, 0.98);
    transform: translateX(0.16rem);
  }

  .hero-title-name {
    max-width: 100%;
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 4.35vw, 5.2rem);
    font-weight: 500;
    letter-spacing: 0;
    line-height: 0.88;
    white-space: nowrap;
  }

  .hero-title-client {
    color: rgba(238, 234, 229, 0.44);
    font-size: clamp(0.78rem, 1vw, 0.95rem);
    font-weight: 600;
    letter-spacing: 0.08em;
    line-height: 1.1;
    text-transform: uppercase;
    transition: color 0.32s var(--ease-smooth);
  }

  .hero-title-button:hover .hero-title-client,
  .hero-title-button:focus-visible .hero-title-client,
  .hero-title-button.active .hero-title-client {
    color: rgba(255, 251, 245, 0.7);
  }

  .player-shell {
    position: fixed;
    inset: 0;
    z-index: 5000;
    background: #050505;
    color: #f7f1e8;
  }

  .player-video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: #050505;
  }

  .player-meta {
    position: fixed;
    left: clamp(1rem, 3.4vw, 3.2rem);
    bottom: calc(env(safe-area-inset-bottom, 0px) + clamp(1rem, 3vw, 2.65rem));
    z-index: 5015;
    width: min(34rem, calc(100vw - 2rem));
    color: rgba(255, 251, 245, 0.92);
  }

  .player-meta h2 {
    font-family: var(--font-display);
    font-size: clamp(1.7rem, 3.8vw, 4.4rem);
    font-weight: 500;
    letter-spacing: 0;
    line-height: 0.9;
  }

  .player-meta p {
    margin-top: 0.42rem;
    color: rgba(255, 251, 245, 0.58);
    font-size: clamp(0.74rem, 0.95vw, 0.9rem);
    font-weight: 600;
    letter-spacing: 0.08em;
    line-height: 1.2;
    text-transform: uppercase;
  }

  .player-progress-meta {
    display: flex;
    align-items: center;
    gap: 0.42rem;
    margin-top: 0.72rem;
    color: rgba(255, 251, 245, 0.62);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    line-height: 1;
  }

  .player-progress {
    --player-progress: 0%;
    appearance: none;
    width: 100%;
    height: 18px;
    margin-top: 0.42rem;
    padding: 0;
    cursor: pointer;
    background:
      linear-gradient(
        90deg,
        rgba(255, 251, 245, 0.84) 0%,
        rgba(255, 251, 245, 0.84) var(--player-progress),
        rgba(255, 251, 245, 0.22) var(--player-progress),
        rgba(255, 251, 245, 0.22) 100%
      );
    background-clip: content-box;
    border: 0;
    border-block: 8px solid transparent;
  }

  .player-progress::-webkit-slider-thumb {
    appearance: none;
    width: 0.42rem;
    height: 0.42rem;
    border-radius: 999px;
    background: rgba(255, 251, 245, 0.94);
  }

  .player-progress::-moz-range-thumb {
    width: 0.42rem;
    height: 0.42rem;
    border: 0;
    border-radius: 999px;
    background: rgba(255, 251, 245, 0.94);
  }

  .player-progress:focus-visible {
    outline: 1px solid rgba(255, 251, 245, 0.72);
    outline-offset: 0.25rem;
  }

  .player-controls {
    position: fixed;
    right: clamp(1rem, 3.4vw, 3.2rem);
    bottom: calc(env(safe-area-inset-bottom, 0px) + clamp(1rem, 3vw, 2.65rem));
    z-index: 5018;
    display: flex;
    align-items: center;
    gap: clamp(0.9rem, 1.7vw, 1.65rem);
  }

  .player-icon-button {
    width: 1.7rem;
    height: 1.7rem;
    display: grid;
    place-items: center;
    color: rgba(255, 251, 245, 0.72);
    transition:
      color 0.22s var(--ease-smooth),
      transform 0.22s var(--ease-emphasis);
  }

  .player-icon-button:hover,
  .player-icon-button:focus-visible {
    color: rgba(255, 251, 245, 0.98);
    transform: translateY(-1px);
  }

  .player-icon-button svg {
    width: 1rem;
    height: 1rem;
    fill: none;
    stroke: currentColor;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-width: 1.6;
    overflow: visible;
  }

  .player-close {
    position: fixed;
    top: calc(env(safe-area-inset-top, 0px) + clamp(1rem, 2.4vw, 1.8rem));
    right: clamp(1rem, 2.4vw, 1.8rem);
    z-index: 5020;
    width: 2.25rem;
    height: 2.25rem;
    display: grid;
    place-items: center;
    color: rgba(255, 251, 245, 0.68);
    font-size: 1.65rem;
    line-height: 1;
    transition: color 0.22s var(--ease-smooth);
  }

  .detail-return {
    position: fixed;
    top: calc(env(safe-area-inset-top, 0px) + clamp(1rem, 2.4vw, 1.8rem));
    right: clamp(1rem, 2.4vw, 1.8rem);
    z-index: 5020;
    min-height: 2.75rem;
    padding: 0 1.05rem;
    color: rgba(255, 251, 245, 0.94);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    background: rgba(0, 0, 0, 0.32);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 999px;
    backdrop-filter: blur(18px);
  }

  .player-close:hover,
  .player-close:focus-visible {
    color: rgba(255, 251, 245, 0.98);
  }

  .detail-return:hover,
  .detail-return:focus-visible {
    background: rgba(255, 255, 255, 0.14);
  }

  .project-nav {
    position: fixed;
    z-index: 5015;
    top: calc(env(safe-area-inset-top, 0px) + clamp(1rem, 2.4vw, 1.8rem));
    left: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: clamp(1.1rem, 2vw, 2.1rem);
    max-width: calc(100% - 10rem);
    padding: 0;
    transform: translateX(-50%);
  }

  .project-nav.detail-active {
    color: rgba(255, 251, 245, 0.96);
  }

  .project-nav button {
    position: relative;
    min-height: 2rem;
    padding: 0 0 0.28rem;
    color: rgba(255, 251, 245, 0.64);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    transition:
      color 0.22s var(--ease-smooth),
      transform 0.22s var(--ease-emphasis);
  }

  .project-nav button::after {
    content: '';
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    height: 1px;
    background: currentColor;
    transform: scaleX(0);
    transform-origin: left center;
    transition: transform 0.22s var(--ease-emphasis);
  }

  .project-nav button:hover,
  .project-nav button:focus-visible,
  .project-nav button.active {
    color: #fffaf2;
    transform: translateY(-1px);
  }

  .project-nav button:hover::after,
  .project-nav button:focus-visible::after,
  .project-nav button.active::after {
    transform: scaleX(1);
  }

  .detail-page {
    position: fixed;
    inset: 0;
    z-index: 5000;
    overflow-y: auto;
    background:
      linear-gradient(90deg, rgba(255, 251, 245, 0.035) 1px, transparent 1px),
      linear-gradient(180deg, rgba(255, 251, 245, 0.028) 1px, transparent 1px),
      linear-gradient(135deg, #0a0908 0%, #11100d 46%, #050505 100%);
    background-size: 18rem 18rem, 18rem 18rem, auto;
    color: #f7f1e8;
    overscroll-behavior: contain;
  }

  .detail-shell {
    position: relative;
    z-index: 1;
    min-height: 100vh;
    min-height: 100svh;
    padding:
      calc(env(safe-area-inset-top, 0px) + clamp(7rem, 11vw, 10rem))
      clamp(1.35rem, 4vw, 4.5rem)
      clamp(2.4rem, 5vw, 5rem);
    animation: state-in 0.32s var(--ease-emphasis);
  }

  .detail-header {
    max-width: min(72rem, 86vw);
    margin-bottom: clamp(1.8rem, 4vw, 4rem);
  }

  .detail-kicker,
  .credit-card p,
  .detail-empty {
    color: rgba(255, 251, 245, 0.64);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }

  .detail-header h1 {
    max-width: 11ch;
    margin: 0.65rem 0 0.9rem;
    font-family: var(--font-body);
    font-size: clamp(3.4rem, 9vw, 9.5rem);
    font-weight: 800;
    letter-spacing: -0.06em;
    line-height: 0.82;
    overflow-wrap: anywhere;
  }

  .detail-header p:last-child {
    color: rgba(255, 251, 245, 0.68);
    font-size: clamp(0.92rem, 1.2vw, 1.05rem);
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .detail-grid--info {
    display: grid;
    grid-template-columns: minmax(19rem, 0.82fr) minmax(0, 1.18fr);
    gap: clamp(1.2rem, 3vw, 3rem);
    height: min(58rem, calc(100svh - clamp(17rem, 23vw, 22rem)));
    min-height: 27rem;
  }

  .detail-copy,
  .detail-media {
    min-height: 0;
    overflow-y: auto;
    overscroll-behavior: contain;
    scrollbar-width: thin;
  }

  .detail-copy {
    padding: clamp(1rem, 2.4vw, 2rem) clamp(1rem, 2vw, 1.6rem) clamp(1.4rem, 3vw, 2.4rem) 0;
    border-top: 1px solid rgba(255, 255, 255, 0.24);
  }

  .detail-copy p {
    max-width: 45rem;
    color: rgba(255, 251, 245, 0.82);
    font-size: clamp(1rem, 1.35vw, 1.18rem);
    line-height: 1.72;
  }

  .detail-copy p + p {
    margin-top: 1.2rem;
  }

  .detail-media,
  .detail-collage {
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    align-content: start;
    gap: clamp(0.75rem, 1.4vw, 1.25rem);
    padding-bottom: 1rem;
  }

  .detail-collage {
    max-width: 92rem;
    margin-inline: auto;
  }

  .media-card {
    grid-column: span 4;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.16);
    background: rgba(255, 251, 245, 0.07);
    box-shadow: 0 22px 54px rgba(0, 0, 0, 0.26);
  }

  .media-card--small {
    grid-column: span 3;
  }

  .media-card--large {
    grid-column: span 5;
  }

  .media-card--wide {
    grid-column: span 7;
  }

  .detail-media .media-card--wide {
    grid-column: span 12;
  }

  .detail-collage .media-card--tilt-1 {
    transform: translateY(0.6rem) rotate(-1.4deg);
  }

  .detail-collage .media-card--tilt-2 {
    transform: rotate(1.1deg);
  }

  .detail-collage .media-card--tilt-3 {
    transform: translateY(1.1rem) rotate(0.8deg);
  }

  .detail-collage .media-card--tilt-4 {
    transform: translateY(-0.2rem) rotate(-0.8deg);
  }

  .detail-collage .media-card--tilt-5 {
    transform: translateY(0.4rem) rotate(1.6deg);
  }

  .media-card img,
  .media-card video {
    width: 100%;
    aspect-ratio: 4 / 3;
    object-fit: cover;
  }

  .media-card--wide img,
  .media-card--wide video {
    aspect-ratio: 16 / 9;
  }

  .media-card figcaption {
    padding: 0.75rem 0.85rem 0.85rem;
    color: rgba(255, 251, 245, 0.66);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .detail-credits {
    max-width: 72rem;
  }

  .credits-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(0.75rem, 1.4vw, 1rem);
  }

  .credit-card {
    min-width: 0;
    padding: clamp(1rem, 2vw, 1.5rem);
    border: 1px solid rgba(255, 255, 255, 0.16);
    background: rgba(255, 251, 245, 0.06);
  }

  .credit-card h2 {
    margin-top: 0.4rem;
    color: #fffaf2;
    font-size: clamp(1.25rem, 2vw, 2rem);
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1;
    overflow-wrap: anywhere;
  }

  .detail-empty {
    grid-column: 1 / -1;
    padding: clamp(1rem, 2vw, 1.5rem) 0;
    color: rgba(255, 251, 245, 0.58);
  }

  @keyframes state-in {
    from {
      transform: translateY(0.9rem);
    }

    to {
      transform: translateY(0);
    }
  }

  @media (max-width: 960px) {
    .hero-shell {
      padding-top: 7.6rem;
    }

    .hero-title-stack {
      width: min(72vw, 34rem);
    }

    .hero-title-button {
      white-space: normal;
    }

    .hero-title-name {
      font-size: clamp(2rem, 7.2vw, 3.8rem);
      white-space: normal;
    }

    .detail-shell {
      padding-top: calc(env(safe-area-inset-top, 0px) + 7.5rem);
    }

    .detail-header {
      max-width: none;
      margin-bottom: 1.5rem;
    }

    .detail-header h1 {
      font-size: clamp(2.8rem, 12vw, 6rem);
    }

    .detail-grid--info {
      display: block;
      height: auto;
      min-height: 0;
    }

    .detail-copy,
    .detail-media {
      overflow: visible;
      max-height: none;
    }

    .detail-media,
    .detail-collage {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      padding-top: 1rem;
    }

    .media-card,
    .media-card--small,
    .media-card--large,
    .media-card--wide {
      grid-column: span 1;
      transform: none !important;
    }

    .media-card--wide {
      grid-column: span 2;
    }

    .credits-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 700px) {
    .hero-shell {
      padding: 8.4rem 1rem 2.4rem;
    }

    .hero-title-stack {
      width: min(100%, 22rem);
    }

    .hero-title-button {
      min-height: 48px;
    }

    .hero-title-name {
      font-size: clamp(1.95rem, 9.5vw, 3.2rem);
      line-height: 0.92;
    }

    .hero-title-client {
      font-size: 0.7rem;
    }

    .project-nav {
      top: calc(env(safe-area-inset-top, 0px) + 0.7rem);
      max-width: calc(100% - 8.5rem);
      gap: 0.8rem;
    }

    .project-nav button {
      min-height: 1.85rem;
      padding-bottom: 0.24rem;
      font-size: 0.66rem;
      letter-spacing: 0.1em;
    }

    .player-close {
      top: calc(env(safe-area-inset-top, 0px) + 0.7rem);
      right: 0.75rem;
      width: 2.45rem;
      height: 2.45rem;
      font-size: 1.75rem;
    }

    .player-meta {
      left: 1rem;
      right: 1rem;
      bottom: calc(env(safe-area-inset-bottom, 0px) + 4.4rem);
      width: auto;
    }

    .player-controls {
      right: 1rem;
      bottom: calc(env(safe-area-inset-bottom, 0px) + 1rem);
      left: 1rem;
      justify-content: flex-end;
    }

    .detail-return {
      top: calc(env(safe-area-inset-top, 0px) + 0.7rem);
      right: 0.75rem;
      min-height: 2.45rem;
      padding: 0 0.78rem;
      font-size: 0.66rem;
      letter-spacing: 0.1em;
    }

    .detail-shell {
      padding-top: calc(env(safe-area-inset-top, 0px) + 6.9rem);
      padding-inline: 1rem;
    }

    .detail-media,
    .detail-collage,
    .credits-grid {
      grid-template-columns: 1fr;
    }

    .media-card,
    .media-card--small,
    .media-card--large,
    .media-card--wide {
      grid-column: span 1;
    }
  }

  @media (max-width: 420px) {
    .detail-return {
      top: calc(env(safe-area-inset-top, 0px) + 3.8rem);
    }

    .detail-shell {
      padding-top: calc(env(safe-area-inset-top, 0px) + 8.7rem);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .hero-video,
    .hero-shell,
    .hero-title-button,
    .project-nav button,
    .detail-shell {
      transition-duration: 0.01ms;
    }

    .detail-shell {
      animation: none;
    }
  }
</style>
