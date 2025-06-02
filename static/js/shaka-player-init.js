document.addEventListener('DOMContentLoaded', async function () {
  const video = document.getElementById('video-player');

  if (!shaka.Player.isBrowserSupported()) {
    console.error('Browser not supported!');
    return;
  }

  const player = new shaka.Player(video);

  // Listen for errors
  player.addEventListener('error', e => console.error('Shaka error', e.detail));

  try {
    await player.load(window.MASTER_PLAYLIST_URL);
  } catch (e) {
    console.error('Error loading video', e);
  }

  // Add subtitles
  if (Array.isArray(window.SUBTITLES)) {
    window.SUBTITLES.forEach(sub => {
      player.addTextTrack(sub.url, sub.label, sub.lang, 'subtitles');
    });
  }

  // Optionally enable subtitles by default
  const tracks = player.getTextTracks();
  if (tracks.length > 0) {
    player.selectTextTrack(tracks[0]);
    player.setTextTrackVisibility(true);
  }
});
